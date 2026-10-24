#!/usr/bin/env python3
"""Recount the entire executable-twin study from its saved search/check results."""
from pathlib import Path
from collections import Counter
import json
p=Path(__file__).resolve().parent
ids=json.loads((p/'population_ids.json').read_text())
S=[json.loads((p/'searches'/f"{r.replace(' ', '_')}.json").read_text()) for r in ids]
assert len(ids)==len(set(ids))==len(S)==604
outcomes=Counter(r['outcome'] for r in S)
assert outcomes=={'WITNESS_FOUND':351,'NO_WITNESS_EXHAUSTIVE':12,'NO_WITNESS_INCONCLUSIVE':221,'CLAIM_NOT_FINITELY_REFUTABLE':20}
V=[json.loads((p/'verifies'/f"{r['record_id'].replace(' ', '_')}.json").read_text()) for r in S if r['outcome']=='WITNESS_FOUND']
verdicts=Counter(r['verdict'] for r in V)
assert verdicts=={'CONFIRMED':348,'REFUTED_WITNESS_INVALID':3}
print(json.dumps({'status':'PASS','tasks':604,'search_outcomes':outcomes,'checker_outcomes':verdicts,'scope':'Saved checker judgments; this replay does not execute generated witness programs.'},indent=2))
