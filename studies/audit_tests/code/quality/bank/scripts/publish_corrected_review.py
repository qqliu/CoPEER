#!/usr/bin/env python3
"""Stage an approved corrected ledger in an ISOLATED BugBank checkout only.

Preserve frozen databases and earlier releases; archive prior current authority
and cards. No network operation, live-checkout activation or human approval.
"""
import argparse
import copy
import hashlib
import html
import json
import posixpath
from pathlib import Path
import re
import sqlite3
import subprocess
import sys
import types
from urllib.parse import quote
import yaml
try:
    from . import active_release
except ImportError:
    import active_release

MARKER='.corrected-review-isolated-stage.json'

def need(value,message):
    if not value:raise ValueError(message)
def sha(raw):return hashlib.sha256(raw).hexdigest()
def digest(path):return sha(path.read_bytes())
def jb(value):return (json.dumps(value,ensure_ascii=False,sort_keys=True,indent=2)+'\n').encode()
def record_sha(value):return sha(json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode())
CONSENSUS_VERIFIER='quality/build_extension_release.py'
REQUIRED_REVIEWERS=['REVIEWER_A','REVIEWER_B','REVIEWER_C']

def canonical_descriptor(root,descriptor):
    need(isinstance(descriptor,dict) and isinstance(descriptor.get('path'),str),'Evidence descriptor/path missing')
    root=Path(root).resolve();path=(root/descriptor['path']).resolve()
    need(path.is_relative_to(root),'Evidence outside research root')
    expected=descriptor.get('sha256')
    need(isinstance(expected,str) and re.fullmatch('[0-9a-f]{64}',expected) is not None,'Invalid evidence SHA256')
    result={'path':str(path.relative_to(root)),'sha256':expected}
    if 'bytes' in descriptor:result['bytes']=descriptor['bytes']
    return result

def read_bound(root,descriptor):
    descriptor=canonical_descriptor(root,descriptor)
    raw=(Path(root).resolve()/descriptor['path']).read_bytes()
    need(sha(raw)==descriptor['sha256'],'Evidence hash differs: '+descriptor['path'])
    if 'bytes' in descriptor:need(len(raw)==descriptor['bytes'],'Evidence byte length differs')
    return raw

def load_verifier_bytes(raw,path):
    module=types.ModuleType('copeer_exact_consensus_verifier')
    module.__file__=str(path)
    exec(compile(raw,str(path),'exec'),module.__dict__)
    need(callable(getattr(module,'verify_consensus_receipt',None)),'Mandatory consensus verifier API absent')
    return module

def validate_admission(admission,before,ledger,corrected_ids):
    need(isinstance(admission,dict) and admission.get('schema')=='current-resource-admission/v1','Replay-bound current admission roster missing')
    historical_retained=sorted(r['record_id'] for r in before if r['release_status']=='RETAINED')
    historical_excluded=sorted(r['record_id'] for r in before if r['release_status']=='EXCLUDED')
    retained=sorted(r['record_id'] for r in ledger if r['release_status']=='RETAINED')
    excluded=sorted(r['record_id'] for r in ledger if r['release_status']=='EXCLUDED')
    withdrawn=sorted(set(historical_retained)-set(retained));corrected=sorted(corrected_ids)
    expected={'historical_retained_record_ids':historical_retained,'historical_excluded_record_ids':historical_excluded,
        'current_retained_record_ids':retained,'current_excluded_record_ids':excluded,
        'newly_excluded_record_ids':withdrawn,'current_retained_ids_sha256':record_sha(retained),
        'counts':{'total_rows':len(ledger),'historical_retained':len(historical_retained),'historical_excluded':len(historical_excluded),
            'current_retained':len(retained),'current_excluded':len(excluded),'newly_excluded':len(withdrawn)},
        'corrected_execution_record_ids':corrected,'current_retained_corrected_record_ids':sorted(set(corrected)&set(retained)),
        'diagnostic_only_corrected_record_ids':sorted(set(corrected)&set(excluded)),
        'diagnostic_only_excluded_from_current_metrics':True}
    need(all(admission.get(key)==value for key,value in expected.items()),'Consensus admission roster differs from bank ledgers')
    need(set(withdrawn)<=set(corrected),'Withdrawal lacks exact correction consensus')

def verify_consensus(research,descriptor,ledger_descriptor,corrected_ids,before):
    """Invoke the actual content-bound replay gate; labels alone never suffice."""
    research=Path(research).resolve()
    descriptor=canonical_descriptor(research,descriptor)
    ledger_descriptor=canonical_descriptor(research,ledger_descriptor)
    raw=read_bound(research,descriptor);consensus=json.loads(raw)
    need(consensus.get('schema')=='copeer-all-three-correction-consensus/v1' and
         consensus.get('status')=='ALL_THREE_APPROVE_EXACT_FINAL_CORRECTIONS','All-three final correction consensus required')
    need(consensus.get('required_reviewers')==REQUIRED_REVIEWERS,'All three actual reviewer identities required')
    need(consensus.get('ledger_sha256')==ledger_descriptor['sha256'],'Consensus binds a different final ledger')
    ledger=json.loads(read_bound(research,ledger_descriptor))
    ids=consensus.get('corrected_record_ids')
    need(isinstance(ids,list) and len(ids)==len(set(ids)) and set(ids)==set(corrected_ids),
         'Consensus does not cover every final changed bank record')
    verifier=canonical_descriptor(research,{'path':CONSENSUS_VERIFIER,'sha256':consensus.get('builder_sha256')})
    verifier_raw=read_bound(research,verifier)
    module=load_verifier_bytes(verifier_raw,research/verifier['path'])
    verified=module.verify_consensus_receipt(descriptor,ledger_descriptor)
    need(verified==consensus,'Verifier returned different consensus content')
    validate_admission(consensus.get('admission'),before,ledger,corrected_ids)
    read_bound(research,verifier) # Refuse a code race during replay.
    return {'receipt':descriptor,'ledger':ledger_descriptor,'verifier':verifier,
            'status':consensus['status'],'required_reviewers':REQUIRED_REVIEWERS,
            'corrected_record_ids':sorted(corrected_ids),'admission':consensus['admission']},raw


def parse_card(raw):
    match=re.fullmatch(r'---\n(.*?)\n---\n(.*)',raw.decode(),re.S)
    need(match is not None,'Invalid existing card')
    return yaml.safe_load(match[1])

SOURCE_STATUSES={'AUTHOR_REVIEWED','RESOLVED_WITH_SOURCE_SUPPLEMENT','UNRESOLVED','CANNOT_DETERMINE','SOURCE_LIMITED','SOURCE_MISMATCH'}
UNCERTAIN_SOURCE={'UNRESOLVED','CANNOT_DETERMINE','SOURCE_LIMITED'}

def source_state(record):
    state=record.get('source_correspondence')
    if state is None:
        flags=record.get('source_correspondence_flags',[])
        if flags:
            # Match the canonical extension verifier's conservative legacy fallback.
            # This is a rendering projection; approved ledger bytes stay unchanged.
            statuses={item.get('status') for item in flags}
            need(statuses <= UNCERTAIN_SOURCE,'Unsupported historical source flag status')
            fallback=next(s for s in ('UNRESOLVED','CANNOT_DETERMINE','SOURCE_LIMITED') if s in statuses)
            return {'status':fallback,'reason':'No separately reviewed active status supplied; preserved source flags remain applicable.',
                    'evidence_ids':[]}
        return {'status':'NOT_SEPARATELY_SPECIFIED','reason':'Consult the versioned author-side review. This is not human approval.','evidence_ids':[]}
    need(isinstance(state,dict) and state.get('status') in SOURCE_STATUSES,'Invalid explicit source correspondence status')
    need(isinstance(state.get('reason'),str) and len(state['reason'].strip())>=20,'Source status requires a substantive author-side reason')
    evidence={d['evidence_id']:d for d in record.get('public_supporting_evidence',[])}
    need(isinstance(state.get('evidence_ids'),list) and set(state['evidence_ids']).issubset(evidence),'Source status names absent accepted public evidence')
    if state['status']=='AUTHOR_REVIEWED':
        need(not record.get('source_correspondence_flags'),'AUTHOR_REVIEWED cannot silently clear recorded source limitations')
    if state['status'] in {'RESOLVED_WITH_SOURCE_SUPPLEMENT','SOURCE_MISMATCH'}:
        need(any(evidence[k]['kind']=='source_supplement' for k in state['evidence_ids']),'Source resolution or mismatch requires an accepted source supplement')
    if state['status']=='SOURCE_MISMATCH':
        need(record.get('release_status')=='EXCLUDED','SOURCE_MISMATCH must be excluded from the active bank')
    return state

def supporting_assets(record,research,release):
    descriptors=record.get('public_supporting_evidence',[])
    need(isinstance(descriptors,list),'Public supporting evidence must be a list')
    bindings=[];outputs={};seen=set()
    for d in descriptors:
        eid=d.get('evidence_id')
        need(isinstance(eid,str) and re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]*',eid) is not None and eid not in seen,'Invalid/duplicate public evidence ID')
        seen.add(eid)
        need(d.get('kind') in {'source_supplement','ancillary_computation'},'Unsupported public evidence kind')
        need(isinstance(d.get('label'),str) and d['label'].strip(),'Public evidence label missing')
        need(isinstance(d.get('accepted_by'),str) and d['accepted_by'].strip(),'Public evidence requires actual named approval')
        need(isinstance(d.get('approval_report'),dict),'Public evidence approval report missing')
        approval=json.loads(read_bound(research,d['approval_report']))
        need(d['accepted_by'] in (approval.get('actual_reviewer'),approval.get('reviewer')),'Public evidence approval identity mismatch')
        raw=read_bound(research,d)
        name=Path(d['path']).name
        need(name and not name.startswith('.'),'Invalid public evidence basename')
        target='dossiers/'+release+'/evidence/'+record['record_id']+'/support/'+eid+'/'+name
        outputs[target]=raw
        canonical=canonical_descriptor(research,d)
        bindings.append({**d,'path':canonical['path'],'original_path':canonical['path'],
            'approval_report':canonical_descriptor(research,d['approval_report']),
            'source_descriptor_sha256':record_sha(d),'vendored_path':target,'bytes':len(raw)})
    source_state(record)
    return outputs,bindings

def render_card(meta,record,release,certificate,dossier,archive):
    meta=copy.deepcopy(meta);f=record['current_fields'];flags=record.get('source_correspondence_flags',[]);state=source_state(record)
    uncertain=state['status'] in UNCERTAIN_SOURCE
    meta.update(statement=f['witness'],refutes=f['claim_quote'],status='draft' if uncertain else 'verified',
        formalized=[certificate],review_release=release,review_record_id=record['record_id'],dossier=dossier,
        formal_status='KERNEL_CHECKED_SELECTED_DECLARATIONS',human_review_status=record['human_approval_of_current_artifact'],
        source_correspondence_status=state['status'])
    meta.pop('true_theorem',None);meta.pop('hypothesis_violated',None)
    if uncertain and 'source-correspondence-unresolved' not in meta['tags']:
        meta['tags'].append('source-correspondence-unresolved')
    sections=['## Object\n\n'+f['witness'],'## Challenged source claim\n\n'+f['claim_quote'],
        '## Objection\n\n'+f.get('flaw',''),'## Explanation\n\n'+f.get('explanation',''),
        '## Scope and evidence\n\nThis version separates the source passage, proposed objection and selected formal statements. '
        'Author-side quality review and kernel checks are not new human approval. '
        'A checked local statement does not certify every informal comment or refute a final theorem automatically.']
    sections.append('### Active source correspondence (author-side review)\n\n'+state['status']+': '+state['reason'])
    if record.get('corrected_scope_metadata'):
        sections.append('### Source and formal scope\n\n'+'\n\n'.join(k.replace('_',' ')+': '+str(v) for k,v in record['corrected_scope_metadata'].items()))
    if flags:
        sections.append('### Recorded extraction and context limitations\n\n'+'\n\n'.join(x['status']+': '+x['reason'] for x in flags))
    sections += ['Current dossier: [source, witness, definitions and selected-check evidence](../../'+dossier+').',
        'Selected Lean declarations: '+', '.join('`'+x['name']+'`' for x in record['build_record']['selected_theorems'])+'.',
        'Certificate SHA-256: `'+record['lean_sha256']+'`.',
        'Prior card: [archive](../../'+archive+'). Current version: [authority](../../active_review.json).']
    return ('---\n'+yaml.safe_dump(meta,sort_keys=False,allow_unicode=True)+'---\n\n'+'\n\n'.join(sections)+'\n').encode()

def render_dossier(record,certificate,evidence,bindings=None,certificate_path=None,dossier_path=None):
    parts=[]
    def pre(label,value):
        if value is not None:parts.append('<h2>'+html.escape(label)+'</h2><pre>'+html.escape(value if isinstance(value,str) else json.dumps(value,ensure_ascii=False,indent=2))+'</pre>')
    pre('Version and roles','Corrected resource artifact. Author-side review is not human approval. Historical human answers below apply only to their original artifact.')
    for key in ('problem','claim_quote','source_context','complete_source','witness','flaw','explanation'):
        pre(key.replace('_',' ').capitalize(),record['current_fields'].get(key))
    pre('Source and formal scope',record.get('corrected_scope_metadata'))
    pre('Active source correspondence (author-side review, not human approval)',source_state(record))
    pre('Recorded extraction and context limitations',record.get('source_correspondence_flags',[]))
    pre('Selected declarations and kernel-printed types',record['build_record']['selected_theorems'])
    pre('Complete supplied Lean file',certificate.decode())
    pre('Exact build record',record['build_record'])
    pre('Human approval of this artifact',record['human_approval_of_current_artifact'])
    pre('Historical human answers (original artifacts only)',record.get('historical_human_reviews',[]))
    for name,raw in evidence.items():
        pre('Mechanical evidence: '+name,raw.decode())
    if dossier_path:
        parent=posixpath.dirname(dossier_path)
        links=[('Exact dossier JSON',str(Path(dossier_path).with_suffix('.json')))]
        if certificate_path:links.append(('Exact Lean certificate',certificate_path))
        links.extend((x['label'],x['vendored_path']) for x in bindings or [])
        parts.append('<h2>Download exact supporting evidence</h2><ul>'+''.join(
            '<li><a href="'+html.escape(quote(posixpath.relpath(path,parent),safe='/-._~'),quote=True)+'">'+html.escape(label)+'</a></li>'
            for label,path in links)+'</ul>')
    return ('<!doctype html><html lang="en"><meta charset="utf-8"><title>'+html.escape(record['record_id'])+
        '</title><style>body{max-width:1050px;margin:2rem auto;font:16px/1.5 system-ui}pre{white-space:pre-wrap;overflow-wrap:anywhere}</style><h1>'+
        html.escape(record['record_id'])+'</h1>'+''.join(parts)+'</html>\n').encode()

def validate_ledger(old,ledger,expected=None):
    need(len(ledger)==len(old),'Reviewed population differs')
    if expected is not None:need(len(ledger)==expected['reviewed'],'Reviewed population differs')
    need(len({x['record_id'] for x in ledger})==len(ledger),'Duplicate ledger IDs')
    need([r['record_id'] for r in ledger]==[r['record_id'] for r in old],'Record identities/order changed')
    immutable=('historical_inventory','historical_source_fields','historical_human_reviews','historical_human_all_yes',
               'historical_human_unambiguous_approval','source_packet','original_record_id','assignment_group')
    for before,after in zip(old,ledger):
        need(after['release_status'] in {'RETAINED','EXCLUDED'},'Unsupported release status')
        need(all(before.get(k)==after.get(k) for k in immutable),'Historical/source identity changed')
        need(all(before['current_fields'].get(k)==after['current_fields'].get(k) for k in ('problem','source_context','complete_source')),
             'Original source/problem changed')
        if before['release_status']=='EXCLUDED':
            need(before==after,'Historical withdrawal changed or restored');continue
        state=source_state(after)
        need(after.get('human_approval_of_current_artifact','').startswith('NOT_ESTABLISHED'),'Refresh cannot manufacture current human approval')
        if before!=after:
            need(after.get('revised_artifact_requires_new_human_review') is True,'Changed record transferred old human approval')
        if after['release_status']=='EXCLUDED':
            need(state['status']=='SOURCE_MISMATCH','New withdrawal requires accepted SOURCE_MISMATCH evidence')
            continue
        br=after.get('build_record') or {}
        need(br.get('status')=='PASS' and br.get('selected_theorems_present') and br.get('selected_theorem_trust_tier')=='KERNEL_ONLY',
             'Retained record missing selected kernel proof')
        need(br.get('source_sha256')==after['lean_sha256'],'Build record binds another Lean source')
        need(br.get('selected_theorems') and all(x['name']==x['audit']['name'] and x['audit'].get('type') and
             not x['audit'].get('unsafe') and not x['audit'].get('disallowed_axioms') and
             not x['audit'].get('uses_native_reduction') for x in br['selected_theorems']),'Selected declaration evidence incomplete')
    if expected is not None:
        need(sum(x['release_status']=='RETAINED' for x in ledger)==expected['retained'],'Retained count differs')
        need(sum(x['release_status']=='EXCLUDED' for x in ledger)==expected['withdrawn'],'Withdrawal count differs')

def withdrawal_plan(old,ledger,prior_rows,release):
    result=[]
    for before,after in zip(old,ledger):
        if before['release_status']=='RETAINED' and after['release_status']=='EXCLUDED':
            row=prior_rows[after['record_id']]
            need(row['decision']=='retain','Prior withdrawal authority disagrees with ledger')
            path=row['entry_path']
            need(path.startswith('entries/') and path.endswith('.md'),'Withdrawal targets must be current cards')
            result.append({'record_id':after['record_id'],'entry_path':path,'entry_sha256':row['entry_sha256'],
                'archive_path':'releases/'+release+'/archive/'+path})
    return result

def render_withdrawal(record,dossier,archive,bindings,historical):
    parts=['<!doctype html><html lang="en"><meta charset="utf-8"><title>Withdrawn source mismatch</title>',
        '<h1>Withdrawn: '+html.escape(record['record_id'])+'</h1>',
        '<p>This record is excluded from the current active bank. Author/model review is not human approval. '
        'Historical formal checks remain evidence of their selected statements; they do not establish source correspondence.</p>']
    for label,value in [('Author-side source correspondence',source_state(record)),('Original source snapshot',record['current_fields']),
                        ('Historical extraction/context flags',record.get('source_correspondence_flags',[]))]:
        parts.append('<h2>'+label+'</h2><pre>'+html.escape(json.dumps(value,ensure_ascii=False,indent=2))+'</pre>')
    links=[('Exact withdrawal record',str(Path(dossier).with_suffix('.json'))),('Exact prior card (historical)',archive)]
    links.extend(('Historical '+key,path) for key,path in historical.items() if key in {'certificate','dossier'})
    links.extend((item['label'],item['vendored_path']) for item in bindings)
    parts.append('<ul>'+''.join('<li><a href="'+html.escape(quote(posixpath.relpath(path,posixpath.dirname(dossier)),safe='/-._~'),quote=True)+'">'+html.escape(label)+'</a></li>' for label,path in links)+'</ul></html>\n')
    return ''.join(parts).encode()


def build(bank,research,ledger_path,acceptance_path,release,expected=None):
    bank=Path(bank).resolve();research=Path(research).resolve();ledger_path=Path(ledger_path).resolve()
    need((bank/MARKER).is_file(),'Only an explicitly marked isolated checkout may be staged')
    marker=json.loads((bank/MARKER).read_bytes())
    need(bank!=Path(marker['source_bank']).resolve() and marker['isolated_bank']==str(bank),'Live authority switch refused')
    need(re.fullmatch(r'[a-z0-9][a-z0-9_]*',release) is not None,'Unsafe release name')
    dest=bank/'releases'/release;need(not dest.exists(),'Release version already exists')
    authority_path=bank/active_release.NAME;prior_raw=authority_path.read_bytes();prior=json.loads(prior_raw)
    need(sha(prior_raw)==marker['source_authority_sha256'],'Isolated authority drift since checkout preparation')
    prior_rows=active_release.load(bank);paths=active_release.active_paths(bank)
    old_ledger_path=active_release.ledger_path(bank);old_raw=old_ledger_path.read_bytes()
    need(sha(old_raw)==prior['source_ledger_sha256'],'Previous active ledger hash drift')
    old=json.loads(old_raw);ledger_raw=ledger_path.read_bytes();ledger=json.loads(ledger_raw)
    acceptance_raw=Path(acceptance_path).read_bytes();acceptance=json.loads(acceptance_raw)
    need(acceptance.get('status')=='APPROVED_FOR_BANK_STAGING' and acceptance.get('ledger_sha256')==sha(ledger_raw),
         'Final ledger is not approved for bank staging')
    need(isinstance(acceptance.get('coordinator'),str) and acceptance['coordinator'].strip(),'Actual coordinator acceptance missing')
    need(acceptance.get('review_evidence'),'Accepted review evidence must be pinned')
    for entry in acceptance['review_evidence']:read_bound(research,entry)
    validate_ledger(old,ledger,expected)
    changed_ids=[after['record_id'] for before,after in zip(old,ledger) if before!=after]
    need(isinstance(acceptance.get('consensus'),dict),'Mandatory all-three consensus descriptor missing')
    consensus_binding,consensus_raw=verify_consensus(research,acceptance['consensus'],
        {'path':str(ledger_path),'sha256':sha(ledger_raw)},changed_ids,old)
    need(set(prior_rows)=={r['record_id'] for r in ledger},'Authority/ledger identity mismatch')
    kept_ids={r['entry_id'] for r in prior_rows.values() if r['decision']=='retain'}
    outside={str(p.relative_to(bank)):digest(p) for p in paths if p.stem not in kept_ids}
    if expected is not None:need(len(outside)==expected['outside'],'Out-of-scope population differs')
    expected={'reviewed':len(ledger),'retained':sum(r['release_status']=='RETAINED' for r in ledger),
        'withdrawn':sum(r['release_status']=='EXCLUDED' for r in ledger),'outside':len(outside)}
    expected['active']=expected['retained']+expected['outside']
    for record in old:
        need(prior_rows[record['record_id']]['decision']==('retain' if record['release_status']=='RETAINED' else 'withdraw'),
             'Previous authority and ledger decisions disagree')
    removals=withdrawal_plan(old,ledger,prior_rows,release)
    historical={str(p.relative_to(bank)):digest(p) for folder in ('releases','lean','dossiers')
                for p in (bank/folder).rglob('*') if p.is_file()}
    historical['bugbank.sqlite']=digest(bank/'bugbank.sqlite')
    outputs={};authority=copy.deepcopy(prior)
    authority.update(schema=active_release.CORRECTED_SCHEMA,release=release,
        ledger='releases/'+release+'/ledger.json',manifest='releases/'+release+'/MANIFEST.json',
        database='releases/'+release+'/bugbank.sqlite',source_ledger_sha256=sha(ledger_raw),
        reviewed_population=expected['reviewed'],previous_authority='releases/'+release+'/archive/active_review.json',
        previous_authority_sha256=sha(prior_raw),outside_review_entries=outside,retained_historical_files=historical,
        scope='Corrected resource version; selected Lean checks and author-side source review are separate. No new human approval.',
        records={})
    authority.pop('source_release_summary_sha256',None)
    authority['correction_consensus']=consensus_binding
    authority['withdrawn_card_removals']=removals
    authority['correction_consensus_path']='releases/'+release+'/CONSENSUS.json'
    outputs[bank/authority['correction_consensus_path']]=consensus_raw
    outputs[bank/authority['previous_authority']]=prior_raw
    outputs[dest/'ledger.json']=ledger_raw;outputs[dest/'ACCEPTANCE.json']=acceptance_raw
    for record in ledger:
        rid=record['record_id'];previous=prior_rows[rid];entry_path=bank/previous['entry_path']
        decision=copy.deepcopy(previous);decision.pop('audit_sha256',None)
        decision.update(record_sha256=record_sha(record),decision_sha256=record_sha(record),human_approval_created=False,
            source_correspondence_flags=record.get('source_correspondence_flags',[]),
            source_correspondence=record.get('source_correspondence'))
        if record['release_status']!='RETAINED' and previous['decision']=='withdraw':
            need(not entry_path.exists(),'Historical withdrawal unexpectedly present')
            authority['records'][rid]=decision;continue
        need(digest(entry_path)==previous['entry_sha256'],'Current card no longer matches previous authority')
        archive=dest/'archive'/previous['entry_path'];outputs[archive]=entry_path.read_bytes()
        if record['release_status']=='EXCLUDED':
            supporting,bindings=supporting_assets(record,research,release)
            outputs.update({bank/name:raw for name,raw in supporting.items()})
            historical_assets={key:previous[key] for key in ('certificate','certificate_sha256','dossier','dossier_sha256') if key in previous}
            dossier='dossiers/'+release+'/'+rid+'.html'
            dossier_raw=render_withdrawal(record,dossier,str(archive.relative_to(bank)),bindings,historical_assets)
            outputs[bank/dossier]=dossier_raw;outputs[(bank/dossier).with_suffix('.json')]=jb(record)
            for key in ('certificate','certificate_sha256','dossier','dossier_sha256','dossier_json_sha256',
                        'final_theorems','build_record','evidence_files','current_witness','entry_sha256',
                        'evidence_tier','binding','witness_action','witness_binding','original_witness','old_statement_matches_frozen_witness'):
                decision.pop(key,None)
            decision.update(decision='withdraw',release_status='EXCLUDED',reason=source_state(record)['reason'],
                semantic_status='SOURCE_MISMATCH',archive_path=str(archive.relative_to(bank)),
                original_entry_sha256=sha(entry_path.read_bytes()),historical_artifacts=historical_assets,
                withdrawal_dossier=dossier,withdrawal_dossier_sha256=sha(dossier_raw),
                withdrawal_dossier_json_sha256=sha(jb(record)),public_supporting_evidence=bindings)
            authority['records'][rid]=decision;continue
        lean_raw=read_bound(research,{'path':record['lean_path'],'sha256':record['lean_sha256']})
        certificate='lean/'+release+'/'+rid+'.lean';dossier='dossiers/'+release+'/'+rid+'.html'
        outputs[bank/certificate]=lean_raw
        evidence={'build_record.json':jb(record['build_record'])}
        br=record['build_record']
        for key in ('compile_receipt','axiom_receipt','fresh_environment'):
            if br.get(key):evidence[key+'.json']=read_bound(research,br[key])
        for key in ('compile_log','axiom_log'):
            if br.get(key):
                source=(research/br[key]).resolve();need(source.is_relative_to(research),'Log escapes research checkout')
                evidence[key+'.txt']=source.read_bytes()
        for dep in record.get('local_dependencies',[]):
            evidence['dependency_'+str(len(evidence))+'.lean']=read_bound(research,{'path':dep['source'],'sha256':dep['sha256']})
        supporting,bindings=supporting_assets(record,research,release)
        outputs.update({bank/name:raw for name,raw in supporting.items()})
        dossier_raw=render_dossier(record,lean_raw,evidence,bindings,certificate,dossier);outputs[bank/dossier]=dossier_raw
        outputs[(bank/dossier).with_suffix('.json')]=jb(record)
        evidences=[]
        for name,raw in evidence.items():
            path='dossiers/'+release+'/evidence/'+rid+'/'+name;outputs[bank/path]=raw
            evidences.append({'path':path,'sha256':sha(raw)})
        card=render_card(parse_card(entry_path.read_bytes()),record,release,certificate,dossier,str(archive.relative_to(bank)))
        outputs[entry_path]=card
        decision.update(entry_sha256=sha(card),archive_path=str(archive.relative_to(bank)),original_entry_sha256=sha(entry_path.read_bytes()),
            certificate=certificate,certificate_sha256=sha(lean_raw),dossier=dossier,dossier_sha256=sha(dossier_raw),
            dossier_json_sha256=sha(jb(record)),final_theorems=[x['name'] for x in br['selected_theorems']],
            evidence_tier=record['evidence_tier'],build_record=br,evidence_files=evidences,public_supporting_evidence=bindings,
            current_witness=record['current_fields']['witness'],semantic_status=source_state(record)['status'])
        for stale in ('reason','witness_action','original_witness','witness_binding','old_statement_matches_frozen_witness'):
            decision.pop(stale,None)
        authority['records'][rid]=decision
    outputs[authority_path]=jb(authority)
    workflow=bank/'.github/workflows/validate.yml';workflow_text=workflow.read_text()
    previous_manifest=str(active_release.release_manifest_path(bank).relative_to(bank))
    need('--manifest '+previous_manifest in workflow_text,'Expected CI manifest pointer absent')
    outputs[workflow]=workflow_text.replace('--manifest '+previous_manifest,'--manifest '+authority['manifest']).encode()
    receipt={'schema':'bugbank-corrected-staging/v1','source_ledger_sha256':sha(ledger_raw),'release':release,
        'counts':expected,'previous_authority_sha256':sha(prior_raw),'new_authority_sha256':sha(jb(authority)),
        'outside_review_entries_unchanged':outside,'retained_historical_files':historical,
        'correction_consensus':consensus_binding,
        'withdrawn_card_removals':removals,
        'human_approval_created':False,'state':'ISOLATED_CANDIDATE_AWAITING_VALIDATION_AND_PUBLICATION',
        'publication_performed':False,'site_host_deployment_performed':False}
    outputs[dest/'STAGING_RECEIPT.json']=jb(receipt)
    return outputs,authority,receipt


def stage(outputs,bank,research):
    bank=Path(bank).resolve()
    need((bank/MARKER).is_file(),'Unmarked live checkout refused')
    authority=json.loads(outputs[bank/active_release.NAME]);binding=authority.get('correction_consensus')
    need(isinstance(binding,dict),'Mandatory consensus absent from prepared authority')
    prior_raw=outputs[bank/authority['previous_authority']]
    need(prior_raw==(bank/active_release.NAME).read_bytes(),'Authority changed before staging')
    prior=json.loads(prior_raw);old_raw=active_release.ledger_path(bank).read_bytes()
    need(sha(old_raw)==prior['source_ledger_sha256'],'Previous ledger changed before staging')
    old=json.loads(old_raw)
    verified,raw=verify_consensus(research,binding['receipt'],binding['ledger'],binding['corrected_record_ids'],old)
    need(verified==binding,'Prepared consensus binding changed before staging')
    need(outputs[bank/authority['correction_consensus_path']]==raw,'Prepared consensus bytes changed')
    need(sha(outputs[bank/authority['ledger']])==binding['ledger']['sha256'],'Prepared ledger differs from consensus')
    ledger=json.loads(outputs[bank/authority['ledger']]);validate_ledger(old,ledger)
    removals=withdrawal_plan(old,ledger,prior['records'],authority['release'])
    need(authority.get('withdrawn_card_removals')==removals,'Prepared withdrawal removal plan changed')
    for name,pin in authority['retained_historical_files'].items():
        need(digest(active_release.safe_path(bank,name))==pin,'Historical artifact changed before staging: '+name)
    for name,pin in authority['outside_review_entries'].items():
        need(digest(active_release.safe_path(bank,name))==pin,'Outside-review card changed before staging: '+name)
    for item in removals:
        path=active_release.safe_path(bank,item['entry_path']);archive=active_release.safe_path(bank,item['archive_path'])
        need(path not in outputs,'Withdrawal card cannot also be rewritten')
        need(path.is_file() and digest(path)==item['entry_sha256'],'Withdrawal card changed before removal')
        need(outputs.get(archive)==path.read_bytes(),'Withdrawal archive differs from exact current card')
        row=authority['records'][item['record_id']]
        need(row['decision']=='withdraw' and row['archive_path']==item['archive_path'] and
             row['original_entry_sha256']==item['entry_sha256'],'Prepared withdrawal authority changed')
    for path in outputs:
        need(path.resolve().is_relative_to(bank),'Output escapes isolated bank')
        if path.exists():
            rel=str(path.relative_to(bank))
            need(rel==active_release.NAME or rel=='.github/workflows/validate.yml' or rel.startswith('entries/'),
                 'Existing historical output would be overwritten: '+rel)
    for path,raw in outputs.items():path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(raw)
    for item in removals:
        path=active_release.safe_path(bank,item['entry_path'])
        need(digest(path)==item['entry_sha256'],'Withdrawal card changed during staging')
        path.unlink()


def finish_manifest(bank,authority,receipt):
    bank=Path(bank)
    def db_record(name):
        p=bank/name
        with sqlite3.connect(p.resolve().as_uri()+'?mode=ro',uri=True) as con:count=con.execute('SELECT COUNT(*) FROM entries').fetchone()[0]
        return {'path':name,'sha256':digest(p),'entry_count':count,'unchanged':True}
    prior=json.loads((bank/authority['previous_authority']).read_bytes())
    old_manifest=json.loads(active_release.safe_path(bank,prior.get('manifest','releases/'+prior['release']+'/MANIFEST.json')).read_bytes())
    current=db_record(authority['database']);previous=db_record(prior['database'])
    retained={r['path']:r for r in [old_manifest['previous_release'],*old_manifest.get('retained_releases',[])]}
    retained.pop(previous['path'],None)
    manifest={'schema':'bugbank-corrected-resource-release/v2','database':current['path'],'database_sha256':current['sha256'],
        'entry_count':current['entry_count'],'active_review_sha256':digest(bank/active_release.NAME),
        'source_ledger_sha256':authority['source_ledger_sha256'],'frozen_database':old_manifest['frozen_database'],
        'previous_release':previous,'retained_releases':list(retained.values()),
        'reviewed_population':receipt['counts']['reviewed'],'retained_reviewed':receipt['counts']['retained'],
        'excluded_reviewed':receipt['counts']['withdrawn'],'outside_review_unchanged':receipt['counts']['outside']}
    path=bank/authority['manifest'];need(not path.exists(),'Final manifest already exists');path.write_bytes(jb(manifest))
    return manifest


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--bank',required=True,type=Path);p.add_argument('--research',required=True,type=Path)
    p.add_argument('--ledger',required=True,type=Path);p.add_argument('--acceptance',required=True,type=Path)
    p.add_argument('--release',required=True);p.add_argument('--stage-and-build',action='store_true')
    a=p.parse_args()
    outputs,authority,receipt=build(a.bank,a.research,a.ledger,a.acceptance,a.release)
    if a.stage_and_build:
        stage(outputs,a.bank,a.research)
        subprocess.run([sys.executable,str(a.bank/'scripts/build_db.py')],cwd=a.bank,check=True)
        finish_manifest(a.bank,authority,receipt)
        subprocess.run([sys.executable,str(a.bank/'scripts/build_site.py')],cwd=a.bank,check=True)
        subprocess.run([sys.executable,str(a.bank/'scripts/check_active_review.py')],cwd=a.bank,check=True)
        subprocess.run([sys.executable,str(a.bank/'scripts/check_release_database.py'),'--manifest',authority['manifest']],cwd=a.bank,check=True)
    print(json.dumps({'operation':'STAGED_AND_BUILT' if a.stage_and_build else 'VALIDATE_INPUTS_ONLY',**receipt},indent=2))

if __name__=='__main__':main()
