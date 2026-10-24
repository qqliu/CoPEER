#!/usr/bin/env python3
"""Replay saved instruction-study counts, output ratios, and corrected full-token totals."""
from pathlib import Path
from collections import Counter
import json,random,math
HERE=Path(__file__).resolve().parent

def read(p):return json.loads(p.read_text())
def close(a,b):return abs(a-b)<1e-10

def native_output(p):
    u=read(p);return u['record_id'],u['arm'],u['usage'].get('output_tokens_bound_model')

def main():
    checked=0
    for p in sorted((HERE/'reproduction/summary').glob('*.json')):
        s=read(p);dataset,model=s['set'],s['model'];U={}
        if model=='opus_task1':
            for line in (HERE/'original/telemetry.jsonl').read_text().splitlines():
                r=json.loads(line);U[r['record_id'],r['arm']]=r['output']
            G={ (g['record_id'],g['arm']):g['grade'] for f in (HERE/'original/grades').glob('*.json') for g in [read(f)]}
        else:
            for f in (HERE/'reproduction/usage'/dataset/model).glob('*.json'):
                rid,arm,output=native_output(f);U[rid,arm]=output
            G={ (g['record_id'],g['arm']):g['grade'] for f in (HERE/'reproduction/grades'/dataset/model).glob('*.json') for g in [read(f)]}
        ids=read(HERE/'reproduction'/f'{dataset}_ids.json')
        for arm,v in s['arms'].items():
            outputs=[U[r,arm] for r in ids if type(U.get((r,arm))) is int and U[r,arm]>0]
            assert sum(outputs)==v['output_sum'],(p.name,arm,'output')
            assert Counter(G[r,arm] for r in ids if (r,arm) in G)==v['grades'],(p.name,arm,'grades')
        for contrast,v in s['paired'].items():
            arm=contrast.removeprefix('refute_vs_');pairs=[(U[r,'refute'],U[r,arm]) for r in sorted(ids) if type(U.get((r,'refute'))) is int and type(U.get((r,arm))) is int and U[r,'refute']>0 and U[r,arm]>0]
            assert len(pairs)==v['n_pairs']
            assert close(sum(a for a,b in pairs)/sum(b for a,b in pairs),v['output_ratio_of_sums'])
            rng=random.Random(20260819);boot=[]
            for _ in range(2000):
                draw=[pairs[rng.randrange(len(pairs))] for _ in pairs];boot.append(sum(a for a,b in draw)/sum(b for a,b in draw))
            boot.sort();assert all(close(a,b) for a,b in zip([boot[50],boot[1949]],v['output_ci95_record_bootstrap']))
        checked+=1
    # These corrected records supersede the older full-token accounting for claims60.
    corrected=read(HERE/'corrected_claims60_accounting/RESULTS.json')
    for model,d in corrected['models'].items():
        assert len(d['accepted_records'])==240
        for arm,saved in d['arms'].items():
            rows=[r for r in d['accepted_records'] if r['arm']==arm]
            for sourcekey,savedkey in [('bound','accepted_bound_model'),('all_reported_models','accepted_all_reported_models')]:
                got={key:sum(r[sourcekey][key] for r in rows) for key in ['input_uncached','input_cache_creation','input_cache_read','output']}
                assert all(got[k]==saved[savedkey][k] for k in got)
                assert sum(got.values())==saved[savedkey]['full_tokens']
            assert Counter(r['grade'] for r in rows)==saved['grade_counts']
        by={(r['record_id'],r['arm']):r for r in d['accepted_records']}
        for arm,v in d['comparisons'].items():
            ids=v['record_ids'];num=sum(sum(by[r,'refute']['bound'].values()) for r in ids);den=sum(sum(by[r,arm]['bound'].values()) for r in ids)
            assert close(num/den,v['full_token_ratio'])
    # References later invalidated: 13 tasks × two instructions × three models.
    validity=read(HERE/'reference_validity/stratified_primary.json');ids=validity['tier_record_ids']['invalidated13'];counts={}
    for model,dataset in [('sol','proofs100'),('gemini','proofs100'),('opus_task1','proofs100_task1')]:
        grades=[read(HERE/'reproduction/grades'/dataset/model/f'{r}__{a}.json')['grade'] for r in ids for a in ['refute','verify_earlystop_witness']]
        counts[model]=grades.count('CAUGHT_MATCHING')
    assert counts==validity['caught_matching_on_invalidated13_by_model'],counts
    assert sum(counts.values())==60
    print(json.dumps({'status':'PASS','saved_instruction_summaries':checked,'claims60_corrected_cells':720,'reference_invalidity_diagnostic':{'matching_grades':60,'model_outputs':78,'by_model':counts},'scope':'Saved labels and native accounting, with original output bootstrap intervals; no new judgments or model calls.'},indent=2))
if __name__=='__main__':main()
