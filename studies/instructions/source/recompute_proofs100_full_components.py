#!/usr/bin/env python3
"""Offline full-token components for the retained proofs100 four-arm comparison.
No inference, grading, compilation, historical-input writes, or imputation.
"""
from pathlib import Path
import hashlib, json, collections
ROOT=Path(__file__).resolve().parents[2]
OUT=Path(__file__).resolve().parent
BASE=ROOT/'qedbench_certificate_availability_triage'
RUN=BASE/'runs/cost_experiment_repro_20260915'
ARMS=('refute','verify_full','verify_earlystop','verify_earlystop_witness')
PINS={}
def read(p):
    b=p.read_bytes();PINS[str(p.relative_to(ROOT)) if p.is_relative_to(ROOT) else str(p)]=hashlib.sha256(b).hexdigest();return b
def obj(p):return json.loads(read(p))
def lines(p):return [json.loads(x) for x in read(p).splitlines() if x]
def valid(v):return type(v) is int and v>=0
def parts(u, model):
    out=u.get('output_tokens_bound_model')
    if model=='sol':
        t=u['usage_total'];i,c=t['input_tokens'],t['cached_input_tokens'];assert valid(i) and valid(c) and i>=c
        assert t.get('cache_write_input_tokens',0)==0
        inp=i-c;think=t.get('reasoning_output_tokens')
    else:
        t=u['usage'];inp,c=t['input_tokens'],t['cache_read_tokens'];think=t.get('thinking_tokens')
    assert all(valid(v) for v in (inp,c,out)) and t['output_tokens']==out
    if think is not None:assert valid(think) and think<=out
    return {'input_uncached_plus_creation':inp,'input_cache_read':c,'output':out,'full_tokens':inp+c+out}
manifest=obj(RUN/'manifest.json');ids=set(manifest['proofs100']);assert len(ids)==100
# Exact manifest input binding; no new reference labels or grades computed.
for rid in sorted(ids):
    p=BASE/'runs/cost_experiment/inputs'/f'{rid.replace(chr(32), chr(95))}.json';read(p)
    assert PINS[str(p.relative_to(ROOT))]==manifest['proofs100'][rid]['input_sha256']
audit=obj(ROOT/'astra/referee_revision_audit_20260917/audit.json')
old_parser=read(BASE/'scripts/cost_experiment_telemetry.py')
rows=[]; records=[]; attempt_scope={}
for model in ('sol','gemini'):
    ledger=lines(RUN/f'ledger/proofs100_{model}.jsonl')
    assert len({(x['record_id'],x['arm'],x['attempt']) for x in ledger})==len(ledger)
    assert all(x['record_id'] in ids and x['arm'] in ARMS and x['model']==model for x in ledger)
    accepted=[x for x in ledger if x['status'] in ('COMPLETE','COMPLETE_RECOVERED')]
    assert len(accepted)==400
    rejected=[x for x in ledger if x not in accepted]
    attempt_scope[model]={'accepted':len(accepted),'excluded_additional_attempts':len(rejected),'excluded_by_status':dict(collections.Counter(x['status'] for x in rejected)), 'excluded_cost_scope':'Excluded from this accepted-attempt table, not imputed zero; original attempt ledger and historical observed-output table retain them.'}
    summary=obj(RUN/f'summary/proofs100_{model}.json')
    for arm in ARMS:
        sub=[]
        for rid in sorted(ids):
            p=RUN/'usage/proofs100'/model/f'{rid.replace(chr(32), chr(95))}__{arm}.json';w=obj(p)
            assert w['record_id']==rid and w['arm']==arm
            u=w['usage'];assert u['status']==0 and u['exit_code']==0
            matches=[x for x in accepted if x['record_id']==rid and x['arm']==arm]
            assert len(matches)==1
            l=matches[0];assert l['attempt']==w['attempt']
            native=Path(l['workdir'])/'usage.json';assert obj(native)==u
            q=parts(u,model);assert l['output_tokens']==q['output']
            sub.append(q);records.append({'model':model,'record_id':rid,'arm':arm,'attempt':w['attempt'],'wrapper':str(p.relative_to(ROOT)),'native_usage':str(native),**q})
        sums={k:sum(x[k] for x in sub) for k in sub[0]}
        assert sums['output']==summary['arms'][arm]['output_sum']
        rows.append({'model':model,'arm':arm,'planned':100,'known_usage':100,'missing_usage':0,'unknown_ids':[],'token_source':'accepted native usage; named engine aggregate',**sums})
old=lines(BASE/'runs/cost_experiment/telemetry.jsonl')
assert len(old)==399 and len({(x['record_id'],x['arm']) for x in old})==399
assert all(x['record_id'] in ids and x['arm'] in ARMS for x in old)
summary=obj(RUN/'summary/proofs100_opus_task1.json')
for arm in ARMS:
    sub=[x for x in old if x['arm']==arm]
    assert all(valid(x[k]) for x in sub for k in ('input_uncached','input_cache_read','output'))
    sums={'input_uncached_plus_creation':sum(x['input_uncached'] for x in sub),'input_cache_read':sum(x['input_cache_read'] for x in sub),'output':sum(x['output'] for x in sub)}
    sums['full_tokens']=sum(sums.values())
    assert sums['output']==summary['arms'][arm]['output_sum']
    missing=sorted(ids-{x['record_id'] for x in sub})
    assert len(missing)==(1 if arm=='verify_earlystop' else 0)
    rows.append({'model':'opus_task1','arm':arm,'planned':100,'known_usage':len(sub),'missing_usage':len(missing),'unknown_ids':missing,'token_source':'provisional archived transcript per-line sums, may duplicate content-block usage',**sums})
    for x in sub:records.append({'model':'opus_task1','record_id':x['record_id'],'arm':arm,'input_uncached_plus_creation':x['input_uncached'],'input_cache_read':x['input_cache_read'],'output':x['output'],'full_tokens':x['input_uncached']+x['input_cache_read']+x['output']})
# Exact match with already-reviewed primary search/witness totals for each model.
for comparison in audit['required_witness_comparison']:
    for arm,expected in comparison['accepted_attempt_token_components'].items():
        got=next(x for x in rows if x['model']==comparison['model'] and x['arm']==arm)
        assert got['input_uncached_plus_creation']==expected['input_uncached']
        assert all(got[k]==expected[k] for k in ('input_cache_read','output','full_tokens'))
labels={'sol':'Sol','gemini':'Gemini','opus_task1':'Archived Opus$^*$'}
arm_labels=dict(zip(ARMS,('Search','Full review','Early stop','Early + witness')))
tex=[r'\begin{table}[ht]',r'\centering\scriptsize\setlength{\tabcolsep}{3pt}',r'\caption{Full token components for all four proof100 instruction arms. Sums cover accepted attempts with known usage; $n$ is usage coverage out of 100, not grade coverage. Uncached input includes cache creation in the archived Opus records. Reasoning is included in output once. Additional attempts, graders and downstream checks are excluded. $^*$Archived Opus transcript sums can repeat usage and remain provisional; its missing early-stop record is unknown, not zero. Absolute costs are not comparable across harnesses.}',r'\label{tab:proofs100-fourarm-full-components}',r'\resizebox{\linewidth}{!}{%',r'\begin{tabular}{llrrrrr}',r'\toprule',r'Model & Instruction & $n$ & Uncached input & Cache reads & Output & Full tokens \\',r'\midrule']
for i,r in enumerate(rows):
    if i and i%4==0:tex.append(r'\midrule')
    tex.append(labels[r['model']]+' & '+arm_labels[r['arm']]+' & '+str(r['known_usage'])+' & '+' & '.join(f'{r[k]:,}' for k in ('input_uncached_plus_creation','input_cache_read','output','full_tokens'))+r' \\')
tex += [r'\bottomrule',r'\end{tabular}}',r'\end{table}']
path=OUT/'PROOFS100_FULL_COMPONENTS.tex';path.write_text('\n'.join(tex)+'\n')
receipt={'status':'PASS','scope':'All four retained proofs100 arms; accepted attempt native sums for Sol/Gemini and original provisional Opus transcript sums. No model/grading/Lean calls.','rows':rows,'checks':{'frozen_input_hashes':100,'sol_native_wrapper_ledger_matches':400,'gemini_native_wrapper_ledger_matches':400,'opus_unique_archived_rows':399,'prior_primary_components_identical':True,'per_arm_output_sums_equal_original_summaries':True},'accounting_rules':{'sol':'native input includes cache: uncached=input-cached; full=input+output','gemini':'native input is uncached: full=input+cache_read+output; do not subtract cache','opus_task1':'original input_uncached includes cache creation; full=input_uncached+cache_read+output; provisional per-line duplicate risk','reasoning':'subset of output; not added again','missing_opus_early':'99 known totals only; remaining full usage unknown; no full-total claim for100'},'excluded_attempt_scope':attempt_scope,'source_sha256':PINS,'records':records,'reproduction_script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'generated_tex_sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
(OUT/'PROOFS100_FULL_COMPONENTS_CHECK.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
print(json.dumps({'status':'PASS','rows':rows,'source_files':len(PINS),'table_sha256':receipt['generated_tex_sha256']},indent=2))
