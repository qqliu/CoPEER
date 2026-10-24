#!/usr/bin/env python3
"""Offline verification of saved results and token arithmetic; never calls a model or Lean."""
from pathlib import Path
import json,hashlib,collections
HERE=Path(__file__).resolve().parent
read=lambda p:json.loads((HERE/p).read_text())
D=read('results.json');T=read('tokens.json');M=read('MANIFEST.json')
for f in M['files']:
    p=HERE/f['path'];assert p.is_file(),f['path']
    assert hashlib.sha256(p.read_bytes()).hexdigest()==f['sha256'],f['path']
C=D['cells'];assert len(C)==288 and len({c['cell_id'] for c in C})==288
assert len(D['record_ids'])==16 and len(D['models'])==3
for c in C:
    assert c['record_id'] in D['record_ids'] and c['model'] in D['models']
    p=HERE/'cells'/c['cell_id']/'SUBMISSION.lean'
    if 'submission_export_sha256' in c:
        assert hashlib.sha256(p.read_bytes()).hexdigest()==c['submission_export_sha256']
        assert c['submission_export_sha256']==c['submission_original_sha256'], 'Proof bytes changed'
    else:
        assert not p.exists()
    if c['grade']:
        g=read('cells/'+c['cell_id']+'/grade.json')
        assert g['submission_sha256']==c['submission_original_sha256']
        assert g['verdict']==c['original_verdict']
    x=c.get('composition')
    if x:
        a=read('cells/'+c['cell_id']+'/helper_audit.json')
        assert a['submission_sha256']==c['submission_original_sha256']
        assert a['disposition']==x['audit_disposition']
        assert x['original_verdict']==c['original_verdict'] and x['composed_verdict']==c['composed_verdict']
        if c['composed_verdict']!=c['original_verdict']:
            assert a['disposition']=='clean' and x['mechanism_match']
            assert x['grade_failed_checks']==['axioms'] and not x['grade_axioms_disallowed']
    else:
        assert c['original_verdict']==c['composed_verdict']

summary=[]
for model in D['models']:
 for arm in ['A','B']:
    group=[c for c in C if c['model']==model and c['condition']==arm]
    assert len(group)==48
    for attempt in [1,2,3]:
        rows=[c for c in group if c['attempt']==attempt];assert len(rows)==16
        expected=D['expected_summary'][model+'|'+arm+'|attempt'+str(attempt)]
        passes=sum(c['composed_verdict']=='PASS' for c in rows)
        fails=sum(c['composed_verdict']=='FAIL' for c in rows)
        absent=sum('submission_export_sha256' not in c for c in rows)
        valid=sum(c['composed_verdict']=='PASS' and c['runtime_class']=='VALID_SUBMISSION' for c in rows)
        assert (passes,fails,absent,valid)==(expected.get('PASS',0),expected.get('FAIL',0),expected['submission_absent'],expected.get('PASS_valid',0))
        if attempt==1:
            summary.append({'model':model,'condition':arm,'PASS':passes,'FAIL':fails,'Absent':absent,'runtime_compliant_PASS':valid})
    anypass=len({c['record_id'] for c in group if c['composed_verdict']=='PASS'})
    expected_any={'claude-opus-5-5':{'A':16,'B':16},'claude-sonnet-5':{'A':14,'B':16},'gpt-oss-120b':{'A':2,'B':3}}[model][arm]
    assert anypass==expected_any
    summary[-1]['any_attempt_PASS']=anypass

assert set(T['cells'])=={c['cell_id'] for c in C if c['attempt']==1}
for cid,c in T['cells'].items():
    u=c['recorded_usage'];assert u['input_tokens_total']==u['provider_input_tokens']+u['provider_cache_read_tokens']+u['provider_cache_creation_tokens']
    assert u['full_tokens']==u['input_tokens_total']+u['output_tokens']
    for field,val in u.items():assert val==sum(p['recorded_usage'][field] for p in c['physical_attempt_components'])
for row in T['summaries']:
    cells=[c for c in T['cells'].values() if c['model']==row['model'] and c['arm']==row['arm']]
    assert len(cells)==16
    for field,val in row['recorded_usage'].items():assert val==sum(c['recorded_usage'][field] for c in cells)
    assert row['cells_with_complete_native_usage']==sum(c['native_usage_complete'] for c in cells)
    assert row['recorded_usage_is_lower_bound']==any(c['recorded_usage_is_lower_bound'] for c in cells)
# Reconstruct every first-attempt token component from exported native/request receipts.
N=read('provenance/native_usage.json')
assert N['source_selection_sha256']==D['source_table_sha256']
assert N['token_summary_sha256']==hashlib.sha256((HERE/'tokens.json').read_bytes()).hexdigest()
assert set(N['cells'])==set(T['cells'])
all_request_hashes=[]; complete=0; physical_count=0
ci={c['cell_id']:c for c in C}
for cid,row in N['cells'].items():
    expected=T['cells'][cid]
    assert row['original_record_sha256']==ci[cid]['original_record_sha256']
    assert row['native_usage_complete']==expected['native_usage_complete']
    assert row['recorded_usage_is_lower_bound']==expected['recorded_usage_is_lower_bound']
    total=collections.Counter()
    for p in row['physical_attempts']:
        physical_count+=1
        assert len(p['original_attempt_receipt_sha256'])==len(p['original_usage_object_sha256'])==64
        assert p['provider_requests_observed']==len(p['per_request'])
        u=collections.Counter()
        for request in p['per_request']:
            h=request['request_id_sha256'];assert len(h)==64;all_request_hashes.append(h)
            if row['model']=='gpt-oss-120b':
                u['provider_input_tokens']+=request.get('prompt_tokens') or 0
                u['output_tokens']+=request.get('completion_tokens') or 0
                assert request['total_tokens']==request['prompt_tokens']+request['completion_tokens']
            else:
                for out_name,in_name in [('provider_input_tokens','input_tokens'),('provider_cache_read_tokens','cache_read_input_tokens'),('provider_cache_creation_tokens','cache_creation_input_tokens'),('output_tokens','output_tokens')]:
                    u[out_name]+=request.get(in_name) or 0
        native=p['native']
        assert p['native_usage_complete']==(native is not None)
        if native is not None:
            complete+=1;v=collections.Counter()
            for model_usage in native['per_model'].values():
                for out_name,in_name in [('provider_input_tokens','inputTokens'),('provider_cache_read_tokens','cacheReadInputTokens'),('provider_cache_creation_tokens','cacheCreationInputTokens'),('output_tokens','outputTokens')]:
                    v[out_name]+=model_usage.get(in_name) or 0
            for field in ['provider_input_tokens','provider_cache_read_tokens','provider_cache_creation_tokens','output_tokens']:assert u[field]==v[field]
            assert native['output_tokens']==u['output_tokens']
            assert native['total_tokens']==sum(u.values())
        total.update(u)
    total['input_tokens_total']=sum(total[k] for k in ['provider_input_tokens','provider_cache_read_tokens','provider_cache_creation_tokens'])
    total['full_tokens']=total['input_tokens_total']+total['output_tokens']
    for field,val in expected['recorded_usage'].items():assert total[field]==val,(cid,field,total[field],val)
assert (len(N['cells']),physical_count,complete)==(96,96,91)
assert len(all_request_hashes)==len(set(all_request_hashes))==929

# Bind selected records and saved predecessor provenance without executing historical runs.
L=read('provenance/recovery_ledger.json');V=read('provenance/support_versions.json')
assert len(L['cells'])==len(C)
ci={c['cell_id']:c for c in C}; selected_count=predecessor_count=environmental_predecessors=0
for row in L['cells']:
    c=ci[row['cell_id']]; selected=[r for r in row['candidates'] if r['selected']]
    assert len(selected)==1
    chosen=selected[0]
    assert row['selected_original_record_sha256']==chosen['original_record_sha256']==c['original_record_sha256']
    assert chosen['version']==row['selected_version']
    assert chosen['runtime_class_as_recorded']==c['runtime_class'] and chosen['environmental_cause'] is None
    assert chosen['original_submission_sha256']==c.get('submission_original_sha256')
    selected_count+=1
    for r in row['candidates']:
        assert len(r['original_record_sha256'])==64
        for e in r['environmental_evidence']: assert len(e['original_sha256'])==64
        if not r['selected']:
            predecessor_count+=1;environmental_predecessors+=r['environmental_cause'] is not None
assert {'selected':selected_count,'predecessor':predecessor_count,'environmental_predecessor':environmental_predecessors}==L['counts']
assert (selected_count,predecessor_count,environmental_predecessors)==(288,364,184)
old=V['older_variant'];later=V['later_variant']; old_cells=[];later_count=0
for c in C:
    if c['grade']:
        g=read('cells/'+c['cell_id']+'/grade.json')
        stamp=g['invocation']['validator_files_sha256']['repair_common.py']
        if stamp==old['original_sha256']:old_cells.append(c['cell_id'])
        else: assert stamp==later['original_sha256'];later_count+=1
assert sorted(old_cells)==sorted(old['saved_grade_cells']) and len(old_cells)==old['saved_grade_count']==20
assert later_count==later['saved_grade_count']==226
for variant in [old,later]: assert hashlib.sha256((HERE/variant['path']).read_bytes()).hexdigest()==variant['export_sha256']

print(json.dumps({'verification':'PASS','cells':len(C),'proof_files':sum('submission_export_sha256' in c for c in C),'native_usage_receipts':physical_count,'numeric_request_rows':len(all_request_hashes),'predecessor_records':predecessor_count,'older_support_grades':len(old_cells),'first_attempt_summary':summary,'tokens':T['summaries']},indent=2))
