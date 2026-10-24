#!/usr/bin/env python3
"""Compile BugBank Markdown entries into bugbank.sqlite.

Usage:  python3 scripts/build_db.py   (from the repo root; needs pyyaml)
        python3 scripts/build_db.py --output releases/new-snapshot.sqlite

Validates frontmatter against the schema in SCHEMA.md and fails loudly on
violations. Rebuilds the database from scratch on every run.
"""
import argparse
import re
import sqlite3
import sys
from pathlib import Path

import yaml

try:
    from . import active_release
except ImportError:  # direct script invocation
    import active_release

ROOT = Path(__file__).resolve().parent.parent
DB = ROOT / "bugbank.sqlite"

TYPES = {"counterexample", "example", "pathology", "sharpness"}
STATUSES = {"seeded", "verified", "draft"}
REQUIRED = ["id", "title", "type", "domain", "subdomain", "tags",
            "statement", "difficulty", "status"]
SLUG = re.compile(r"^[a-z0-9][a-z0-9-]*$")

DDL = """
CREATE TABLE entries (
  id TEXT PRIMARY KEY, title TEXT NOT NULL,
  type TEXT NOT NULL CHECK (type IN ('counterexample','example','pathology','sharpness')),
  domain TEXT NOT NULL, subdomain TEXT NOT NULL,
  refutes TEXT, statement TEXT NOT NULL, true_theorem TEXT, hypothesis_violated TEXT,
  source_book TEXT, source_chapter TEXT, source_item TEXT, source_pages TEXT,
  difficulty INTEGER NOT NULL CHECK (difficulty BETWEEN 1 AND 5),
  status TEXT NOT NULL CHECK (status IN ('seeded','verified','draft')),
  body_md TEXT NOT NULL, path TEXT NOT NULL
);
CREATE TABLE tags (entry_id TEXT REFERENCES entries(id), tag TEXT,
                   PRIMARY KEY (entry_id, tag));
CREATE TABLE relations (entry_id TEXT REFERENCES entries(id), related_id TEXT,
                        PRIMARY KEY (entry_id, related_id));
CREATE TABLE sources (id TEXT PRIMARY KEY, citation TEXT NOT NULL);
CREATE VIRTUAL TABLE entries_fts USING fts5(
  id, title, refutes, statement, true_theorem, body_md, tags);
"""


def fail(path, msg):
    sys.exit(f"SCHEMA ERROR in {path}: {msg}")


def parse_entry(path: Path):
    text = path.read_text(encoding="utf-8")
    m = re.match(r"\A---\n(.*?)\n---\n(.*)\Z", text, re.DOTALL)
    if not m:
        fail(path, "missing YAML frontmatter block")
    try:
        meta = yaml.safe_load(m.group(1))
    except yaml.YAMLError as e:
        fail(path, f"YAML parse error: {e}")
    body = m.group(2).strip()

    for field in REQUIRED:
        if meta.get(field) in (None, "", []):
            fail(path, f"missing required field '{field}'")
    if meta["id"] != path.stem:
        fail(path, f"id '{meta['id']}' does not match filename '{path.stem}'")
    if not SLUG.match(meta["id"]):
        fail(path, f"id '{meta['id']}' is not a valid slug")
    if meta["type"] not in TYPES:
        fail(path, f"bad type '{meta['type']}'")
    if meta["status"] not in STATUSES:
        fail(path, f"bad status '{meta['status']}'")
    if not isinstance(meta["difficulty"], int) or not 1 <= meta["difficulty"] <= 5:
        fail(path, f"difficulty must be int 1-5, got {meta['difficulty']!r}")
    if meta["type"] in ("counterexample", "sharpness") and not meta.get("refutes"):
        fail(path, f"type '{meta['type']}' requires a 'refutes' field")
    if not isinstance(meta["tags"], list):
        fail(path, "'tags' must be a list")
    meta["body"] = body
    meta["path"] = str(path.relative_to(ROOT))
    return meta


def main(output=None):
    database = Path(output).resolve() if output is not None else (active_release.database_path(ROOT) if (ROOT / active_release.NAME).exists() else DB)
    entries = active_release.prune_relations(
        [parse_entry(p) for p in active_release.active_paths(ROOT)], active_release.load(ROOT))
    ids = [e["id"] for e in entries]
    if len(ids) != len(set(ids)):
        dupes = {i for i in ids if ids.count(i) > 1}
        sys.exit(f"SCHEMA ERROR: duplicate ids: {dupes}")
    idset = set(ids)

    sources = yaml.safe_load((ROOT / "sources.yaml").read_text(encoding="utf-8")) or {}

    for e in entries:
        for r in e.get("related") or []:
            if r not in idset:
                fail(e["path"], f"related id '{r}' does not exist")
        book = (e.get("source") or {}).get("book")
        if book and book not in sources:
            fail(e["path"], f"source book '{book}' not in sources.yaml")

    database.parent.mkdir(parents=True, exist_ok=True)
    database.unlink(missing_ok=True)
    con = sqlite3.connect(database)
    con.executescript(DDL)
    con.executemany("INSERT INTO sources VALUES (?,?)",
                    [(k, v.strip()) for k, v in sources.items()])
    for e in entries:
        src = e.get("source") or {}
        con.execute(
            "INSERT INTO entries VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (e["id"], e["title"], e["type"], e["domain"], e["subdomain"],
             (e.get("refutes") or "").strip() or None,
             e["statement"].strip(),
             (e.get("true_theorem") or "").strip() or None,
             (e.get("hypothesis_violated") or "").strip() or None,
             src.get("book"), src.get("chapter"),
             str(src["item"]) if src.get("item") is not None else None,
             str(src["pages"]) if src.get("pages") is not None else None,
             e["difficulty"], e["status"], e["body"], e["path"]))
        con.executemany("INSERT INTO tags VALUES (?,?)",
                        [(e["id"], t) for t in e["tags"]])
        con.executemany("INSERT INTO relations VALUES (?,?)",
                        [(e["id"], r) for r in (e.get("related") or [])])
        con.execute(
            "INSERT INTO entries_fts (id,title,refutes,statement,true_theorem,body_md,tags)"
            " VALUES (?,?,?,?,?,?,?)",
            (e["id"], e["title"], e.get("refutes") or "", e["statement"],
             e.get("true_theorem") or "", e["body"], " ".join(e["tags"])))
    con.commit()
    n = con.execute("SELECT COUNT(*) FROM entries").fetchone()[0]
    con.close()
    print(f"OK: built {database} with {n} entries.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=None,
                        help="Build a separate snapshot without changing bugbank.sqlite.")
    main(parser.parse_args().output)
