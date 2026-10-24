#!/usr/bin/env python3
"""Validate the published index against a fresh build without changing any DB.

This check is standalone: external experiment evidence is not required.
Logical FTS rows are compared, not SQLite-version-dependent shadow storage.
"""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import sqlite3
import tempfile

if __package__:
    from . import build_db
else:
    import build_db

ROOT = Path(__file__).resolve().parent.parent
TABLES = ("entries", "tags", "relations", "sources", "entries_fts")


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def repository_path(root, value):
    if not isinstance(value, str) or not value or Path(value).is_absolute():
        raise ValueError("database path must be a nonempty relative repository path")
    relative = Path(value)
    if ".." in relative.parts:
        raise ValueError("database path must not contain parent traversal")
    resolved = (root / relative).resolve()
    if root.resolve() not in resolved.parents:
        raise ValueError("database path escapes the repository")
    return resolved


def logical_database(path):
    with sqlite3.connect(path.resolve().as_uri() + "?mode=ro", uri=True) as con:
        if con.execute("PRAGMA integrity_check").fetchall() != [("ok",)]:
            raise ValueError(f"database integrity check failed: {path}")
        if con.execute("PRAGMA foreign_key_check").fetchall():
            raise ValueError(f"database foreign-key check failed: {path}")
        result = {}
        for table in TABLES:
            schema = con.execute(f"PRAGMA table_info({table})").fetchall()
            if not schema:
                raise ValueError(f"missing logical table: {table}")
            rows = Counter(con.execute(f"SELECT * FROM {table}"))
            result[table] = (schema, rows)
        return result


def compare_databases(committed, rebuilt):
    left, right = logical_database(committed), logical_database(rebuilt)
    for table in TABLES:
        if left[table] != right[table]:
            raise ValueError(
                f"published database is stale: logical table {table} differs; "
                "build a new release and update the CI manifest pointer"
            )


def check_release(manifest_path):
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    records = [("current", {
        "path": manifest["database"],
        "sha256": manifest["database_sha256"],
        "entry_count": manifest["entry_count"],
    })]
    records.extend((name, manifest[name]) for name in ("frozen_database", "previous_release"))
    records.extend((f"retained_release_{index}", record)
                   for index, record in enumerate(manifest.get("retained_releases", [])))
    snapshots = []
    for name, record in records:
        path = repository_path(ROOT, record["path"])
        expected = record["sha256"]
        if (not isinstance(expected, str) or len(expected) != 64 or
                any(c not in "0123456789abcdef" for c in expected)):
            raise ValueError(f"invalid SHA-256 for {name}")
        count = record["entry_count"]
        if type(count) is not int or count < 0:
            raise ValueError(f"invalid entry count for {name}")
        if sha256(path) != expected:
            raise ValueError(f"{name} database hash does not match manifest")
        content = logical_database(path)
        if sum(content["entries"][1].values()) != count:
            raise ValueError(f"{name} database entry count does not match manifest")
        snapshots.append((path, expected))

    # Retained release metadata also hashes historical documentation and external
    # evidence. Those are not freshness inputs here: all canonical cards/sources
    # are validated by the real builder, and all logical DB rows must agree.
    try:
        with tempfile.TemporaryDirectory(prefix="bugbank-ci-") as directory:
            rebuilt = Path(directory) / "rebuilt.sqlite"
            build_db.main(rebuilt)
            compare_databases(snapshots[0][0], rebuilt)
    finally:
        for path, expected in snapshots:
            if sha256(path) != expected:
                raise ValueError(f"validation changed a retained database: {path}")
    return {"result": "PASS", "database": manifest["database"],
            "entry_count": manifest["entry_count"], "logical_tables": list(TABLES),
            "retained_databases_unchanged": len(snapshots)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True,
                        help="Manifest selecting the current published release.")
    args = parser.parse_args()
    try:
        result = check_release(args.manifest)
    except (ValueError, KeyError, OSError, sqlite3.Error) as error:
        parser.exit(1, f"Release validation failed: {error}\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
