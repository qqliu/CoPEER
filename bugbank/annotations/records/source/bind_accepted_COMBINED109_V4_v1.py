import pathlib,json,importlib.util
ROOT=pathlib.Path('<workspace>');P=ROOT/'astra/resource285_quality_check_20260923';HERE=P/'census_refresh';E=P/'extension_COMBINED109_V4_20260923';C=P/'review_candidates/COMBINED109_v4'
def module(n,p):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
b=module('rebindb',P/'build_extension_release.py');r=module('rebindr',HERE/'refresh.py')
def read(p):return json.loads(p.read_bytes())
def desc(p):return {'path':str(p.relative_to(ROOT)),'sha256':b.sha(p.read_bytes())}
assert desc(E/'ledger.json')['sha256']=='55666597b2e9d05de740169f5e7ed69e8f0acf835ad5e693c386734bae4d75d9';assert desc(E/'CONSENSUS.json')['sha256']=='6360e72c6db2894db90199606b197e347fe9d8da7ec0d098a9806732200fbc74'
verified=r.consensus_binding(E/'CONSENSUS.json',E/'ledger.json')
base,selected,allowed,pins=b.read_inputs();pre,specs=b.change_records(base,read(C/'DOSSIER_OVERLAY.json'),read(C/'LEAN_OVERLAY.json'),{x['record_id'] for x in selected['rows']},allowed);specs,ctx=b.prepare_consensus_specifications(base,pre,specs)
assert specs==read(C/'CHANGE_SPECIFICATIONS.json');preby={x['record_id']:x for x in pre};final=read(E/'ledger.json');byid={x['record_id']:x for x in final};baseline=read(r.BASELINE);before={x['record_id']:x for x in baseline};baseby={x['record_id']:x for x in base}
files=['recodings_selected30_basea289_v1.json','recodings_candidate52_remaining40_provisional_v1.json','recodings_astra22_provisional_v1.json','recodings_claude33_R042_withheld_provisional_v1.json','recodings_R042_v3_provisional_v1.json','recodings_final2_combined109_v4_provisional_v1.json'];chosen={};superseded=[]
for name in files:
 for x in read(HERE/name):
  rid=x['record_id']
  if rid in chosen:
   assert name==files[-1] and rid in {'g3ref-pnv-141','mse_3160594__ans3160616'};superseded.append({'record_id':rid,'previous_file':chosen[rid][0],'replacement_file':name})
  chosen[rid]=(name,x)
assert len(chosen)==108
transitions=[]
for rid,(name,x) in chosen.items():
 f=r.fields(byid[rid]);context=r.context(byid[rid]);oldct=x.get('interpretation_context')
 if oldct is None:
  assert x['protected_record_canonical_sha256']==b.sha(r.encoded(baseby[rid]));oldct=r.context(baseby[rid]);oldct.pop('release_status');assert r.value_sha(oldct)==x['context_sha256'];assert r.fields(baseby[rid])==f
 else:assert r.value_sha(oldct)==x['context_sha256']
 assert r.value_sha(f)==x['input_sha256'];assert r.value_sha(r.fields(before[rid]))==x['prior_input_sha256']
 assert 'five_coded_fields' not in x or x['five_coded_fields']==f
 candidate=x.get('candidate_binding')
 if candidate:
  b.bound(candidate['manifest']);b.bound(candidate['input']);assert candidate['change_sha256']==specs[rid]['change_sha256'];assert candidate['final_record_before_consensus_metadata_sha256']==b.value_sha(preby[rid])
 contextdiff={key:{'before':oldct.get(key),'after':context.get(key)} for key in set(oldct)|set(context) if oldct.get(key)!=context.get(key)}
 topdiff={key:{'before':preby[rid].get(key),'after':byid[rid].get(key)} for key in set(preby[rid])|set(byid[rid]) if preby[rid].get(key)!=byid[rid].get(key)}
 transitions.append({'record_id':rid,'source_file':name,'context_changes':contextdiff,'administrative_top_keys':list(sorted(topdiff)),'administrative_changes':topdiff})
import copy,datetime,inspect
now=datetime.datetime.now(datetime.timezone.utc).isoformat();transby={x['record_id']:x for x in transitions}
allowed_admin={'audit','audit_provenance','correction','correction_provenance','exact_checker','witness_action','witness_action_provenance','extension_correction_history','human_approval_of_current_artifact','revised_artifact_requires_new_human_review','corrected_release'}
expected_recode={rid for rid in byid if byid[rid]['release_status']=='RETAINED' and (r.fields(before[rid])!=r.fields(byid[rid]) or r.context(before[rid])!=r.context(byid[rid]))}
assert set(chosen)==expected_recode
assert all(byid[rid]['release_status']=='RETAINED' for rid in chosen)
assert 'reddit_learnmath_6r8mz6' not in chosen and verified['admission']['newly_excluded_record_ids']==['reddit_learnmath_6r8mz6']
rows=[];reviewrows=[]
identity='OpenAI Codex /root/correct30_dossiers; explicit final-ledger documentation rebinding reviewer'
for rid,(name,x) in sorted(chosen.items()):
 record=byid[rid];prepared=preby[rid];t=transby[rid];ctxdiff=t['context_changes'];admin=t['administrative_changes']
 assert not ctxdiff or ctxdiff=={'release_status':{'before':None,'after':'RETAINED'}}
 assert set(admin)<=allowed_admin
 # No informal omission of changed full-record content: the complete candidate
 # was replayed canonically; separately check how finalization moved old fields.
 if 'extension_correction_history' in admin:
  oldhistory=prepared.get('extension_correction_history',[]);newhistory=record['extension_correction_history'];assert newhistory[:-1]==oldhistory
  prior_audit={key:prepared[key] for key in ['audit','audit_provenance','correction','correction_provenance','exact_checker','witness_action','witness_action_provenance'] if key in prepared}
  assert newhistory[-1]['prior_audit_fields']==prior_audit
  assert newhistory[-1]['change_sha256']==specs[rid]['change_sha256']
  assert record['corrected_release']['author_side_consensus']=='ALL_THREE_APPROVED_EXACT_FINAL_CHANGE'
  assert record['corrected_release']['automated_build_is_human_approval'] is False
  assert record['human_approval_of_current_artifact']=='NOT_ESTABLISHED_FOR_CORRECTED_VERSION'
  assert record['revised_artifact_requires_new_human_review'] is True
 annotation=r.validate_annotation(x['annotation'],record);assert annotation==x['annotation']
 reason=('Full five-field content and prior source/scope/formal context are exact. The previous context schema omitted release_status; I verified the complete protected a289 record using its original pretty-JSON hash and the final unchanged RETAINED membership, and explicitly add that context key.' if ctxdiff else 'Full five-field content, complete source/scope/formal context and retained membership match the substantively coded provisional candidate exactly. Its exact change specification and complete pre-consensus record match the canonically replayed accepted candidate.')
 reason+=' Differences outside census context are only the inspected canonical finalization bookkeeping: prior audit fields move into bound history, exact correction consensus is recorded, and inherited human approval is not asserted.' if admin else ' The complete prepared record is unchanged at finalization.'
 binding={'actual_rebinding_reviewer':identity,'rebound_at_utc':now,'basis':'EXPLICIT_IDENTICAL_CONTENT_AND_CONTEXT_TRANSITION_REVIEW','reason':reason,
 'source_recoding_file':desc(HERE/name),'source_recoding_row_sha256':b.value_sha(x),'original_annotation_reviewer':x['reviewer'],'original_annotation_reviewed_at_utc':x['reviewed_at_utc'],
 'previous_ledger_binding':x['ledger_sha256'],'previous_context_sha256':x['context_sha256'],'accepted_ledger':desc(E/'ledger.json'),'canonical_consensus':desc(E/'CONSENSUS.json'),
 'pre_consensus_full_record_sha256':b.value_sha(prepared),'accepted_full_record_sha256':b.value_sha(record),'change_sha256':specs[rid]['change_sha256'],
 'context_transitions':ctxdiff,'finalization_field_transitions':{key:{'before_value_sha256':b.value_sha(d['before']),'after_value_sha256':b.value_sha(d['after'])} for key,d in admin.items()},
 'all_five_fields_equal':True,'labels_and_evidence_unchanged':True,'human_approval_transferred':False}
 row=copy.deepcopy(x);row['status']='EXPLICITLY_BOUND_TO_ACCEPTED_LEDGER';row['ledger_sha256']=desc(E/'ledger.json')['sha256'];row['context_sha256']=r.value_sha(r.context(record));row['five_coded_fields']=r.fields(record);row['interpretation_context']=r.context(record);row['annotation']=annotation;row['rebinding_attestation']=binding
 if 'rebind_requirement' in row:row['previous_provisional_rebind_requirement']=row.pop('rebind_requirement')
 rows.append(row);reviewrows.append({'record_id':rid,'rebinding_attestation':binding,'current_input_sha256':row['input_sha256'],'current_context_sha256':row['context_sha256']})
def write_new(p,x):
 assert not p.exists(),p;p.write_bytes(r.encoded(x))
out=HERE/'recodings_accepted_COMBINED109_V4_20260923_v1.json';write_new(out,rows)
review={'schema':'accepted-census-explicit-rebinding-review/v1','status':'EXPLICIT_REBIND_COMPLETE_CURRENT_ASSET_BUILD_NEXT','actual_rebinding_reviewer':identity,'reviewed_at_utc':now,
 'accepted_ledger':desc(E/'ledger.json'),'canonical_consensus':desc(E/'CONSENSUS.json'),'accepted_provenance':desc(E/'PROVENANCE.json'),'exact_candidate_manifest':desc(C/'MANIFEST.json'),'recodings':desc(out),
 'codebook':desc(ROOT/'qedbench_certificate_availability_triage/analysis/counterexample_structure_20260910/CODEBOOK.md'),'refresh_implementation':desc(HERE/'refresh.py'),'builder_implementation':desc(P/'build_extension_release.py'),
 'source_recoding_files':[desc(HERE/name) for name in files],'source_review_reports':[desc(HERE/name) for name in ['SELECTED30_RECODING_REVIEW_v1.json','CANDIDATE52_REMAINING40_RECODING_REVIEW_v1.json','ASTRA22_RECODING_REVIEW_v1.json','CLAUDE33_RECODING_REVIEW_v1.json','R042_V3_RECODING_REVIEW_v1.json','FINAL2_COMBINED109_V4_RECODING_REVIEW_v1.json']],
 'records':reviewrows,'superseded_provisional_rows':superseded,'coverage':{'explicit_recodings':108,'identical_current_context':97,'explicit_old_context_schema_transitions':11,'remaining_substantive_mismatches':0,'newly_withdrawn_no_current_recoding':['reddit_learnmath_6r8mz6']},
 'exposure_and_limits':'I authored many source recodings and the final2 corrections and have prior mathematical/review exposure. This task explicitly reconciles complete field/context/specification bindings and finalization transitions; it does not pretend to be a new independent annotation of all 284 records. The original annotation author, actual review time, rationale, evidence and exposure remain intact. Other-author annotations are retained only after exact unchanged-content/context checks. Historical audit metadata was visible while verifying canonical finalization but is not used to create new documentation labels. No human answer, model execution, fresh Lean compile or source-validation claim is generated.',
 'hash_conventions':{'selected12_protected_record_canonical_sha256':'SHA256 of refresh.encoded(record): ensure_ascii=False, sort_keys=True, indent=2, final newline; all11 retained older hashes verified exactly. This differs from the compact builder canonical hash.','fields_and_context':'refresh.value_sha: sorted ensure_ascii=False JSON with default separators','candidate_record_and_specifications':'builder.value_sha: sorted ensure_ascii=False compact JSON'},
 'rebind_decisions':['Final2 c35b3617 replaces earlier R094/I023 rows; previous files and judgment histories remain immutable.',
 'R042 uses its separately substantively reviewed v3 recoding; the remaining33 Claude-allocation rows use their exact existing candidate fields/context.',
 'For11 older selected30 rows, current context equals the bound old context plus release_status=RETAINED; the protected complete original record, selected packet/manifest and unchanged membership are checked.',
 'R221 is EXCLUDED/SOURCE_MISMATCH and receives no current recoding. Canonical census machinery preserves its old annotation as history/diagnostic-only.',
 'All complete pre-consensus records/specifications were checked against canonical accepted replay; audited metadata movements are recorded per row and do not alter current documentation fields/context.'],
 'current_property_totals_emitted_by_this_rebinding_step':False,'paper_edits':False,'historical_files_mutated':False,'test_suite_rerun':False,'human_approval_created':False}
rp=HERE/'ACCEPTED_COMBINED109_V4_REBIND_REVIEW_v1.json';write_new(rp,review)
md=HERE/'ACCEPTED_COMBINED109_V4_REBIND_REVIEW_v1.md';assert not md.exists();md.write_text('# Explicit census rebinding to the accepted ledger\n\nAccepted ledger: `55666597b2e9d05de740169f5e7ed69e8f0acf835ad5e693c386734bae4d75d9`; consensus: `6360e72c6db2894db90199606b197e347fe9d8da7ec0d098a9806732200fbc74`. Canonical replay was executed before rebinding.\n\nAll 108 required changed retained rows are covered. Their five mathematical fields match the substantive provisional annotations exactly. Complete current context matches for 97; the other 11 differ only because the older schema omitted the unchanged `RETAINED` membership. Each old complete-record hash, source/scope/formal context and selected package binding was checked explicitly. The old selected12 full-record hash uses pretty JSON with a final newline, not the builder compact hash.\n\nThe latest final2 R094/I023 rows replace the older provisional rows. R042 uses its v3 recoding. R221 remains withdrawn and has no current annotation. Canonical finalization bookkeeping was inspected and recorded per row; no substantive mismatch remains. Original annotator identities, times, labels and evidence are preserved. This is explicit rebinding, not a newly claimed independent mathematical or human review.\n\nThe next actual `refresh.py` invocation produces the current census through accepted provenance and canonical consensus replay. No earlier property totals are imported; old files and paper remain unchanged.\n')
print(json.dumps({'rebound_recodings':desc(out),'review':desc(rp),'coverage':review['coverage']},indent=2))
