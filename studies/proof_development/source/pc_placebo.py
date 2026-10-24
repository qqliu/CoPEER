#!/usr/bin/env python3
"""Placebo substitution for the placebo_parity arm.

Input: a hits file written by the frozen retriever ({claim_id: [record, ...]}).
Output: the same file rewritten in place, every record replaced by a BugBank
record chosen so that the packet keeps its shape and size but not its content:

  * candidates are all entries in the same sqlite database EXCEPT the real hits
    for this cell, the cell's own source item(s), and any entry whose domain
    equals the replaced record's domain (so the substitute is off-topic);
  * for each replaced record the substitute is the candidate whose rendered
    length (title + refutes + counterexample + true_theorem) is closest to the
    original's, ties broken by a seeded shuffle; a substitute is used at most
    once per cell;
  * the bm25 field is kept from the original record so the packet looks like an
    ordinary retrieval result.

The seed is per cell (driver: sha256(record_id) mod 2**31) and recorded. The
exact substitution (original entry_id -> substitute entry_id, lengths) is
written next to the hits file as <hits>.placebo_map.json for audit. Nothing is
printed to stdout except a one-line note, which the wrapper stores in its log.
"""
import argparse, json, random, sqlite3, pathlib, hashlib

# same database the frozen retriever reads (repo root / BugBank / bugbank.sqlite)
DB = pathlib.Path(__file__).resolve().parents[4] / "BugBank" / "bugbank.sqlite"
FIELDS = ("entry_id", "bm25", "title", "type", "domain", "refutes", "counterexample", "true_theorem",
          "source_book", "source_item", "status")


def rendered_len(rec):
    return sum(len(rec.get(k) or "") for k in ("title", "refutes", "counterexample", "true_theorem"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--hits", required=True)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--exclude-items", default="[]")
    a = ap.parse_args()
    hits = json.load(open(a.hits))
    real_ids = {r["entry_id"] for v in hits.values() for r in v}
    excl_items = set(json.loads(a.exclude_items))
    cx = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
    rows = cx.execute("SELECT id,title,type,domain,refutes,statement,true_theorem,source_book,source_item,status FROM entries").fetchall()
    pool = []
    for (eid, title, typ, domain, refutes, statement, true_theorem, book, item, status) in rows:
        if eid in real_ids or (item and item in excl_items):
            continue
        pool.append({"entry_id": eid, "title": title, "type": typ, "domain": domain, "refutes": refutes,
                     "counterexample": statement, "true_theorem": true_theorem, "source_book": book,
                     "source_item": item, "status": status})
    rng = random.Random(a.seed)
    used = set()
    mapping = []
    for cid, recs in hits.items():
        new = []
        for rec in recs:
            target = rendered_len(rec)
            cands = [p for p in pool if p["entry_id"] not in used and p.get("domain") != rec.get("domain")] or \
                    [p for p in pool if p["entry_id"] not in used]
            rng.shuffle(cands)
            best = min(cands, key=lambda p: abs(rendered_len(p) - target))
            used.add(best["entry_id"])
            sub = dict(best)
            sub["bm25"] = rec.get("bm25")
            new.append({k: sub.get(k) for k in FIELDS})
            mapping.append({"claim_id": cid, "original": rec["entry_id"], "original_len": target,
                            "substitute": best["entry_id"], "substitute_len": rendered_len(best),
                            "original_domain": rec.get("domain"), "substitute_domain": best.get("domain")})
        hits[cid] = new
    pathlib.Path(a.hits).write_text(json.dumps(hits, indent=1))
    pathlib.Path(a.hits + ".placebo_map.json").write_text(json.dumps(
        {"seed": a.seed, "db_sha256": hashlib.sha256(open(DB, "rb").read()).hexdigest(), "map": mapping}, indent=1))
    print(f"placebo: substituted {len(mapping)} records (seed {a.seed})")


if __name__ == "__main__":
    main()
