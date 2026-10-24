#!/usr/bin/env python3
"""Reproduce published interval/sensitivity tables from saved labels and usage. Requires NumPy."""
from pathlib import Path
import json,hashlib,random
import numpy as np
HERE=Path(__file__).resolve().parent
RUN=HERE/'reproduction'
TELEMETRY=HERE/'original/telemetry.jsonl'
PINS={}
ARMS=['refute','verify_earlystop_witness']
CAUGHT=('CAUGHT_MATCHING','CAUGHT_DIFFERENT')
GRADES=['CAUGHT_MATCHING','CAUGHT_DIFFERENT','FALSE_CATCH','MISSED']
SEED,B=20260917,20000
def read_bytes(path):
    path = Path(path)
    data = path.read_bytes()
    PINS[str(path)] = hashlib.sha256(data).hexdigest()
    return data

def read_json(path):
    return json.loads(read_bytes(path))

def read_text(path):
    return read_bytes(path).decode()

def cell_name(rid, arm):
    return rid.replace(' ', '_') + '__' + arm + '.json'

def load_usage(model, ids):
    out = {}
    if model == 'opus_task1':
        for line in read_text(TELEMETRY).splitlines():
            r = json.loads(line)
            if r['arm'] in ARMS:
                out[r['record_id'], r['arm']] = {'output': r['output'], 'uncached': r['input_uncached'], 'cache': r['input_cache_read'],
                                                 'api_calls': r.get('api_calls'), 'extra_exec': None, 'attempt': None}
    else:
        for rid in ids:
            for arm in ARMS:
                u = read_json(RUN / 'usage/proofs100' / model / cell_name(rid, arm))
                us = u['usage']
                assert u['record_id'] == rid and u['arm'] == arm
                if us['engine'] == 'agy':
                    t = us['usage']
                    rec = {'output': us['output_tokens_bound_model'], 'uncached': int(t['input_tokens']),
                           'cache': int(t.get('cache_read_tokens', 0)), 'api_calls': len(us.get('usage_steps') or [])}
                elif us['engine'] == 'codex':
                    t = us['usage_total']
                    rec = {'output': us['output_tokens_bound_model'], 'uncached': int(t['input_tokens']) - int(t.get('cached_input_tokens', 0)),
                           'cache': int(t.get('cached_input_tokens', 0)), 'api_calls': len(us.get('turns') or [])}
                else:
                    raise SystemExit('unexpected engine ' + str(us['engine']))
                rec['extra_exec'] = int(us.get('extra_exec_count', 0) or 0)
                rec['attempt'] = u.get('attempt')
                out[rid, arm] = rec
    for rid in ids:
        for arm in ARMS:
            assert (rid, arm) in out, (model, rid, arm)
            assert all(isinstance(out[rid, arm][k], int) and out[rid, arm][k] >= 0 for k in ['output', 'uncached', 'cache']), (model, rid, arm)
    return out

def load_grades(model, dataset, ids):
    g = {}
    for rid in ids:
        for arm in ARMS:
            d = read_json(RUN / 'grades' / dataset / model / cell_name(rid, arm))
            assert d['record_id'] == rid and d['arm'] == arm
            g[rid, arm] = d['grade']
    return g

def boot_index(n):
    return np.random.default_rng(SEED).integers(0, n, size=(B, n))

def ratio_ci(a, b, ix):
    return np.quantile(a[ix].sum(1) / b[ix].sum(1), [.025, .975]).tolist()

def block(model, U, G, ids):
    """Paired statistics on the task list `ids` for one model. Same estimator and bootstrap as the paper."""
    n = len(ids)
    ix = boot_index(n)
    a = np.array([G[r, ARMS[0]] in CAUGHT for r in ids], int)
    b = np.array([G[r, ARMS[1]] in CAUGHT for r in ids], int)
    d = a - b
    res = {'model': model, 'n': n, 'search_catches': int(a.sum()), 'witness_review_catches': int(b.sum()),
           'both': int(((a == 1) & (b == 1)).sum()), 'search_only': int((d == 1).sum()), 'review_only': int((d == -1).sum()),
           'neither': int(((a == 0) & (b == 0)).sum()),
           'paired_difference': float(d.mean()), 'paired_difference_ci95': np.quantile(d[ix].mean(1), [.025, .975]).tolist()}
    vec = {}
    for key in ['output', 'uncached', 'cache']:
        vec[key] = [np.array([U[r, arm][key] for r in ids], float) for arm in ARMS]
    vec['input_only'] = [vec['uncached'][i] + vec['cache'][i] for i in range(2)]
    vec['full_tokens'] = [vec['output'][i] + vec['input_only'][i] for i in range(2)]
    for name in ['output', 'full_tokens', 'input_only']:
        v = vec[name]
        res[name + '_ratio'] = float(v[0].sum() / v[1].sum())
        res[name + '_ratio_ci95'] = ratio_ci(v[0], v[1], ix)
    res['token_components'] = {arm: {'output': int(vec['output'][i].sum()), 'input_uncached': int(vec['uncached'][i].sum()),
                                     'input_cache_read': int(vec['cache'][i].sum()), 'full_tokens': int(vec['full_tokens'][i].sum())}
                               for i, arm in enumerate(ARMS)}
    for arm in ARMS:
        other = [G[r, arm] for r in ids if G[r, arm] not in GRADES]
        assert not other, (model, arm, other)
    res['grade_counts'] = {arm: {g: int(sum(1 for r in ids if G[r, arm] == g)) for g in GRADES} for arm in ARMS}
    return res
def full(r, which='bound'):
    p=r[which]
    return sum(p.values()) if p is not None else None

def compare(records, ids, arm):
    ids=sorted(ids)
    pairs=[(records[r,'refute'],records[r,arm]) for r in ids]
    assert all(a['bound'] is not None and b['bound'] is not None for a,b in pairs)
    av=[full(a) for a,b in pairs]; bv=[full(b) for a,b in pairs]
    all_available=all(full(a,'all_reported_models') is not None and full(b,'all_reported_models') is not None for a,b in pairs)
    aa=[full(a,'all_reported_models') for a,b in pairs] if all_available else []
    bb=[full(b,'all_reported_models') for a,b in pairs] if all_available else []
    rng=random.Random(SEED); vals=[]; all_vals=[]
    for _ in range(RESAMPLES):
        indices=[rng.randrange(len(ids)) for _ in ids]
        vals.append(sum(av[i] for i in indices)/sum(bv[i] for i in indices))
        if all_available: all_vals.append(sum(aa[i] for i in indices)/sum(bb[i] for i in indices))
    vals.sort(); all_vals.sort()
    all_model_available=all(full(a,'all_reported_models') is not None and full(b,'all_reported_models') is not None for a,b in pairs)
    return {'n_pairs':len(ids),'record_ids':ids,'search_full_tokens':sum(av),'comparator_full_tokens':sum(bv),
            'full_token_ratio':sum(av)/sum(bv),'full_token_ci95':[vals[500],vals[19499]],
            'all_reported_model_full_token_ci95':[all_vals[500],all_vals[19499]] if all_available else None,
            'output_ratio':sum(a['bound']['output'] for a,b in pairs)/sum(b['bound']['output'] for a,b in pairs),
            'all_reported_model_full_token_ratio':sum(full(a,'all_reported_models') for a,b in pairs)/sum(full(b,'all_reported_models') for a,b in pairs) if all_model_available else None}

def main():
    global SEED,RESAMPLES
    saved=read_json(HERE/'reference_validity/stratified_primary.json')
    checked=0
    for model,dataset in [('sol','proofs100'),('gemini','proofs100'),('opus_task1','proofs100_task1')]:
        ids=saved['tier_record_ids']['all100'];U=load_usage(model,ids);G=load_grades(model,dataset,ids)
        for tier,rows in saved['rows'].items():
            expected=next(x for x in rows if x['model']==model)
            got=block(model,U,G,saved['tier_record_ids'][tier])
            assert got==expected,(tier,model)
            checked+=1
    SEED,RESAMPLES=20260921,20000
    corrected=read_json(HERE/'corrected_claims60_accounting/RESULTS.json');claims_checked=0
    for model,d in corrected['models'].items():
        records={(r['record_id'],r['arm']):r for r in d['accepted_records']}
        for arm,expected in d['comparisons'].items():
            got=compare(records,expected['record_ids'],arm)
            assert all(got[k]==expected[k] for k in got),(model,arm)
            claims_checked+=1
        for label,expected in d['witness_sensitivity'].items():
            got=compare(records,expected['record_ids'],'prove_earlystop_witness')
            assert all(got[k]==expected[k] for k in got),(model,label)
            claims_checked+=1
    print(json.dumps({'status':'PASS','proof100_source_validity_rows':checked,'corrected_claim60_comparisons':claims_checked,'resamples_each':20000,'numpy_version':np.__version__,'source':'Original analysis arithmetic helpers, with path-neutral data loading; saved labels unchanged.'},indent=2))
if __name__=='__main__':main()
