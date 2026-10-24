#!/usr/bin/env python3
"""Reproduce all five reported retrieval cohorts and deduplicated final endpoints."""
from pathlib import Path
from collections import Counter
import json
HERE=Path(__file__).resolve().parent

def summarize(rows):
    c=Counter(r['outcome'] for r in rows)
    return {'both_solved':c['BOTH_SOLVED'],'bugbank_only':c['BUGBANK_ONLY'],'plain_only':c['PLAIN_ONLY'],'neither_solved':c['NEITHER_SOLVED'],'bugbank_solved':c['BOTH_SOLVED']+c['BUGBANK_ONLY'],'plain_solved':c['BOTH_SOLVED']+c['PLAIN_ONLY']}

def check(d):
    assert summarize(d['records'])==d['outcomes']
    for arm in ['bugbank','plain']:
        assert sum(r['arms'][arm]['model_tokens_used'] for r in d['records'])==d['tokens'][arm+'_total']

p=json.loads((HERE/'results/paired_open_problem_results.json').read_text())
for cohort in p['protocols']:check(cohort)
final=p['distinct_target_final_endpoint_aggregate'];assert len(final['records'])==36 and summarize(final['records'])==final['outcomes']
stages=p['protocol_stage_observation_aggregate'];assert sum(len(x['records']) for x in p['protocols'])==58
reports={'distinct_targets':final['outcomes'],'protocol_stage_units':58}
for name in ['exploratory','targeted']:
    d=json.loads((HERE/'results'/f'paired_open_problem_{name}_results.json').read_text());check(d['cohort']);assert len(d['cohort']['records'])==6;reports[name]=d['cohort']['outcomes']
print(json.dumps({'status':'PASS',**reports,'endpoint':'run-local model-audited full target resolution','scope':'Five cohorts remain separate; continuation endpoints replace their original target endpoints.'},indent=2))
