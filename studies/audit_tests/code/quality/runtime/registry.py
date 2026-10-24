"""Read-only scientific gates and immutable correction-run registration.

No provider, GPU or frozen runner imports occur in this module.
"""
import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import sys
import tempfile

HERE=Path(__file__).resolve().parent
REPO=HERE.parents[3]
SCHEMA='corrected-ccl-run-registry/v1'
COMPONENTS=('measured_tokens','unknown_attempts','observed_lower_bound_tokens','charged_tokens')
BUDGET_METHODOLOGY={'path':'astra/resource285_quality_check_20260923/benchmark_reruns/ASTRA_CORRECTION_BUDGET_POLICY_v1.json',
    'sha256':'0ddc353d1f0f72473c27629201148b1aed2cf80699a9d6ebefef647f80149097'}
RUNTIME_NAMES=('registry.py','correction_accounting.py','dispatch_corrected.py','local_adapter.py','pilot_view.py','resolve_and_score_corrected.py')

def need(test,message):
    if not test:raise ValueError(message)
def canonical(value):return json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()
def sha(raw):return hashlib.sha256(raw).hexdigest()
def vsha(value):return sha(canonical(value))
def safe(value):return re.sub(r'[^A-Za-z0-9._-]','_',value)
def key(root_label,lane):
    for name in (root_label,lane):
        need(isinstance(name,str) and name and safe(name)==name and not name.startswith(('.','-')),'Unsafe configuration identity')
    return root_label+'__'+lane

def execution_configurations(manifest):
    return manifest.get('physical_configurations',manifest['reported_configurations'])

def validate_physical_plan(m):
    physical=execution_configurations(m);lookup={};donor_configs={};seen=set()
    for c in physical:
        k=key(c['root_label'],c['lane']);need(k not in seen,'Duplicate physical configuration');seen.add(k)
        need(c.get('scope','active_lane')=='active_lane','Physical runtime donor must be a frozen active lane')
        need(c['runner'] in {'run_critic.py','run_local.py','run_agy.py','run_codex.py'},'Unsupported physical runner')
        for call in c['calls']:
            if call['fresh_call_required']:
                identity=(c['root_label'],c['lane'],call['record_id']);lookup[identity]=call;donor_configs[identity]=c
    aliases={k:[] for k in lookup}
    for c in m['reported_configurations']:
        scope=c.get('scope','active_lane')
        need(scope in {'active_lane','lifetime_evaluation'},'Unknown reporting view')
        if scope=='lifetime_evaluation':
            need('physical_configurations' in m and bool(c.get('joined_source_policy')),'Joined view lacks replay-bound source/physical policy')
            mapping=m.get('physical_reporting_map') or {}
            need(mapping.get('policy_state')=='APPROVED_BOUND' and bool(mapping.get('shared_policy')),'Shared physical-call approval not bound')
        for call in c['calls']:
            if not call['fresh_call_required']:continue
            default={'root_label':c['root_label'],'lane':c['lane'],'record_id':call['record_id']}
            pk=call.get('physical_call_key',default)
            need(set(pk)=={'root_label','lane','record_id'} and pk['record_id']==call['record_id'],'Invalid physical call identity')
            need(pk['lane']==c['lane'],'Shared physical call cannot substitute another model')
            identity=(pk['root_label'],pk['lane'],pk['record_id']);need(identity in lookup,'Reporting view omits physical execution')
            donor=lookup[identity]
            if scope=='lifetime_evaluation':
                equivalence=call.get('execution_equivalence') or {}
                need(equivalence.get('approval_bound') is True and equivalence.get('actual_settings_equal') is True
                    and equivalence.get('native_cli_version')=='2.1.275'
                    and equivalence.get('donor_configuration_id')==donor_configs[identity].get('configuration_id')
                    and isinstance(equivalence.get('execution_contract_sha256'),str)
                    and re.fullmatch('[0-9a-f]{64}',equivalence['execution_contract_sha256']) is not None,
                    'Joined native inference equivalence lacks exact approval/donor/version binding')
            for field in ('new_user_prompt_sha256','new_system_prompt_sha256','new_logical_messages_sha256','new_request_surface_sha256'):
                need(call[field]==donor[field],'Shared physical source/request contracts differ')
            aliases[identity].append(default)
    for identity,call in lookup.items():
        need(bool(aliases[identity]),'Physical call has no declared reporting view')
        declared=call.get('reporting_aliases',[dict(zip(('root_label','lane','record_id'),identity))])
        projected=[{k:a[k] for k in ('root_label','lane','record_id')} for a in declared]
        need(sorted(projected,key=canonical)==sorted(aliases[identity],key=canonical),'Physical/reporting alias coverage differs')
    return physical

def path(value,repo=REPO):
    repo=Path(repo).resolve();candidate=Path(value)
    candidate=candidate if candidate.is_absolute() else repo/candidate
    need(candidate.is_relative_to(repo),'Path outside repository')
    for part in (candidate,*candidate.parents):
        need(not part.is_symlink(),'Symlink path refused')
        if part==repo:break
    result=candidate.resolve();need(result.is_relative_to(repo),'Path escape refused');return result

def descriptor(value,repo=REPO):
    p=path(value,repo);raw=p.read_bytes()
    return {'path':str(p.relative_to(Path(repo).resolve())),'sha256':sha(raw),'bytes':len(raw)}

def bound(d,repo=REPO):
    need(isinstance(d,dict) and isinstance(d.get('path'),str),'Missing file descriptor')
    raw=path(d['path'],repo).read_bytes()
    need(sha(raw)==d.get('sha256'),'Bound file hash drift: '+d['path'])
    if 'bytes' in d:need(len(raw)==d['bytes'],'Bound file length drift')
    return raw

def load_code(d,name,repo=REPO):
    raw=bound(d,repo);p=path(d['path'],repo)
    import types
    module=types.ModuleType(name);module.__file__=str(p)
    exec(compile(raw,str(p),'exec'),module.__dict__)
    return module

def write_new(p,value):
    p=Path(p);p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('xb') as f:f.write(canonical(value)+b'\n');f.flush();os.fsync(f.fileno())

def atomic(p,value):
    p=Path(p);p.parent.mkdir(parents=True,exist_ok=True)
    fd,tmp=tempfile.mkstemp(prefix=p.name+'.',suffix='.tmp',dir=p.parent)
    try:
        with os.fdopen(fd,'wb') as f:f.write(canonical(value)+b'\n');f.flush();os.fsync(f.fileno())
        os.replace(tmp,p)
    finally:
        if os.path.exists(tmp):os.unlink(tmp)

def scientific_gate(d,repo=REPO):
    """Replay the actual bound manifest builder, including both all-three gates."""
    m=json.loads(bound(d,repo))
    need(m.get('schema')=='corrected-ccl-affected-input-manifest/v2' and m.get('state')=='FROZEN_DEFINITION',
         'Final manifest v2 is not frozen')
    need(m.get('ready_for_claude_dispatch') is True and m.get('blockers')==[],'Scientific dispatch gates unresolved')
    need(m.get('population_definition_state')=='ALL_GATES_APPROVED' and isinstance(m.get('current_population_definition'),dict),
         'Current scoring masks are not approved')
    for label in ('reference_adjudication','all_three_consensus'):
        need(m.get(label,{}).get('all_three_bound') is True,'Missing '+label)
    b=m['bindings'];extension=b['accepted_extension']
    need(extension.get('exact_replay_pass') is True,'Accepted extension replay missing')
    builder=load_code(b['builder'],'corrected_ccl_manifest_replay',repo)
    old=sys.dont_write_bytecode;sys.dont_write_bytecode=True
    try:
        options={}
        shared=(m.get('physical_reporting_map') or {}).get('shared_policy')
        if shared:options['shared_execution_policy_path']=path(shared['receipt']['path'],repo)
        replay=builder.build(export_path=path(b['export']['path'],repo),
            extension_path=path(extension['provenance']['path'],repo),
            reference_items_path=path(m['reference_items']['path'],repo),
            reference_receipt_path=path(m['reference_adjudication']['receipt']['path'],repo),
            consensus_path=path(m['all_three_consensus']['receipt']['path'],repo),**options)
    finally:sys.dont_write_bytecode=old
    need(replay==m,'Manifest differs from exact scientific replay')
    configs=m['reported_configurations'];seen=set()
    for c in configs:
        k=key(c['root_label'],c['lane']);need(k not in seen,'Duplicate configuration');seen.add(k)
        need(c['runner'] in {'run_critic.py','run_local.py','run_agy.py','run_codex.py'},'Unsupported runner; explicit implementation required')
        ids=[r['record_id'] for r in c['calls']]
        need(len(ids)==len(set(ids))==len({safe(r).casefold() for r in ids}),'Duplicate/unsafe item directory identity')
        need(all(safe(r) not in {'','.','..'} and not safe(r).startswith('.') for r in ids),'Unsafe item identity')
        for call in c['calls']:
            need(call['current_roles'] is not None and type(call['current_benchmark_admitted']) is bool,'Current call roles missing')
            need(call['current_roles']==m['current_population_definition']['record_masks'][call['record_id']]['roles'],'Call mask mismatch')
            need(call['fresh_call_required']==(call['record_id'] in m['affected_record_ids']),'Affected call union mismatch')
            need(not call['witness_reference_or_dossier_fields_supplied_to_renderer'],'Source-only contract violated')
    need(len(configs)==m['counts']['reported_configurations'],'Configuration count mismatch')
    validate_physical_plan(m)
    return m

def policy_gate(d,manifest_d,m,repo=REPO):
    p=json.loads(bound(d,repo))
    need(p.get('schema')=='corrected-ccl-prospective-epoch-policy/v1' and p.get('status')=='APPROVED_PROSPECTIVELY',
         'Explicit prospective correction budget/epoch policy required')
    s=p['subject'];need(s.get('manifest')==manifest_d,'Epoch policy binds another manifest')
    need(isinstance(s.get('fresh_root'),str) and str(path(s['fresh_root'],repo).relative_to(Path(repo).resolve()))==s['fresh_root'],
         'Prospective policy must bind one canonical fresh root; directory changes cannot reset its budget')
    need(isinstance(s.get('epoch_id'),str) and s['epoch_id'].startswith('correction-'),'Distinct correction epoch required')
    need(s.get('max_physical_attempts_per_item')==2,'Physical attempt cap must remain two')
    need(s.get('budget_policy')=='EXPLICIT_CORRECTION_PASS_ALLOWANCE','Silent budget reset refused')
    need(s.get('budget_methodology')==BUDGET_METHODOLOGY,'Accepted inclusive-floor budget methodology not bound')
    bound(BUDGET_METHODOLOGY,repo)
    runtime=s.get('runtime_files',[])
    need({Path(x['path']).name for x in runtime}==set(RUNTIME_NAMES) and len(runtime)==len(RUNTIME_NAMES),'Exact runtime code freeze missing')
    for entry in runtime:
        need(path(entry['path'],repo)==HERE/Path(entry['path']).name,'Runtime file is not this implementation')
        bound(entry,repo)
    approval=json.loads(bound(p['approval_report'],repo))
    need(approval.get('decision')=='APPROVE_CORRECTION_EXECUTION' and approval.get('subject_sha256')==vsha(s)
         and approval.get('prospective') is True and approval.get('actual_authorizer')==p.get('approved_by')
         and bool(p.get('approved_by')) and bool(approval.get('evidence')),'Actual prospective approval is absent or unbound')
    configs={key(c['root_label'],c['lane']):c for c in execution_configurations(m)}
    need(set(s.get('configurations',{}))==set(configs),'Budget policy silently omits/adds configurations')
    coverage=set()
    for k,row in s['configurations'].items():
        need(type(row.get('lane_cap')) is int and row['lane_cap']>0,'Explicit cumulative lane cap missing')
        cost=json.loads(bound(row['historical_cost_report'],repo))
        need(cost.get('schema')=='corrected-ccl-historical-cost/v1' and cost.get('configuration')==k,
             'Historical campaign cost report missing')
        need(cost.get('no_double_counted_attempts') is True and bool(cost.get('census_bindings')),'Historical receipt census absent')
        for source in cost['census_bindings']:bound(source,repo)
        units=cost.get('units');need(isinstance(units,list) and bool(units),'Disjoint historical cost units missing')
        totals={name:0 for name in COMPONENTS};unit_ids=set()
        for unit in units:
            need(unit.get('unit_id') and unit['unit_id'] not in unit_ids,'Duplicate historical cost unit');unit_ids.add(unit['unit_id'])
            ids=unit.get('coverage_ids',[])
            need(ids and len(ids)==len(set(ids)) and not coverage.intersection(ids),'Historical attempt/carryover counted twice')
            coverage.update(ids)
            need(bool(unit.get('evidence')),'Historical cost unit evidence missing')
            for evidence in unit['evidence']:bound(evidence,repo)
            need(set(unit.get('components',{}))==set(COMPONENTS),'Cost unit components missing')
            for name,value in unit['components'].items():
                need(type(value) is int and value>=0,'Invalid cost unit component');totals[name]+=value
        components=cost.get('components',{})
        need(set(components)==set(COMPONENTS) and all(type(x) is int and x>=0 for x in components.values()),'Invalid historical cost components')
        need(row.get('historical_components')==components,'Historical cost differs from approved policy')
        need(totals==components,'Historical total differs from disjoint unit sum')
        need(components['charged_tokens']>=components['measured_tokens'] and components['charged_tokens']>=components['observed_lower_bound_tokens'],
             'Historical conservative charge smaller than observed cost')
        need(row.get('historical_cost_included_once') is True,'Historical cost must be included exactly once')
        n=sum(bool(c['fresh_call_required']) for c in configs[k]['calls'])
        need(row.get('fresh_record_count')==n and row.get('fresh_lane_cap')==120000*n,'Fresh lane cap must equal 120000 times distinct targeted IDs')
        need(row['lane_cap']==components['charged_tokens']+row['fresh_lane_cap'],'Cumulative ceiling differs from historical cost plus explicit fresh allowance')
    return p

def gate(registry,repo=REPO):
    need(registry.get('schema')==SCHEMA,'Invalid correction registry')
    m=scientific_gate(registry['manifest'],repo)
    p=policy_gate(registry['policy'],registry['manifest'],m,repo)
    need(registry['epoch_id']==p['subject']['epoch_id'],'Registry epoch drift')
    need(registry['fresh_root']==p['subject']['fresh_root'],'Registry moved outside its prospective budget root')
    need(registry['configurations']==execution_configurations(m),'Registry physical lane/input drift')
    need(registry['reporting_configurations']==m['reported_configurations'],'Registry silently omitted/changed a reporting view')
    return m,p

def prepare(manifest_d,policy_d,fresh_root,repo=REPO):
    bound(manifest_d,repo);bound(policy_d,repo)
    manifest_d=descriptor(manifest_d['path'],repo);policy_d=descriptor(policy_d['path'],repo)
    m=scientific_gate(manifest_d,repo);p=policy_gate(policy_d,manifest_d,m,repo)
    root=path(fresh_root,repo)
    need(str(root.relative_to(Path(repo).resolve()))==p['subject']['fresh_root'],'Another output root cannot reuse this approved epoch/budget')
    need(not any(part in {'runs','canary'} or part.startswith('superseded_') for part in root.parts),'Historical output namespace refused')
    for c in m['reported_configurations']:
        original=path(c['root'],repo)
        need(not root.is_relative_to(original) and not original.is_relative_to(root),'Historical experiment output overlap')
    registry={'schema':SCHEMA,'manifest':manifest_d,'policy':policy_d,'epoch_id':p['subject']['epoch_id'],
        'fresh_root':str(root.relative_to(Path(repo).resolve())),'configurations':execution_configurations(m),
        'reporting_configurations':m['reported_configurations'],
        'runtime_files':p['subject']['runtime_files'],'source_only_fields':['record_id','split','lines'],
        'terminal_index_schema':'corrected-ccl-terminal-index/v1','model_calls_performed_by_prepare':0}
    if root.exists():
        need((root/'RUN_REGISTRY.json').is_file(),'Fresh root already exists without this registry')
        need(json.loads((root/'RUN_REGISTRY.json').read_bytes())==registry,'Existing fresh root has another registry')
    else:
        root.mkdir(parents=True);write_new(root/'RUN_REGISTRY.json',registry)
    return descriptor(root/'RUN_REGISTRY.json',repo)

def load_registry(d,repo=REPO):
    r=json.loads(bound(d,repo));root=path(r['fresh_root'],repo)
    need(path(d['path'],repo)==root/'RUN_REGISTRY.json','Registry moved from its bound fresh root')
    gate(r,repo);return r

def verify_registry(filename,expected_sha256,repo=REPO):
    d=descriptor(filename,repo);need(d['sha256']==expected_sha256,'Registry hash differs')
    r=load_registry(d,repo)
    return r,json.loads(bound(r['manifest'],repo))

def source_item(item):
    need(set(('record_id','split','lines'))<=set(item),'Incomplete frozen source item')
    return {k:copy.deepcopy(item[k]) for k in ('record_id','split','lines')}
