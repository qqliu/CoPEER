#!/usr/bin/env python3
"""Validate/apply approved corrections while preserving prior reviewed30 bytes.

Default mode validates only. Applying requires --apply and a new version name;
this program never edits prior output, original data, or the reviewed30 package.
Named review files are attestations, not cryptographic proof of provider identity.
The coordinator must verify actual execution before supplying approval evidence.
"""
import argparse
import copy
import hashlib
import importlib.util
import json
from pathlib import Path

BASE=Path(__file__).resolve().parent
ROOT=BASE.parent
REVIEWED=ROOT/'astra/resource30_corrections_20260923'
BASE_LEDGER_SHA='a289be149ad458068cd27db33d2e61f7302ad7e7d22ba6fc5179bc4bec961a03'
REVIEWED_MANIFEST_SHA='401653a8388b9ce80efef294b3a8898c35cace29b6f77da1c47b4cfc3a0fde34'
PROTECTED_PIN=BASE/'REVIEWED30_PROTECTED_INPUTS.json'
PROTECTED_PIN_SHA='da000ab5ff7a22c0a18d248f35270ecfc30614dcd4ca26997cc7f8e29fdd2ff6'
ORIGINAL_LEDGER={'path':'qedbench_certificate_availability_triage/validation/human_review_20260915/confirmed_release/ledger.json',
                 'sha256':'d8e4028ab7d844520167b49d2d21846e7fea3945c9fee395e8198c5997d6afc4'}
REQUIRED_REVIEWERS=('REVIEWER_A','REVIEWER_B','REVIEWER_C')
SELECTED30_FOLLOWON={'I023':'mse_3160594__ans3160616'}
SELECTED30_DOSSIER_FIELDS={'claim_quote','flaw','witness','explanation'}


def need(condition,message):
    if not condition: raise ValueError(message)

def sha(raw):return hashlib.sha256(raw).hexdigest()
def canonical(value):return json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()
def value_sha(value):return sha(canonical(value))
def jb(value):return (json.dumps(value,ensure_ascii=False,sort_keys=True,indent=2)+'\n').encode()
def location(value):
    path=(ROOT/value).resolve()
    need(path.is_relative_to(ROOT),'Evidence outside repository')
    return path

def bound(descriptor):
    path=location(descriptor['path'])
    need(not path.is_symlink(),'Evidence symlink refused')
    raw=path.read_bytes()
    need(sha(raw)==descriptor['sha256'],'Evidence hash drift: '+descriptor['path'])
    if 'bytes' in descriptor:need(len(raw)==descriptor['bytes'],'Evidence size drift')
    return raw

def previous_builder():
    spec=importlib.util.spec_from_file_location('reviewed30_frozen_builder',REVIEWED/'build_corrected_release.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module

def read_inputs():
    pin_raw=PROTECTED_PIN.read_bytes()
    need(sha(pin_raw)==PROTECTED_PIN_SHA,'Reviewed30 protected-input pin drift')
    pins=json.loads(pin_raw)
    for entry in pins['files']:bound(entry)
    ledger_raw=(REVIEWED/'release_v2/ledger.json').read_bytes()
    manifest_raw=(REVIEWED/'MANIFEST_v2.json').read_bytes()
    need(sha(ledger_raw)==BASE_LEDGER_SHA,'Base corrected ledger drift')
    need(sha(manifest_raw)==REVIEWED_MANIFEST_SHA,'Reviewed30 manifest drift')
    ledger=json.loads(ledger_raw);manifest=json.loads(manifest_raw)
    need(len(ledger)==425 and len({r['record_id'] for r in ledger})==425,'Base ledger identity/count mismatch')
    plan=json.loads((BASE/'REVIEW_PLAN.json').read_bytes())
    allowed={r['record_id']:r for r in plan['rows']}
    selected={r['record_id'] for r in manifest['rows']}
    need(len(allowed)==255 and len(selected)==30 and not selected.intersection(allowed),'Remaining255 partition differs')
    need(set(allowed)|selected=={r['record_id'] for r in ledger if r['release_status']=='RETAINED'},'Full285 partition differs')
    return ledger,manifest,allowed,pins

SOURCE_STATUSES={'AUTHOR_REVIEWED','RESOLVED_WITH_SOURCE_SUPPLEMENT',
                 'UNRESOLVED','CANNOT_DETERMINE','SOURCE_LIMITED','SOURCE_MISMATCH'}
UNRESOLVED_SOURCE_STATUSES={'UNRESOLVED','CANNOT_DETERMINE','SOURCE_LIMITED'}
RECORD_UPDATE_FIELDS={'public_supporting_evidence','source_correspondence','release_status'}

def checked_supporting_file(descriptor,reader):
    need(isinstance(descriptor,dict) and {'path','sha256'}<=set(descriptor)<= {'path','sha256','bytes'},
         'Invalid supporting-evidence file descriptor')
    need(isinstance(descriptor['path'],str) and bool(descriptor['path']),'Evidence path missing')
    digest=descriptor['sha256']
    need(isinstance(digest,str) and len(digest)==64 and all(c in '0123456789abcdef' for c in digest),
         'Invalid supporting-evidence SHA256')
    location(descriptor['path'])
    raw=reader(descriptor)
    need(sha(raw)==digest,'Supporting evidence hash drift: '+descriptor['path'])
    if 'bytes' in descriptor:need(len(raw)==descriptor['bytes'],'Supporting evidence size drift')
    return raw

def validate_public_supporting_evidence(evidence,rid,assignment,reader):
    """Check existing substantive attestations; never manufacture an approval."""
    need(isinstance(evidence,list),'Public supporting evidence must be a list')
    ids=set()
    for item in evidence:
        need(isinstance(item,dict) and set(item)=={'evidence_id','kind','label','path','sha256','accepted_by','approval_report'},
             'Unexpected public supporting evidence fields')
        eid=item['evidence_id']
        need(isinstance(eid,str) and eid.strip() and eid not in ids,'Invalid/duplicate evidence ID');ids.add(eid)
        need(item['kind'] in {'source_supplement','ancillary_computation'},'Unsupported evidence kind')
        need(isinstance(item['label'],str) and item['label'].strip(),'Supporting evidence label missing')
        need(isinstance(item['accepted_by'],str) and len(item['accepted_by'].strip())>=8,
             'Actual evidence-review identity required')
        checked_supporting_file({'path':item['path'],'sha256':item['sha256']},reader)
        report=json.loads(checked_supporting_file(item['approval_report'],reader))
        need(isinstance(report,dict),'Supporting approval report must be an object')
        need(report.get('qa_id')==assignment['qa_id'],'Evidence approval QA identity differs')
        need(report.get('record_id',rid)==rid,'Evidence approval record identity differs')
        need(isinstance(report.get('reviewed_at_utc'),str) and bool(report['reviewed_at_utc']),
             'Evidence approval review time missing')
        if item['kind']=='source_supplement':
            need(report.get('schema')=='astra-source-supplement-second-review/v1'
                 and report.get('decision')=='ACCEPT_CURRENT_PRIMARY_SOURCE_SUPPLEMENT_FOR_ACTIVE_DOSSIER',
                 'Source supplement lacks an accepted source review')
            need(report.get('record_id')==rid,'Source supplement review must identify its record')
            identity=report.get('actual_reviewer');reason=report.get('source_review')
            bindings=report.get('inputs')
            need(isinstance(bindings,dict) and bool(bindings),'Source approval evidence bindings missing')
            descriptors=list(bindings.values())
        else:
            need(report.get('schema')=='astra-computation-receipt-review/v1'
                 and report.get('decision')=='ACCEPT_SCOPED_SEPARATE_COMPUTATIONAL_EVIDENCE',
                 'Ancillary computation lacks an accepted computational review')
            identity=report.get('reviewer');reason=report.get('reason')
            descriptors=[report.get(key) for key in ('receipt','source','output')]
        need(identity==item['accepted_by'],'Evidence accepted_by differs from actual review identity')
        need(isinstance(reason,str) and len(reason.strip())>=30,'Substantive evidence review missing')
        for descriptor in descriptors:checked_supporting_file(descriptor,reader)
        need(any(location(d['path'])==location(item['path']) and d['sha256']==item['sha256'] for d in descriptors),
             'Approval does not directly bind the published supporting evidence')

def validate_source_correspondence(current):
    status=current.get('source_correspondence')
    if status is None:return
    need(isinstance(status,dict) and set(status)=={'status','reason','evidence_ids'},
         'Unexpected active source-correspondence fields')
    need(status['status'] in SOURCE_STATUSES,'Invalid active source-correspondence status')
    need(isinstance(status['reason'],str) and len(status['reason'].strip())>=20,
         'Substantive active source-correspondence reason required')
    refs=status['evidence_ids']
    need(isinstance(refs,list) and all(isinstance(x,str) and x for x in refs)
         and len(refs)==len(set(refs)),'Invalid/duplicate source evidence IDs')
    evidence={x['evidence_id']:x for x in current.get('public_supporting_evidence',[])}
    need(set(refs)<=set(evidence),'Active source status references missing public evidence')
    if status['status'] in {'RESOLVED_WITH_SOURCE_SUPPLEMENT','SOURCE_MISMATCH'}:
        need(any(evidence[eid]['kind']=='source_supplement' for eid in refs),
             'Source resolution or mismatch requires referenced approved source-supplement evidence')
    if status['status']=='SOURCE_MISMATCH':
        need(current.get('release_status')=='EXCLUDED','SOURCE_MISMATCH cannot remain retained')
    if status['status']=='AUTHOR_REVIEWED':
        need(not any(f['status'] in UNRESOLVED_SOURCE_STATUSES for f in current.get('source_correspondence_flags',[])),
             'Historical source flags require explicit source-supplement resolution, not AUTHOR_REVIEWED')

def active_source_state(record):
    """An explicit reviewed active status supersedes, but never deletes, old flags."""
    if record.get('source_correspondence') is not None:return copy.deepcopy(record['source_correspondence'])
    flags=record.get('source_correspondence_flags',[])
    if not flags:return None
    statuses={f['status'] for f in flags}
    state=next(s for s in ('UNRESOLVED','CANNOT_DETERMINE','SOURCE_LIMITED') if s in statuses)
    return {'status':state,'reason':'No separately reviewed active status supplied; preserved source flags remain applicable.',
            'evidence_ids':[]}

def validate_record_source_evidence(record,assignment,reader=None):
    """Reusable consumer gate for approved public evidence and active source state."""
    if reader is None:reader=bound
    need(assignment.get('record_id')==record['record_id'],'Source evidence assignment identity differs')
    if 'public_supporting_evidence' in record:
        validate_public_supporting_evidence(record['public_supporting_evidence'],record['record_id'],assignment,reader)
    validate_source_correspondence(record)

def validate_admission_transition(before,after,protected=()):
    """Structural admission check; evidence/consensus validation remains required."""
    need(before['record_id']==after['record_id'],'Admission record identity differs')
    old,new=before.get('release_status'),after.get('release_status')
    need(old in {'RETAINED','EXCLUDED'} and new in {'RETAINED','EXCLUDED'},'Unsupported admission status')
    state=(after.get('source_correspondence') or {}).get('status')
    if state=='SOURCE_MISMATCH':need(new=='EXCLUDED','SOURCE_MISMATCH cannot remain retained')
    if old==new:return
    need(old=='RETAINED' and new=='EXCLUDED','Only RETAINED to EXCLUDED is permitted; restoration refused')
    need(before['record_id'] not in protected,'Original15 or selected30 admission is protected')
    need(state=='SOURCE_MISMATCH','New withdrawal requires explicit SOURCE_MISMATCH')

def original15_record_ids(base_ledger):
    initial={r['record_id']:r for r in json.loads(bound(ORIGINAL_LEDGER))}
    base={r['record_id']:r for r in base_ledger}
    need(set(initial)==set(base),'Original15 ledger identity partition differs')
    result=sorted(rid for rid in initial if initial[rid]!=base[rid])
    need(len(result)==15,'Original correction cohort must contain exactly15 records')
    return result

def admission_roster(before,after,corrected_record_ids):
    """Derive current membership and diagnostic roles after exact consensus replay.

    This pure projection is not approval and does not validate evidence bytes.
    All corrected IDs remain execution targets; excluded IDs are diagnostic only.
    """
    old={r['record_id']:r for r in before};new={r['record_id']:r for r in after}
    need(len(old)==len(before) and len(new)==len(after),'Duplicate admission record IDs')
    need(list(old)==list(new),'Admission ledger identities/order changed')
    for rid in old:validate_admission_transition(old[rid],new[rid])
    historical_retained=sorted(rid for rid in old if old[rid]['release_status']=='RETAINED')
    historical_excluded=sorted(set(old)-set(historical_retained))
    retained=sorted(rid for rid in new if new[rid]['release_status']=='RETAINED')
    excluded=sorted(set(new)-set(retained))
    withdrawn=sorted(set(historical_retained)-set(retained))
    corrected=sorted(set(corrected_record_ids))
    need(set(corrected)<=set(historical_retained),'Corrected execution roster outside historical retained records')
    need(set(withdrawn)<=set(corrected),'Withdrawal absent from exact correction roster')
    return {'schema':'current-resource-admission/v1',
        'historical_retained_record_ids':historical_retained,'historical_excluded_record_ids':historical_excluded,
        'current_retained_record_ids':retained,'current_excluded_record_ids':excluded,
        'newly_excluded_record_ids':withdrawn,'current_retained_ids_sha256':value_sha(retained),
        'counts':{'total_rows':len(new),'historical_retained':len(historical_retained),
            'historical_excluded':len(historical_excluded),'current_retained':len(retained),
            'current_excluded':len(excluded),'newly_excluded':len(withdrawn)},
        'corrected_execution_record_ids':corrected,
        'current_retained_corrected_record_ids':sorted(set(corrected)&set(retained)),
        'diagnostic_only_corrected_record_ids':sorted(set(corrected)&set(excluded)),
        'diagnostic_only_excluded_from_current_metrics':True,
        'execution_policy':'Execute every corrected ID in each reported configuration; excluded corrected IDs are separately labeled non-scored diagnostics, never current benchmark members.'}

def validate_flags(flags,reader=bound):
    need(isinstance(flags,list),'Source-correspondence flags must be a list')
    ids=set()
    for flag in flags:
        need(set(flag)=={'flag_id','status','reason','source_lines','evidence'},'Unexpected source flag fields')
        need(isinstance(flag['flag_id'],str) and flag['flag_id'] and flag['flag_id'] not in ids,'Invalid/duplicate flag ID')
        ids.add(flag['flag_id'])
        need(flag['status'] in {'UNRESOLVED','CANNOT_DETERMINE','SOURCE_LIMITED'},'This builder only adds unresolved source flags')
        need(isinstance(flag['reason'],str) and len(flag['reason'].strip())>=20,'Substantive flag reason required')
        need(isinstance(flag['source_lines'],list) and bool(flag['source_lines']),'Flag must identify frozen source lines')
        need(isinstance(flag['evidence'],list) and bool(flag['evidence']),'Flag must bind source evidence')
        for entry in flag['evidence']:reader(entry)

def selected30_revision(ledger,dossier,selected,reader=None):
    """Read the narrow versioned opt-in; this is never correction approval."""
    if reader is None:reader=bound
    descriptor=dossier.get('selected30_revision')
    if descriptor is None:return None
    policy=json.loads(checked_supporting_file(descriptor,reader))
    need(isinstance(policy,dict) and set(policy)=={'schema','base_ledger_sha256','reviewed_manifest',
        'protected_inputs','prospective_packet_version','revisions'},'Malformed selected30 revision descriptor')
    need(policy['schema']=='selected30-dossier-only-followon/v1','Unknown selected30 revision schema')
    need(policy['base_ledger_sha256']==BASE_LEDGER_SHA,'Selected30 revision base ledger differs')
    manifest_descriptor=policy['reviewed_manifest']
    need(manifest_descriptor=={'path':str((REVIEWED/'MANIFEST_v2.json').relative_to(ROOT)),
                              'sha256':REVIEWED_MANIFEST_SHA},'Selected30 revision must bind exact old reviewed manifest')
    manifest=json.loads(checked_supporting_file(manifest_descriptor,reader))
    pin_descriptor=policy['protected_inputs']
    need(pin_descriptor=={'path':str(PROTECTED_PIN.relative_to(ROOT)),
                         'sha256':PROTECTED_PIN_SHA},'Selected30 protected-input pin differs')
    pins=json.loads(checked_supporting_file(pin_descriptor,reader))
    need(len(pins['files'])==468,'Selected30 protected-input roster differs')
    for item in pins['files']:checked_supporting_file(item,reader)
    version=policy['prospective_packet_version']
    need(isinstance(version,str) and version.isidentifier() and version.startswith('candidate_')
         and version!='candidate_v2','A distinct prospective candidate_ packet version is required')
    rows={row['record_id']:row for row in manifest['rows']}
    need(len(rows)==30 and set(rows)==set(selected),'Selected30 opt-in roster differs from old manifest')
    entries=policy['revisions']
    need(isinstance(entries,list) and len(entries)==1,'Only the explicit I023 follow-on is supported')
    records={r['record_id']:r for r in ledger};out={}
    for entry in entries:
        need(isinstance(entry,dict) and set(entry)=={'packet_id','record_id','old_manifest_row_sha256',
            'before_record_sha256','dossier_entry_sha256','final_record_before_consensus_metadata_sha256'},
            'Malformed selected30 exact revision entry')
        pid,rid=entry['packet_id'],entry['record_id']
        need(SELECTED30_FOLLOWON.get(pid)==rid and rid in rows and rows[rid]['packet_id']==pid,
             'Selected30 opt-in is restricted to exact I023 identity')
        need(value_sha(rows[rid])==entry['old_manifest_row_sha256'],'Selected30 old manifest row digest differs')
        need(value_sha(records[rid])==entry['before_record_sha256'],'Selected30 old record digest differs')
        need(records[rid]['release_status']=='RETAINED','Selected30 revision cannot alter admission')
        for key in ('dossier_entry_sha256','final_record_before_consensus_metadata_sha256'):
            digest=entry[key]
            need(isinstance(digest,str) and len(digest)==64 and all(c in '0123456789abcdef' for c in digest),
                 'Invalid selected30 revision digest')
        out[rid]=copy.deepcopy(entry)
    need(set(out)=={r['record_id'] for r in dossier['records'] if r['record_id'] in selected},
         'Selected30 opt-in and actual dossier revision IDs differ')
    return {'descriptor':copy.deepcopy(descriptor),'prospective_packet_version':version,'revisions':out}

def selected30_content(before,after,revision,finalized=False):
    """Bind the exact new dossier while excluding all source/formal/admission edits."""
    expected=copy.deepcopy(before)
    expected['current_fields']=copy.deepcopy(after['current_fields'])
    expected['corrected_scope_metadata']=copy.deepcopy(after.get('corrected_scope_metadata',{}))
    old_fields=before['current_fields'];new_fields=expected['current_fields']
    need(set(old_fields)==set(new_fields) and
         {k for k in old_fields if old_fields[k]!=new_fields[k]}==SELECTED30_DOSSIER_FIELDS,
         'Selected30 revision requires exactly four pinned dossier fields; source/problem unchanged')
    need(new_fields['claim_quote']=='I believe the answer is yes.','I023 follow-on requires the exact line1 quote')
    old_scope=before.get('corrected_scope_metadata',{});new_scope=expected['corrected_scope_metadata']
    need(set(old_scope)==set(new_scope) and {k for k in old_scope if old_scope[k]!=new_scope[k]}=={'quote_status'},
         'Selected30 revision permits only the pinned quote_status scope update')
    need(value_sha(expected)==revision['final_record_before_consensus_metadata_sha256'],
         'Selected30 final dossier record digest differs')
    administrative={'audit','audit_provenance','correction','correction_provenance','exact_checker',
        'witness_action','witness_action_provenance','extension_correction_history',
        'human_approval_of_current_artifact','revised_artifact_requires_new_human_review','corrected_release'} if finalized else set()
    need({k:v for k,v in after.items() if k not in administrative}==
         {k:v for k,v in expected.items() if k not in administrative},
         'Selected30 source/formal/admission or unrelated record mutation refused')
    return value_sha(expected)

def change_records(ledger,dossier,lean,selected,allowed,reader=None):
    """Pure change preparation; no approval fabrication and no filesystem output."""
    if reader is None:reader=bound
    for overlay in (dossier,lean):
        need(overlay.get('base_ledger_sha256')==BASE_LEDGER_SHA,'Overlay must bind current corrected ledger')
        need(isinstance(overlay.get('overlay_version'),str) and overlay['overlay_version'],'Versioned overlay required')
    by_id={r['record_id']:r for r in ledger}
    followon=selected30_revision(ledger,dossier,selected,reader)
    specifications={}
    revised=copy.deepcopy(ledger);new_by_id={r['record_id']:r for r in revised}
    for entry in dossier['records']:
        rid=entry['record_id']
        need(rid not in specifications,'Duplicate dossier record')
        opted=followon is not None and rid in followon['revisions']
        need((rid in allowed and rid not in selected) or opted,
             'Dossier correction affects selected30 or unassigned record; new packet version required')
        if opted:
            need(value_sha(entry)==followon['revisions'][rid]['dossier_entry_sha256'],
                 'Selected30 dossier delta differs from exact opt-in')
            need(not entry.get('source_correspondence_flags') and not entry.get('record_field_updates'),
                 'Selected30 opt-in permits dossier text only, not source evidence or admission updates')
        need(value_sha(by_id[rid])==entry['before_record_sha256'],'Before-record digest differs: '+rid)
        need(not RECORD_UPDATE_FIELDS.intersection(entry),'Active ledger fields require guarded record_field_updates')
        need(bool(entry.get('field_changes') or entry.get('scope_updates') or entry.get('source_correspondence_flags')
                  or entry.get('record_field_updates')),'Empty dossier proposal')
        current=new_by_id[rid];seen=set()
        for patch in entry.get('field_changes',[]):
            field=patch['field']
            need(field in {'claim_quote','witness','flaw','explanation'},'Original source/problem or unsupported field mutation refused')
            need(field not in seen,'Duplicate field patch');seen.add(field)
            need(isinstance(patch['old_value'],str) and isinstance(patch['new_value'],str),'Text corrections require strings')
            need(current['current_fields'].get(field)==patch['old_value'],'Old current field mismatch')
            need(value_sha(patch['old_value'])==patch['old_value_sha256'],'Old field digest differs')
            need(value_sha(patch['new_value'])==patch['new_value_sha256'],'New field digest differs')
            need(patch['old_value']!=patch['new_value'],'No-op correction refused')
            need(isinstance(patch['reason'],str) and patch['reason'].strip(),'Correction reason missing')
            current['current_fields'][field]=patch['new_value']
        scopes=current.setdefault('corrected_scope_metadata',{}) if entry.get('scope_updates') else current.get('corrected_scope_metadata',{})
        for update in entry.get('scope_updates',[]):
            key=update['field']
            need(isinstance(key,str) and key and key not in seen,'Invalid/duplicate scope update');seen.add(key)
            need(scopes.get(key)==update['old_value'] and value_sha(update['old_value'])==update['old_value_sha256'],'Old scope value/digest differs')
            need(value_sha(update['new_value'])==update['new_value_sha256'] and isinstance(update['new_value'],str),'New scope digest/type differs')
            need(update['old_value']!=update['new_value'],'No-op scope update refused')
            scopes[key]=update['new_value']
        flags=entry.get('source_correspondence_flags',[])
        validate_flags(flags,reader)
        if flags:
            existing=current.setdefault('source_correspondence_flags',[])
            need(not {x['flag_id'] for x in existing}.intersection(x['flag_id'] for x in flags),'Existing unresolved flag cannot be silently replaced')
            existing.extend(copy.deepcopy(flags))
        record_seen=set()
        updates=entry.get('record_field_updates',[])
        need(isinstance(updates,list),'record_field_updates must be a list')
        for update in updates:
            need(isinstance(update,dict) and set(update)=={'field','old_value','old_value_sha256','new_value','new_value_sha256','reason'},
                 'Unexpected guarded record update fields')
            field=update['field']
            need(field in RECORD_UPDATE_FIELDS,'Unsupported guarded record field')
            need(field not in record_seen,'Duplicate guarded record update');record_seen.add(field)
            need(current.get(field)==update['old_value'] and value_sha(update['old_value'])==update['old_value_sha256'],
                 'Old guarded record value/digest differs')
            need(value_sha(update['new_value'])==update['new_value_sha256'],'New guarded record digest differs')
            need(update['old_value']!=update['new_value'],'No-op guarded record update refused')
            need(isinstance(update['reason'],str) and len(update['reason'].strip())>=20,'Substantive guarded update reason required')
            current[field]=copy.deepcopy(update['new_value'])
        if 'source_correspondence' in record_seen:
            need(current['source_correspondence'] is not None,'Active source status cannot be silently removed')
        validate_admission_transition(by_id[rid],current)
        if 'release_status' in record_seen:
            validate_admission_transition(by_id[rid],current,set(selected)|set(original15_record_ids(ledger)))
        validate_record_source_evidence(current,allowed[rid] if not opted else
            {'record_id':rid,'qa_id':followon['revisions'][rid]['packet_id']},reader)
        specifications[rid]={'record_id':rid,'before_record_sha256':value_sha(by_id[rid]),'dossier_entry':entry,'lean_correction_sha256':None}
        if opted:
            selected30_content(by_id[rid],current,followon['revisions'][rid])
            specifications[rid]['selected30_dossier_revision']={
                'descriptor':followon['descriptor'],'prospective_packet_version':followon['prospective_packet_version'],
                'revision':followon['revisions'][rid]}
    for correction in lean['corrections']:
        consumers={r['record_id'] for r in ledger if r.get('lean_path')==correction['original_path'] and r.get('lean_sha256')==correction['original_sha256']}
        listed=[r['record_id'] for r in correction['affected_records']]
        need(bool(consumers) and consumers==set(listed) and len(listed)==len(set(listed)),'Shared certificate consumer coverage incomplete')
        need(not consumers.intersection(selected),'Shared Lean change affects selected30; new human packet version required')
        need(consumers.issubset(allowed),'Lean change affects record outside remaining255')
        digest=value_sha(correction)
        for rid in consumers:
            spec=specifications.setdefault(rid,{'record_id':rid,'before_record_sha256':value_sha(by_id[rid]),'dossier_entry':None,'lean_correction_sha256':None})
            need(spec['lean_correction_sha256'] is None,'Duplicate Lean correction record')
            spec['lean_correction_sha256']=digest
    need(bool(specifications),'No approved changes supplied; no no-op extension produced')
    # The already validated helper checks actual file bytes, compilation success,
    # printed types, exact kernel audit events, and every shared-file consumer.
    previous_builder().apply_lean(revised,lean)
    for rid,spec in specifications.items():
        if by_id[rid]['release_status']!=new_by_id[rid]['release_status']:
            spec['admission_change']={
                'before_release_status':by_id[rid]['release_status'],
                'after_release_status':new_by_id[rid]['release_status'],
                'final_record_before_consensus_metadata_sha256':value_sha(new_by_id[rid])}
        spec['change_sha256']=value_sha(spec)
    return revised,specifications

def prepare_consensus_specifications(base_ledger,revised,extension_specifications):
    """Bind all original15 to the final proposed record, including overlaps."""
    initial={r['record_id']:r for r in json.loads(bound(ORIGINAL_LEDGER))}
    base={r['record_id']:r for r in base_ledger};final={r['record_id']:r for r in revised}
    need(set(initial)==set(base)==set(final),'Consensus ledger identity partition differs')
    original15=sorted(rid for rid in initial if initial[rid]!=base[rid])
    need(len(original15)==15,'Original correction cohort must contain exactly15 records')
    for rid in original15:validate_admission_transition(base[rid],final[rid],original15)
    specifications=copy.deepcopy(extension_specifications)
    for rid in original15:
        spec=specifications.setdefault(rid,{'record_id':rid,'before_record_sha256':value_sha(base[rid]),
                                           'dossier_entry':None,'lean_correction_sha256':None})
        spec.pop('change_sha256',None)
        spec['original15_final_review']={
            'original_ledger_sha256':ORIGINAL_LEDGER['sha256'],
            'original_before_record_sha256':value_sha(initial[rid]),
            'base_corrected_record_sha256':value_sha(base[rid]),
            'final_record_before_consensus_metadata_sha256':value_sha(final[rid]),
            'also_changed_by_extension':rid in extension_specifications}
        spec['change_sha256']=value_sha(spec)
    context={'original_ledger':copy.deepcopy(ORIGINAL_LEDGER),'base_corrected_ledger_sha256':BASE_LEDGER_SHA,
        'reviewed30_manifest_sha256':REVIEWED_MANIFEST_SHA,'record_ids':original15,
        'final_specifications_sha256':value_sha({rid:specifications[rid] for rid in original15})}
    return specifications,context

def validate_approvals(specifications,approvals,allowed=None,reader=bound,original15_context=None):
    """Require three independently executed, exact final-correction reviews."""
    need(approvals.get('schema')=='all-three-correction-approvals/v1','All-three approval schema required; legacy two-review approvals are insufficient')
    need(approvals.get('base_ledger_sha256')==BASE_LEDGER_SHA,'Approvals bind wrong base ledger')
    need(isinstance(approvals.get('approval_version'),str) and approvals['approval_version'],'Versioned approvals required')
    need(approvals.get('required_reviewers')==list(REQUIRED_REVIEWERS),'All three named owners are required')
    if original15_context is not None:
        need(approvals.get('original15')==original15_context,'Original15 final-record consensus context differs')
    rows=approvals['records']
    need(len(rows)==3*len(specifications) and {r['record_id'] for r in rows}==set(specifications),
         'Every changed record needs exactly three independent approvals')
    result={rid:{'record_id':rid,'change_sha256':spec['change_sha256'],'required_reviewers':list(REQUIRED_REVIEWERS),'reviews':{}}
            for rid,spec in specifications.items()}
    for approval in rows:
        required={'record_id','before_record_sha256','change_sha256','reviewer_owner','actual_reviewer_identity',
                  'execution_context','decision','reason','reviewed_at_utc','independent_verification','review_report'}
        need(set(approval)==required,'Unexpected or missing all-three approval fields')
        rid=approval['record_id'];spec=specifications[rid];owner=approval['reviewer_owner']
        need(owner in REQUIRED_REVIEWERS and owner not in result[rid]['reviews'],'Missing or duplicate named consensus owner')
        need(approval['decision']=='APPROVE_CORRECTION','Correction not approved')
        need(approval['change_sha256']==spec['change_sha256'],'Approval does not bind concrete changed bytes')
        need(approval['before_record_sha256']==spec['before_record_sha256'],'Approval before record differs')
        need(isinstance(approval['actual_reviewer_identity'],str) and len(approval['actual_reviewer_identity'].strip())>=8,'Actual reviewer execution identity missing')
        need(isinstance(approval['execution_context'],str) and len(approval['execution_context'].strip())>=8,'Distinct execution context missing')
        need(isinstance(approval['reason'],str) and len(approval['reason'].strip())>=30,'Substantive second-review reason missing')
        need(isinstance(approval['reviewed_at_utc'],str) and approval['reviewed_at_utc'],'Review time missing')
        independent=approval['independent_verification']
        need(isinstance(independent,dict) and set(independent)=={
            'personally_checked_final_correction','relied_on_other_approvals','basis','prior_own_review_reports','exposure_notes'},
            'Independent-verification declaration missing or malformed')
        need(independent['personally_checked_final_correction'] is True and independent['relied_on_other_approvals'] is False,
             'Independent verification of final source, witness and formal meaning required')
        need(independent['basis'] in {'FULL_FINAL_REVIEW','PRIOR_OWN_REVIEW_PLUS_FINAL_DELTA'},'Unknown independent review basis')
        need(isinstance(independent['exposure_notes'],str) and len(independent['exposure_notes'].strip())>=8,
             'Actual review exposure disclosure required')
        need(isinstance(independent['prior_own_review_reports'],list),'Prior-own-review bindings must be a list')
        if independent['basis']=='PRIOR_OWN_REVIEW_PLUS_FINAL_DELTA':
            need(bool(independent['prior_own_review_reports']),'Prior own full review must be bound')
        for descriptor in independent['prior_own_review_reports']:checked_supporting_file(descriptor,reader)
        report=json.loads(checked_supporting_file(approval['review_report'],reader))
        signed={k:v for k,v in approval.items() if k!='review_report'}
        need(isinstance(report,dict) and signed in report.get('approvals',[]),'Pinned named review does not contain this exact approval')
        result[rid]['reviews'][owner]=copy.deepcopy(approval)
    for rid,row in result.items():
        need(set(row['reviews'])==set(REQUIRED_REVIEWERS),'Every correction requires all three named owners')
        need(len({r['execution_context'] for r in row['reviews'].values()})==3,
             'Three owner labels cannot reuse one execution context')
        need(len({r['actual_reviewer_identity'] for r in row['reviews'].values()})==3,
             'Three owner labels cannot reuse one actual reviewer identity')
    return result

def finalize_records(original,revised,specifications,approvals,version):
    old_by_id={r['record_id']:r for r in original}
    need([r['record_id'] for r in revised]==[r['record_id'] for r in original],'Record identities/order changed')
    protected=original15_record_ids(original) if any(old_by_id[r['record_id']]['release_status']!=r['release_status'] for r in revised) else ()
    for record in revised:
        rid=record['record_id'];old=old_by_id[rid]
        validate_admission_transition(old,record,protected)
        if old['release_status']!=record['release_status']:
            need(rid in specifications and rid in approvals,'Withdrawal lacks exact approved correction')
            need(specifications[rid].get('admission_change')=={
                'before_release_status':old['release_status'],'after_release_status':record['release_status'],
                'final_record_before_consensus_metadata_sha256':value_sha(record)},
                'Withdrawal final row differs from exact admission specification')
        if old['release_status']=='EXCLUDED':need(old==record,'Previously excluded record is immutable')
    for record in revised:
        rid=record['record_id']
        if rid not in specifications:continue
        old=old_by_id[rid]
        history={k:record.pop(k) for k in ('audit','audit_provenance','correction','correction_provenance','exact_checker','witness_action','witness_action_provenance') if k in record}
        record.setdefault('extension_correction_history',[]).append({
            'base_ledger_sha256':BASE_LEDGER_SHA,'before_record_sha256':value_sha(old),
            'prior_audit_fields':history,'prior_corrected_release':copy.deepcopy(old.get('corrected_release')),
            'prior_build_record':copy.deepcopy(old.get('build_record')),
            'prior_release_status':old['release_status'],
            'prior_source_correspondence':copy.deepcopy(old.get('source_correspondence')),
            'prior_public_supporting_evidence':copy.deepcopy(old.get('public_supporting_evidence')),
            'change_sha256':specifications[rid]['change_sha256'],'all_three_reviews':approvals[rid]})
        record['human_approval_of_current_artifact']='NOT_ESTABLISHED_FOR_CORRECTED_VERSION'
        record['revised_artifact_requires_new_human_review']=True
        record['corrected_release']={'version':version,'base_ledger_sha256':BASE_LEDGER_SHA,
            'change_sha256':specifications[rid]['change_sha256'],'human_review_status':'AWAITING_NEW_REVIEW',
            'author_side_consensus':'ALL_THREE_APPROVED_EXACT_FINAL_CHANGE','automated_build_is_human_approval':False}
    immutable=('historical_inventory','historical_source_fields','historical_human_reviews','historical_human_all_yes',
               'historical_human_unambiguous_approval','source_packet','original_record_id','assignment_group')
    for old,new in zip(original,revised):
        need(all(old.get(k)==new.get(k) for k in immutable),'Historical/source field altered')
        need(all(old['current_fields'].get(k)==new['current_fields'].get(k) for k in ('problem','source_context','complete_source')),'Original source/problem changed')
        flags=old.get('source_correspondence_flags',[])
        need(new.get('source_correspondence_flags',[])[:len(flags)]==flags,'Historical source flags altered or removed')
    return revised

def alignment(original,revised,manifest,followon=None,finalized=False):
    before={r['record_id']:r for r in original};after={r['record_id']:r for r in revised};rows=[]
    revisions=followon['revisions'] if followon is not None else {}
    for row in manifest['rows']:
        rid=row['record_id']
        changed=before[rid]!=after[rid]
        need(not changed or rid in revisions,
             'Selected30 ledger record altered: '+rid+'; new human packet version required')
        if rid in revisions:
            need(changed,'Selected30 opt-in must produce its exact dossier change')
            prepared_sha=selected30_content(before[rid],after[rid],revisions[rid],finalized)
        for asset in row['evidence_files']:
            bound({'path':str((REVIEWED/'candidate_v2'/asset['path']).relative_to(ROOT)),**{k:asset[k] for k in ('sha256','bytes')}})
        bound({'path':str((REVIEWED/'candidate_v2'/row['packet_file']).relative_to(ROOT)),'sha256':row['packet_sha256']})
        item={'packet_id':row['packet_id'],'record_id':rid,'record_unchanged':not changed,
                     'before_record_sha256':value_sha(before[rid]),'after_record_sha256':value_sha(after[rid]),
                     'input_sha256':row['input_sha256'],'packet_sha256':row['packet_sha256'],'lean_sha256':row['lean_sha256']}
        if rid in revisions:
            item.update({'old_packet_current':False,'requires_new_packet':True,
                'final_record_before_consensus_metadata_sha256':prepared_sha,
                'prospective_packet_version':followon['prospective_packet_version']})
        rows.append(item)
    if followon is not None:
        need(set(revisions)=={row['record_id'] for row in rows if not row['record_unchanged']},
             'Selected30 alignment revision roster differs')
        return {'schema':'extension-reviewed30-alignment/v2','reviewed_manifest_sha256':REVIEWED_MANIFEST_SHA,
            'selected30_record_count':30,'all_records_and_assets_unchanged':False,
            'historical_assets_unchanged':True,'old_packet_current':False,
            'packet_status':'OLD_PACKET_NOT_CURRENT_REPLACEMENT_REQUIRED',
            'revised_selected_record_ids':sorted(revisions),
            'required_new_packet_version':followon['prospective_packet_version'],
            'selected30_revision_descriptor':followon['descriptor'],'rows':rows,
            'meaning':'All prior reviewed30 asset bytes remain historical and intact. The explicitly listed dossier changed; '
                'candidate_v2 must not be published as the current human package. A separately validated new packet version '
                'is required. Corrected-ledger consensus, census and benchmarks do not depend on packet delivery or human approval.'}
    return {'schema':'extension-reviewed30-alignment/v1','reviewed_manifest_sha256':REVIEWED_MANIFEST_SHA,
        'selected30_record_count':30,'all_records_and_assets_unchanged':True,'rows':rows,
        'meaning':'The reviewed candidate_v2 remains the exact30-artifact package under its existing manifest. '
                  'The global extension changes only remaining255 records. This alignment is not additional semantic approval or human review.'}

def require_current_old_reviewed30_package(verified_consensus):
    """Gate reuse of candidate_v2 as CURRENT, after canonical consensus replay.

    This does not gate ledger/census/benchmark consumers and does not validate a
    replacement package. A new version requires its own full packet validation.
    """
    need(verified_consensus.get('schema')=='copeer-all-three-correction-consensus/v1'
         and verified_consensus.get('status')=='ALL_THREE_APPROVE_EXACT_FINAL_CORRECTIONS',
         'Pass the canonically verified correction consensus')
    state=verified_consensus.get('selected30_packet_alignment')
    need(state is None or state.get('old_packet_current') is True,
         'Old reviewed30 packet is not current; validate and publish the required new packet version')
    return {'reviewed_manifest_sha256':REVIEWED_MANIFEST_SHA,'old_packet_current':True,
            'meaning':'Reuse of the exact historical manifest as current is structurally aligned; no human approval is created.'}

def build(dossier_path,lean_path,approval_path,version):
    need(version.isidentifier() and version.startswith('extension_'),'Use a simple new extension_ version name')
    original,manifest,allowed,pins=read_inputs()
    inputs={}
    def read(path):
        path=Path(path).resolve();need(path.is_relative_to(BASE),'Accepted overlay/approval must reside in remaining255 directory')
        raw=path.read_bytes();inputs[str(path.relative_to(ROOT))]={'sha256':sha(raw),'bytes':len(raw)};return json.loads(raw)
    dossier,lean,approvals=read(dossier_path),read(lean_path),read(approval_path)
    revised,extension_specs=change_records(original,dossier,lean,{r['record_id'] for r in manifest['rows']},allowed)
    followon=selected30_revision(original,dossier,{r['record_id'] for r in manifest['rows']})
    specifications,original15_context=prepare_consensus_specifications(original,revised,extension_specs)
    accepted=validate_approvals(specifications,approvals,allowed,original15_context=original15_context)
    final_before_metadata={r['record_id']:value_sha(r) for r in revised if r['record_id'] in specifications}
    finalize_records(original,revised,{rid:specifications[rid] for rid in extension_specs},accepted,version)
    matched=alignment(original,revised,manifest,followon,finalized=True)
    admission=admission_roster(original,revised,specifications)
    ledger_raw=jb(revised);dest=BASE/version
    active={r['record_id']:active_source_state(r) for r in revised if active_source_state(r) is not None}
    receipt={'schema':'remaining255-approved-extension/v1','version':version,'base_ledger_sha256':BASE_LEDGER_SHA,
        'ledger_sha256':sha(ledger_raw),'total_rows':len(revised),'changed_record_ids':sorted(extension_specs),
        'admission':admission,
        'all_corrected_record_ids':sorted(specifications),
        'inputs':inputs,'review_plan_sha256':sha((BASE/'REVIEW_PLAN.json').read_bytes()),
        'protected30_pin_sha256':sha(PROTECTED_PIN.read_bytes()),'reviewed30_manifest_sha256':REVIEWED_MANIFEST_SHA,
        'builder_sha256':sha(Path(__file__).read_bytes()),'recordwise30_alignment_sha256':sha(jb(matched)),
        'unchanged30_package_validity':'Exact byte/record alignment only; original team review gates remain independently required.',
        'historical_source_correspondence_flags':{r['record_id']:r['source_correspondence_flags'] for r in revised if r.get('source_correspondence_flags')},
        'active_source_correspondence':active,
        'active_unresolved_source_record_ids':sorted(rid for rid,state in active.items() if state['status'] in UNRESOLVED_SOURCE_STATUSES),
        'active_source_mismatch_record_ids':sorted(rid for rid,state in active.items() if state['status']=='SOURCE_MISMATCH'),
        'unresolved_source_flags':{r['record_id']:r['source_correspondence_flags'] for r in revised
            if r.get('source_correspondence_flags') and active[r['record_id']]['status'] in UNRESOLVED_SOURCE_STATUSES},
        'public_supporting_evidence':{r['record_id']:r['public_supporting_evidence'] for r in revised if r.get('public_supporting_evidence')},
        'named_approvals_bind_exact_changes':True,'all_three_independent_reviews_required':True,
        'human_approval_created':False,'release_zip_created':False,
        'approval_identity_note':'Pinned substantive named-review attestations; actual execution is verified by the coordinator, not inferred from labels.'}
    specification_raw=jb(specifications)
    approval_rel=str(Path(approval_path).resolve().relative_to(ROOT))
    reports={}
    for record in accepted.values():
        for approval in record['reviews'].values():
            for descriptor in [approval['review_report'],*approval['independent_verification']['prior_own_review_reports']]:
                reports[(descriptor['path'],descriptor['sha256'])]={'path':descriptor['path'],'sha256':descriptor['sha256']}
    consensus={'schema':'copeer-all-three-correction-consensus/v1',
        'status':'ALL_THREE_APPROVE_EXACT_FINAL_CORRECTIONS','version':version,
        'required_reviewers':list(REQUIRED_REVIEWERS),'corrected_record_ids':sorted(specifications),
        'original15_record_ids':original15_context['record_ids'],'extension_record_ids':sorted(extension_specs),
        'base_ledger_sha256':BASE_LEDGER_SHA,'original15':original15_context,
        'admission':admission,
        'ledger_sha256':sha(ledger_raw),
        'specifications':{'path':str((dest/'CHANGE_SPECIFICATIONS.json').relative_to(ROOT)),'sha256':sha(specification_raw)},
        'approval_file':{'path':approval_rel,'sha256':inputs[approval_rel]['sha256']},
        'replay_inputs':{key:{'path':str(Path(path).resolve().relative_to(ROOT)),
            'sha256':inputs[str(Path(path).resolve().relative_to(ROOT))]['sha256']}
            for key,path in (('dossier_overlay',dossier_path),('lean_overlay',lean_path),('approvals',approval_path))},
        'review_reports':[reports[key] for key in sorted(reports)],
        'records':{rid:{**accepted[rid],'before_record_sha256':specifications[rid]['before_record_sha256'],
            'final_record_before_consensus_metadata_sha256':final_before_metadata[rid],
            'final_release_status':next(r['release_status'] for r in revised if r['record_id']==rid)} for rid in sorted(specifications)},
        'builder_sha256':sha(Path(__file__).read_bytes()),
        'independence_meaning':'Each named owner attests to personally checking final source, witness and formal meaning. Prior own full review plus a checked final delta is allowed and disclosed. Session identity is not model diversity.',
        'execution_identity_limit':'Reports are content-bound attestations; the coordinator independently verifies actual execution. No approval is inferred from primary-review labels, tool success or owner templates.',
        'human_approval_created':False}
    if followon is not None:
        receipt['unchanged30_package_validity']='Prior bytes preserved as history; selected dossier changed and old packet is not current.'
        receipt['selected30_packet_alignment']=matched
        consensus['selected30_packet_alignment']=matched
    receipt['consensus_sha256']=sha(jb(consensus))
    return {dest/'ledger.json':ledger_raw,dest/'PROVENANCE.json':jb(receipt),
            dest/'REVIEWED30_ALIGNMENT.json':jb(matched),dest/'CHANGE_SPECIFICATIONS.json':specification_raw,
            dest/'CONSENSUS.json':jb(consensus)},receipt

def verify_consensus_receipt(descriptor,ledger_descriptor=None):
    """Read-only replay gate for bank staging or later benchmark dispatch."""
    raw=checked_supporting_file(descriptor,bound);consensus=json.loads(raw)
    need(consensus.get('schema')=='copeer-all-three-correction-consensus/v1'
         and consensus.get('status')=='ALL_THREE_APPROVE_EXACT_FINAL_CORRECTIONS','Final all-three consensus receipt required')
    need(consensus.get('required_reviewers')==list(REQUIRED_REVIEWERS),'Consensus reviewer set differs')
    replay=consensus.get('replay_inputs')
    need(isinstance(replay,dict) and set(replay)=={'dossier_overlay','lean_overlay','approvals'},'Consensus replay inputs missing')
    for item in replay.values():checked_supporting_file(item,bound)
    outputs,receipt=build(location(replay['dossier_overlay']['path']),location(replay['lean_overlay']['path']),
                          location(replay['approvals']['path']),consensus['version'])
    expected_consensus=next(value for path,value in outputs.items() if path.name=='CONSENSUS.json')
    need(raw==expected_consensus,'Consensus receipt differs from exact builder replay')
    for path,expected in outputs.items():
        need(path.read_bytes()==expected,'Published extension artifact differs from consensus replay: '+str(path))
    if ledger_descriptor is not None:
        ledger_raw=checked_supporting_file(ledger_descriptor,bound)
        need(sha(ledger_raw)==consensus['ledger_sha256'],'Accepted ledger differs from consensus')
    return consensus

def apply(outputs):
    need(all(p.resolve().is_relative_to(BASE.resolve()) for p in outputs),'Output escapes extension directory')
    need(all(not p.exists() for p in outputs),'Extension output exists; use a new explicit version')
    consensus_entries=[raw for path,raw in outputs.items() if path.name=='CONSENSUS.json']
    need(len(consensus_entries)==1,'Application requires the exact all-three consensus output bundle')
    consensus=json.loads(consensus_entries[0]);replay=consensus.get('replay_inputs',{})
    need(set(replay)=={'dossier_overlay','lean_overlay','approvals'},'Application consensus replay inputs missing')
    for descriptor in replay.values():checked_supporting_file(descriptor,bound)
    expected,_=build(location(replay['dossier_overlay']['path']),location(replay['lean_overlay']['path']),
                     location(replay['approvals']['path']),consensus['version'])
    need(outputs==expected,'Application bundle differs from the approved all-three replay')
    read_inputs() # Recheck protected bytes immediately before writing.
    for path,raw in outputs.items():
        path.parent.mkdir(parents=True,exist_ok=True)
        with path.open('xb') as handle:handle.write(raw)
    read_inputs() # Never mutate protected review artifacts.

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--dossier-overlay',required=True,type=Path);p.add_argument('--lean-overlay',required=True,type=Path)
    p.add_argument('--approvals',required=True,type=Path);p.add_argument('--version',required=True)
    p.add_argument('--apply',action='store_true',help='Write a new version only after coordinator authorization')
    a=p.parse_args();outputs,receipt=build(a.dossier_overlay,a.lean_overlay,a.approvals,a.version)
    if a.apply:apply(outputs)
    print(json.dumps({'operation':'APPLY' if a.apply else 'VALIDATE_ONLY',**receipt},indent=2))

if __name__=='__main__':main()
