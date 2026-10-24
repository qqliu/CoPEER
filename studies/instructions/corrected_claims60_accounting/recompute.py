#!/usr/bin/env python3
"""Offline correction of claims60 token accounting. Never calls models or rewrites historical inputs.

Run: python3 astra/writing_20260921/claims60_accounting/recompute.py
The resulting JSON pins every source read; --verify-pins RESULTS.json rejects drift.
"""
import argparse, collections, hashlib, json, random, re
from pathlib import Path

MODELS = ('sol', 'gemini', 'opus')
ARMS = ('refute', 'prove_full', 'prove_earlystop', 'prove_earlystop_witness')
COMPONENTS = ('input_uncached', 'input_cache_creation', 'input_cache_read', 'output')
SEED, RESAMPLES = 20260921, 20000
PINS = {}

def read(path):
    raw = path.read_bytes()
    PINS[str(path)] = hashlib.sha256(raw).hexdigest()
    return raw

def obj(path):
    return json.loads(read(path))

def valid(v):
    return type(v) is int and v >= 0

def parts(values):
    return dict(zip(COMPONENTS, values)) if all(valid(v) for v in values) else None

def plus(rows):
    known = [r for r in rows if r is not None]
    sums = {k: sum(r[k] for r in known) for k in COMPONENTS}
    return {**sums, 'known_full_tokens': sum(sums.values()), 'unknown_records': len(rows)-len(known),
            'full_tokens': sum(sums.values()) if len(known) == len(rows) else None}

def parse(u):
    engine = u.get('engine')
    o = u.get('output_tokens_bound_model')
    bound = None; auxiliary = None; all_reported = None; thinking = None
    if engine == 'codex':
        t = u.get('usage_total') or {}
        i, c = t.get('input_tokens'), t.get('cached_input_tokens')
        if valid(i) and valid(c) and i >= c:
            # Native input already includes cached reads. This roster has no cache-write tokens.
            assert t.get('cache_write_input_tokens', 0) == 0
            bound = parts((i-c, 0, c, o))
        thinking = t.get('reasoning_output_tokens')
        if bound is not None: assert o == t['output_tokens']
    elif engine == 'agy':
        t = u.get('usage') or {}
        # Gemini input_tokens is UNCACHED input; cache_read_tokens is additional.
        bound = parts((t.get('input_tokens'), 0, t.get('cache_read_tokens'), o))
        thinking = t.get('thinking_tokens')
        if bound is not None: assert o == t['output_tokens']
    elif engine == 'claude':
        bm = u.get('bound_model_usage') or {}
        if len(bm) == 1:
            name, t = next(iter(bm.items()))
            bound = parts(tuple(t.get(k) for k in ('inputTokens','cacheCreationInputTokens','cacheReadInputTokens','outputTokens')))
            thinking = t.get('thinkingTokens')
            if bound is not None: assert o == bound['output']
            mu = u.get('modelUsage')
            if isinstance(mu, dict) and name in mu:
                assert mu[name] == t
                others = [parts(tuple(v.get(k) for k in ('inputTokens','cacheCreationInputTokens','cacheReadInputTokens','outputTokens'))) for k,v in mu.items() if k != name]
                a = plus(others)
                auxiliary = {k:a[k] for k in COMPONENTS} if not a['unknown_records'] else None
                if bound is not None and auxiliary is not None:
                    all_reported = {k:bound[k]+auxiliary[k] for k in COMPONENTS}
    else:
        raise ValueError('Unexpected engine: '+str(engine))
    if engine in ('codex','agy'): all_reported = bound  # Only the native aggregate is reported; no auxiliary split.
    if bound is not None and valid(thinking): assert thinking <= bound['output']
    return {'engine':engine,'bound':bound,'auxiliary':auxiliary,'all_reported_models':all_reported,
            'reasoning_subset':thinking if valid(thinking) else None,
            'extra_exec':u.get('extra_exec_count') if valid(u.get('extra_exec_count')) else None}

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
    ap=argparse.ArgumentParser();ap.add_argument('--repo',type=Path,default=Path(__file__).resolve().parents[3]);ap.add_argument('--canonical',type=Path,default=Path('<workspace-home>/copeer_overleaf_6aab4fdd06028cb9e4ebe6d6'));ap.add_argument('--out',type=Path,default=Path(__file__).resolve().parent);ap.add_argument('--verify-pins',type=Path);args=ap.parse_args()
    # parents[3] is the research repository for astra/writing_DATE/claims60_accounting/script.py.
    repo=args.repo.resolve();run=repo/'qedbench_certificate_availability_triage/runs/cost_experiment_repro_20260915';out=args.out;out.mkdir(parents=True,exist_ok=True)
    manifest=obj(run/'manifest.json');ids=sorted(manifest['claims60']);assert len(ids)==60
    hint=set(manifest['claims60_hint_flagged_ids']);assert len(hint)==13 and hint<=set(ids)
    assert set(obj(run/'claims60_ids.json'))==set(ids)
    for rid in ids:
        for kind,key in [('inputs_claims60','input_sha256'),('grading_truth_claims60','truth_sha256')]:
            p=run/kind/(rid+'.json');read(p);assert PINS[str(p)]==manifest['claims60'][rid][key]
    results={}; macro_changes=[]
    for model in MODELS:
        summary=obj(run/f'summary/claims60_{model}.json');records={}
        ledger_path=run/f'ledger/claims60_{model}.jsonl';ledger=[json.loads(l) for l in read(ledger_path).decode().splitlines()]
        seen=set()
        for n,l in enumerate(ledger,1):
            key=(l['record_id'],l['arm'],l['attempt']);assert key not in seen;seen.add(key)
            assert l['record_id'] in ids and l['arm'] in ARMS and l['model']==model
        rejected=[];arm_results={}
        for rid in ids:
            for arm in ARMS:
                p=run/'usage/claims60'/model/f'{rid}__{arm}.json';wrapped=obj(p);assert wrapped['record_id']==rid and wrapped['arm']==arm
                u=wrapped['usage'];assert u['status']==0 and u['exit_code']==0
                r=parse(u);assert r['bound'] is not None
                matches=[(n,l) for n,l in enumerate(ledger,1) if l['record_id']==rid and l['arm']==arm and l['status'] in ('COMPLETE','COMPLETE_RECOVERED')]
                assert len(matches)==1
                n,l=matches[0];assert l['attempt']==wrapped['attempt'] and l['output_tokens']==r['bound']['output']
                native=Path(l['workdir'])/'usage.json';assert obj(native)==u
                r.update(record_id=rid,arm=arm,attempt=wrapped['attempt'],source_path=str(p),native_path=str(native),ledger_line=n)
                gp=run/'grades/claims60'/model/f'{rid}__{arm}.json';apath=run/'assessments/claims60'/model/f'{rid}__{arm}.json'
                g=obj(gp);assess=obj(apath)
                assert g['record_id']==assess['record_id']==rid and g['arm']==assess['arm']==arm
                r.update(grade=g['grade'],verdict=assess['verdict'],grade_path=str(gp),assessment_path=str(apath))
                records[rid,arm]=r
        for n,l in enumerate(ledger,1):
            if l['status'] in ('COMPLETE','COMPLETE_RECOVERED'):continue
            native=Path(l['workdir'])/'usage.json'
            r=parse(obj(native)) if native.exists() else {'bound':None,'auxiliary':None,'all_reported_models':None,'reasoning_subset':None,'extra_exec':None}
            r.update(record_id=l['record_id'],arm=l['arm'],attempt=l['attempt'],status=l['status'],source_path=str(native),source_exists=native.exists(),ledger_line=n,ledger_output=l.get('output_tokens'))
            if r['bound'] is not None:assert l['output_tokens']==r['bound']['output']
            rejected.append(r)
        for arm in ARMS:
            rs=[records[rid,arm] for rid in ids];rej=[r for r in rejected if r['arm']==arm]
            grades=dict(collections.Counter(r['grade'] for r in rs));verdicts=dict(collections.Counter(r['verdict'] for r in rs))
            assert grades==summary['arms'][arm]['grades'] and verdicts==summary['arms'][arm]['verdicts']
            accepted=plus([r['bound'] for r in rs]);assert accepted['output']==summary['arms'][arm]['output_sum']
            known_rejected=plus([r['bound'] for r in rej]);observed=plus([r['bound'] for r in rs+rej])
            arm_results[arm]={'planned':60,'accepted':len(rs),'grade_counts':grades,'verdict_counts':verdicts,'supported_refutations':sum(grades.get(g,0) for g in ['CAUGHT_MATCHING','CAUGHT_DIFFERENT']),'accepted_bound_model':accepted,
                'accepted_auxiliary_models':plus([r['auxiliary'] for r in rs]) if model=='opus' else None,
                'accepted_all_reported_models':plus([r['all_reported_models'] for r in rs]),
                'reasoning_subset_sum':sum(r['reasoning_subset'] for r in rs if r['reasoning_subset'] is not None),
                'extra_exec_known_cells':sum(r['extra_exec'] is not None for r in rs),'extra_exec_positive_cells':sum(r['extra_exec'] is not None and r['extra_exec']>0 for r in rs),
                'rejected_attempts':len(rej),'rejected_status_counts':dict(collections.Counter(r['status'] for r in rej)),
                'rejected_bound_model':known_rejected,'observed_solver_bound_model':observed,
                'observed_all_reported_models':plus([r['all_reported_models'] for r in rs+rej])}
        comparisons={};sensitivity={}
        for arm in ARMS[1:]:
            comparisons[arm]=compare(records,ids,arm);old=summary['paired']['refute_vs_'+arm]
            assert abs(comparisons[arm]['output_ratio']-old['output_ratio_of_sums'])<1e-12
            comparisons[arm]['historical_full_token_ratio']=old['all_tokens_ratio_of_sums']
            comparisons[arm]['historical_output_ci95']=old['output_ci95_record_bootstrap']
            a={'prove_full':'ProveFull','prove_earlystop':'ProveEarly','prove_earlystop_witness':'ProveEarlyWitness'}[arm]
            macro_changes.append({'macro':f'crClaims{model.title()}RefuteVs{a}AllTokRatio','old':old['all_tokens_ratio_of_sums'],'corrected':comparisons[arm]['full_token_ratio'],'changed':abs(comparisons[arm]['full_token_ratio']-old['all_tokens_ratio_of_sums'])>1e-12})
        witness='prove_earlystop_witness'
        sensitivity['without_hint']=compare(records,set(ids)-hint,witness)
        if all(records[r,a]['extra_exec'] is not None for r in ids for a in ['refute',witness]):
            no_tools={r for r in ids if all(records[r,a]['extra_exec']==0 for a in ['refute',witness])}
            sensitivity['without_recorded_extra_exec']=compare(records,no_tools,witness)
            sensitivity['without_hint_or_recorded_extra_exec']=compare(records,no_tools-hint,witness)
        results[model]={'arms':arm_results,'comparisons':comparisons,'witness_sensitivity':sensitivity,'accepted_records':list(records.values()),'rejected_records':rejected,'ledger_attempt_count':len(ledger)}
    assert results['gemini']['arms']['refute']['accepted_bound_model']['full_tokens']==2480272
    assert results['gemini']['arms']['prove_earlystop_witness']['accepted_bound_model']['full_tokens']==2745952
    # Inventory all existing full-token macro definitions/references; do not mutate canonical files.
    macro_occurrences=[]; canonical_pins={}
    for path in sorted(args.canonical.rglob('*.tex')):
        if '.git' in path.parts:continue
        text=path.read_text()
        for n,line in enumerate(text.splitlines(),1):
            if re.search(r'\\cr(?:Claims|Proofs)\w*AllTokRatio',line):
                canonical_pins[str(path.relative_to(args.canonical))]=hashlib.sha256(path.read_bytes()).hexdigest();macro_occurrences.append({'path':str(path.relative_to(args.canonical)),'line':n,'text':line,'definition':bool(re.search(r'\\(?:newcommand|renewcommand|providecommand)',line))})
    report={'schema':'claims60-corrected-native-accounting/v1','model_calls':0,'scope':'All720 accepted cells, all730 recorded solver-ledger attempts, fixed60claims/fourarms/three models; no grading or audit costs, no claim of exhaustive orphan-attempt coverage.',
        'formulas':{'sol':'uncached=input_tokens-cached_input_tokens; cache_read=cached_input_tokens; output includes reasoning; cache_write zero throughout this roster',
                    'gemini':'uncached=input_tokens; cache_read=cache_read_tokens; output includes thinking; reported total_tokens excludes cache reads',
                    'opus':'bound model inputTokens + cacheCreationInputTokens + cacheReadInputTokens + outputTokens; auxiliary modelUsage entries separated and also included in all_reported_models view'},
        'intervals':{'status':'new offline descriptive analysis, not preregistered; pointwise, no multiplicity adjustment','seed':SEED,'resamples':RESAMPLES,'method':'sorted record IDs; Python random.Random(seed), n draws with replacement per replicate; ratio of paired full-token sums; sorted values at indices500 and19499'},
        'limitations':['Unknown usage is null, never zero. Six Opus rejected attempts lack bound usage despite api_messages0; no pre-service inference is made.','Complete accepted records do not imply complete campaign cost. Rejected attempts, auxiliary models, downstream grades and checks must be distinguished.','Sol/Gemini all-reported totals use their native aggregate; no auxiliary-model split is available or inferred. Opus all-reported totals add every modelUsage entry, with auxiliary use separately visible.','Extra-execution counts are absent for Opus. No-tools sensitivities exclude paired outcomes post hoc and are descriptive.','Historical summary JSON and all canonical files remain unmodified. Output-ratio and observed-output fields are distinct and are not repaired by changing full-token fields.'],
        'models':results,'macro_corrections':macro_changes,'canonical_full_token_macro_occurrences':macro_occurrences,'canonical_inventory_sha256':canonical_pins,'source_sha256':PINS}
    if args.verify_pins:
        expected=json.loads(args.verify_pins.read_text())['source_sha256'];assert expected==PINS,'Source pin drift'
    (out/'RESULTS.json').write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
    lines=['% Accepted-attempt totals. First four components refer to bound model; auxiliary full tokens added only in final column.',r'\begin{tabular}{llrrrrrrr}',r'\toprule',r'Model & Arm & Uncached & Cache create & Cache read & Output & Bound full & Aux. full & All reported \\',r'\midrule']
    labels={'refute':'Search','prove_full':'Full proof','prove_earlystop':'Early stop','prove_earlystop_witness':'Early + witness'}
    for model in MODELS:
        for arm in ARMS:
            a=results[model]['arms'][arm];v=a['accepted_bound_model'];aux=a['accepted_auxiliary_models']
            lines.append(model.title()+' & '+labels[arm]+' & '+' & '.join(f'{v[k]:,}' for k in COMPONENTS+('full_tokens',))+' & '+(f"{aux['full_tokens']:,}" if aux is not None else r'\textemdash')+' & '+f"{a['accepted_all_reported_models']['full_tokens']:,}"+r' \\')
    lines += [r'\bottomrule',r'\end{tabular}']
    (out/'claims60_corrected_components.tex').write_text('\n'.join(lines)+'\n')
    mainlines=[r'\begin{tabular}{lccc}',r'\toprule',r'Model & Supported S/O/W & Output S/W & Full S/W \\',r'\midrule']
    for model in MODELS:
        m=results[model];c=m['comparisons']['prove_earlystop_witness'];counts='/'.join(str(m['arms'][a]['supported_refutations']) for a in ['refute','prove_earlystop','prove_earlystop_witness'])
        mainlines.append(model.title()+' & '+counts+' & '+f"{c['output_ratio']:.3f}"+' & '+f"{c['all_reported_model_full_token_ratio']:.3f}"+r' \\')
    mainlines += [r'\bottomrule',r'\end{tabular}']
    (out/'claims60_corrected_main.tex').write_text('\n'.join(mainlines)+'\n')
    macros=['% Load after historical cost_repro_macros.tex. Bound-model accepted-attempt full-token corrections only.']
    for r in macro_changes:macros.append('\\renewcommand{\\'+r['macro']+'}{'+f"{r['corrected']:.3f}"+'}')
    (out/'claims60_corrected_macros.tex').write_text('\n'.join(macros)+'\n')
    print(json.dumps({m:{a:results[m]['arms'][a]['accepted_bound_model']['full_tokens'] for a in ARMS} for m in MODELS},indent=2));print('source files pinned:',len(PINS))
if __name__=='__main__':main()
