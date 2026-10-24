#!/usr/bin/env python3
"""Mechanical BugBank retrieval: given claim text, return the most similar
known-false claims and their counterexamples.

This is the zero-token stage of the bugbank-check workflow (PI task 6): the
`refutes` field is BugBank's designed retrieval key ("you search for the
statement you suspect, not the object that kills it"), and SQLite FTS5 over
refutes/statement/tags/title is its only search machinery.  Retrieval must be
mechanical so that when the primed checker beats the from-scratch baseline,
the credit assignment is clean: the tokens saved were saved by a database
query, not by a second model call.

Leakage control: 604/661 BugBank entries derive from THIS pipeline's corpus.
Evaluating retrieval-primed checking on our own records would be
self-retrieval.  --exclude-self drops the qedbench-canonical-600 and
qedbench-pipeline source books; --exclude-items drops specific source record
ids (for held-out records that later entered BugBank).

Query construction: FTS5 MATCH with OR-of-salient-terms.  Raw math text is
full of FTS operators (^, *, quotes), so every term is quoted; terms are the
alphabetic words of the claim minus stopwords, weighted by rarity via a
document-frequency pass over the refutes column (computed once, cached).

Usage:
  python3 scripts/bugbank_retrieve.py --query "every eulerian graph is hamiltonian" -k 5
  python3 scripts/bugbank_retrieve.py --claims-json claims.json -k 5 --exclude-self
"""
import argparse
import json
import re
import sqlite3
import sys
from collections import Counter
from pathlib import Path

DB = Path(__file__).resolve().parent / "retrieval.sqlite"
SELF_BOOKS = ("qedbench-canonical-600", "qedbench-pipeline")
STOP = set("""a an and are as at be by for from has have if in into is it its of on
or that the their there these this to was we which will with not no nor so then
than let all any each every some such given hence thus where when suppose assume
proof claim show shows shown implies follows since because therefore step case
""".split())

WORD = re.compile(r"[a-zA-Z][a-zA-Z-]{2,}")


def salient_terms(text: str, df: Counter, n_docs: int, top: int = 12):
    words = [w.lower() for w in WORD.findall(text)]
    seen = {}
    for w in words:
        if w in STOP or len(w) < 3:
            continue
        # rarity-weighted: unseen-in-corpus words still score (they may match
        # statement/body even if absent from every refutes field)
        seen.setdefault(w, (n_docs + 1) / (df.get(w, 0) + 1))
    ranked = sorted(seen.items(), key=lambda kv: -kv[1])
    return [w for w, _ in ranked[:top]]


def build_df(cx) -> tuple[Counter, int]:
    df = Counter()
    rows = cx.execute("SELECT refutes FROM entries").fetchall()
    for (refutes,) in rows:
        for w in set(x.lower() for x in WORD.findall(refutes or "")):
            if w not in STOP:
                df[w] += 1
    return df, len(rows)


def retrieve(cx, claim: str, k: int, exclude_self: bool,
             exclude_items: set[str], df: Counter, n_docs: int):
    terms = salient_terms(claim, df, n_docs)
    if not terms:
        return []
    match = " OR ".join(f'"{t}"' for t in terms)
    sql = """
      SELECT f.id, bm25(entries_fts, 2.0, 8.0, 4.0, 1.0, 1.0, 3.0) AS score,
             e.title, e.type, e.domain, e.refutes, e.statement,
             e.true_theorem, e.source_book, e.source_item, e.status
      FROM entries_fts f JOIN entries e ON e.id = f.id
      WHERE entries_fts MATCH ?
    """
    params = [match]
    if exclude_self:
        sql += " AND e.source_book NOT IN (?, ?)"
        params += list(SELF_BOOKS)
    sql += " ORDER BY score LIMIT ?"
    params.append(k * 3)          # over-fetch; exclude_items filters after
    out = []
    for row in cx.execute(sql, params):
        (eid, score, title, typ, domain, refutes, statement,
         true_theorem, book, item, status) = row
        if item and item in exclude_items:
            continue
        out.append({
            "entry_id": eid, "bm25": round(score, 3), "title": title,
            "type": typ, "domain": domain, "refutes": refutes,
            "counterexample": statement, "true_theorem": true_theorem,
            "source_book": book, "source_item": item, "status": status,
        })
        if len(out) >= k:
            break
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--query")
    ap.add_argument("--claims-json", help="JSON list of claim strings, or list of {claim_id, claim}")
    ap.add_argument("-k", type=int, default=5)
    ap.add_argument("--exclude-self", action="store_true")
    ap.add_argument("--exclude-items-json", help="JSON list of source_item ids to drop")
    ap.add_argument("--out", help="write JSON here instead of stdout")
    a = ap.parse_args()
    if not DB.exists():
        raise SystemExit(f"BugBank db missing: {DB}")
    cx = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
    df, n_docs = build_df(cx)
    exclude_items = set(json.load(open(a.exclude_items_json))) if a.exclude_items_json else set()

    if a.query:
        claims = [{"claim_id": "q0", "claim": a.query}]
    elif a.claims_json:
        raw = json.load(open(a.claims_json))
        claims = [{"claim_id": f"q{i}", "claim": c} if isinstance(c, str) else c
                  for i, c in enumerate(raw)]
    else:
        raise SystemExit("need --query or --claims-json")

    result = {c["claim_id"]: retrieve(cx, c["claim"], a.k, a.exclude_self,
                                      exclude_items, df, n_docs)
              for c in claims}
    text = json.dumps(result, indent=1)
    if a.out:
        Path(a.out).write_text(text)
        print(f"wrote {a.out}: {sum(len(v) for v in result.values())} hits "
              f"for {len(result)} claims")
    else:
        print(text)


if __name__ == "__main__":
    main()
