#!/usr/bin/env python3
"""Reproduce proof-development table and usage from the saved selected attempts; no model calls."""
from pathlib import Path
import json,random
HERE=Path(__file__).resolve().parent
COMPONENTS=['input_uncached','cache_creation','cache_read','output']
def native_usage(raw):
    """Return disjoint components; no receipt or failed zero receipt is unknown."""
    engine = raw.get('engine')
    auxiliary = 0
    if engine == 'claude':
        models = raw.get('modelUsage') or {}
        if not models:
            return None
        parts = {'input_uncached': 0, 'cache_creation': 0, 'cache_read': 0, 'output': 0}
        reasoning = 0
        for model, u in models.items():
            v = dict(zip(COMPONENTS, [u.get('inputTokens', 0), u.get('cacheCreationInputTokens', 0),
                                     u.get('cacheReadInputTokens', 0), u.get('outputTokens', 0)]))
            if model != 'claude-opus-5':
                auxiliary += sum(v.values())
            for k in COMPONENTS:
                parts[k] += v[k]
            reasoning += u.get('thinkingTokens', 0)
    elif engine == 'codex':
        u = raw.get('usage_total') or {}
        if not all(k in u and u[k] is not None for k in ['input_tokens', 'output_tokens']):
            return None
        cached = u.get('cached_input_tokens') or 0
        parts = dict(zip(COMPONENTS, [u['input_tokens'] - cached, 0, cached, u['output_tokens']]))
        reasoning = u.get('reasoning_output_tokens')
    elif engine == 'agy':
        u = raw.get('usage') or {}
        if not all(k in u and u[k] is not None for k in ['input_tokens', 'output_tokens']):
            return None
        parts = dict(zip(COMPONENTS, [u['input_tokens'], 0, u.get('cache_read_tokens') or 0, u['output_tokens']]))
        reasoning = u.get('thinking_tokens')
    else:
        return None
    assert all(isinstance(v, int) and v >= 0 for v in parts.values()), parts
    total = sum(parts.values())
    if not total and raw.get('status', raw.get('exit_code')) != 0:
        return None
    return {**parts, 'total': total, 'reasoning_within_output': reasoning,
            'auxiliary_within_total': auxiliary}

def additional_attempt_costs(pd):
    """A rerun can reuse a path: failed telemetry rows still count as attempts."""
    chosen = {r['row']['attempt_dir'] for r in pd['endpoints']}
    failed = [x for x in pd['attempts'] if x['row']['status'] != 0]
    receipts = []
    primary_lower_bound = 0
    for x in failed:
        receipt = x['receipt']
        if x['row']['attempt_dir'] in chosen:
            receipt = {'tokens': None, 'reason': 'Native path overwritten by successful rerun'}
        receipts.append(receipt)
        if receipt['tokens'] is None:
            u = x['row']['usage']
            # Native helper details may be absent, but nonzero historical primary
            # telemetry is still a measured lower bound, never a reconstructed zero.
            primary_lower_bound += sum(u.get(k) or 0 for k in ['input_uncached', 'input_cache_read', 'output_tokens'])
    result = sum_usage(receipts)
    result['native_known_total'] = result['total']
    result['historical_primary_only_lower_bound'] = primary_lower_bound
    result['total'] += primary_lower_bound
    result['total_is_lower_bound'] = bool(result['unknown'])
    result['component_totals_cover_native_receipts_only'] = True
    return result

def sum_usage(receipts):
    known = [r['tokens'] for r in receipts if r['tokens'] is not None]
    return {**{k: sum(r[k] for r in known) for k in COMPONENTS + ['total', 'auxiliary_within_total']},
            'receipts': len(receipts), 'unknown': len(receipts) - len(known)}

def bootstrap(a, b):
    assert len(a) == len(b)
    if not a or not sum(b):
        return None
    rng = random.Random(20260916)
    n = len(a)
    draws = []
    for _ in range(2000):
        idx = [rng.randrange(n) for _ in range(n)]
        denominator = sum(b[i] for i in idx)
        if denominator:
            draws.append(sum(a[i] for i in idx) / denominator)
    draws.sort()
    return [sum(a)/sum(b), draws[int(.025*len(draws))], draws[int(.975*len(draws))-1]]

def main():
    data=json.loads((HERE/'snapshot.json').read_text())
    saved=json.loads((HERE/'studies50_results_20260917.json').read_text())
    supplement=json.loads((HERE/'proof50_grade_completion_20260917.json').read_text())
    assert supplement['base_snapshot_sha256']==saved['snapshot_sha256']
    for item in supplement['entries']:
        grade=item['grade']
        e=next(e for e in data['proof']['opus']['endpoints'] if e['row']['arm']==grade['arm_key'] and e['row']['record_id']==grade['record_id'])
        assert e['grade'] is None and e['draft_text_sha256']==grade['draft_sha256']
        e['grade']=grade
        raw={'engine':'codex','status':0,'usage_total':item['report']['usage']}
        data['proof']['opus']['grader_receipts'].append({'tokens':native_usage(raw)})
    rows=[];costs=[]
    for model,pd in data['proof'].items():
        E={(x['row']['record_id'],x['row']['arm']):x for x in pd['endpoints']}
        for protocol,a,b in [('shared','bugbank_parity','plain_parity'),('original','bugbank_orig','plain_orig')]:
            ids=sorted(data['proof_roster']);assert len(ids)==50
            graded=[r for r in ids if E[r,a]['grade'] and E[r,b]['grade']]
            row={'model':model,'protocol':protocol,'n_pairs':len(ids),'n_graded_pairs':len(graded)}
            for tag,arm in [('bugbank',a),('plain',b)]:
                selected=[E[r,arm] for r in ids]
                row[tag]={'correct':sum(E[r,arm]['grade']['correctness']=='CORRECT' for r in graded),'tokens':sum_usage([x['receipt'] for x in selected]),'primary_output':sum(x['row']['usage']['output_tokens'] for x in selected)}
            row['output_ratio']=bootstrap([E[r,a]['row']['usage']['output_tokens'] for r in ids],[E[r,b]['row']['usage']['output_tokens'] for r in ids])
            row['full_ratio']=bootstrap([E[r,a]['receipt']['tokens']['total'] for r in ids],[E[r,b]['receipt']['tokens']['total'] for r in ids])
            expected=next(x for x in saved['proof'] if x['model']==model and x['protocol']==protocol)
            assert row==expected,(model,protocol)
            rows.append(row)
        costs.extend([{'study':'proof','model':model,'category':'additional attempts',**additional_attempt_costs(pd)},{'study':'proof','model':model,'category':'grading',**sum_usage(pd['grader_receipts'])}])
    assert sorted(costs,key=lambda x:(x['model'],x['category']))==sorted(saved['costs'],key=lambda x:(x['model'],x['category']))
    print(json.dumps({'status':'PASS','pairs_per_row':50,'rows':len(rows),'selected_drafts':600,'reproduced':['correctness','token components','paired bootstrap intervals','additional attempt costs','grading costs']},indent=2))
if __name__=='__main__':main()
