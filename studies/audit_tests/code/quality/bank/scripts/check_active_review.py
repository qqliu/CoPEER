#!/usr/bin/env python3
"""Verify active bank, archived withdrawals, dossiers and proof bindings."""
import hashlib
import json
from pathlib import Path
import re
import sqlite3
try:
    from . import active_release, build_db, build_site, site_assets, publish_corrected_review
except ImportError:
    import active_release, build_db, build_site, site_assets, publish_corrected_review

ROOT = Path(__file__).resolve().parent.parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def check_supporting_evidence(root,rid,row,record):
    descriptors=record.get('public_supporting_evidence',[])
    assert len(descriptors)==len(row.get('public_supporting_evidence',[])),rid
    for descriptor,binding in zip(descriptors,row.get('public_supporting_evidence',[])):
        original_digest=hashlib.sha256(json.dumps(descriptor,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode()).hexdigest()
        assert binding['source_descriptor_sha256']==original_digest,rid
        assert all(binding.get(k)==v for k,v in descriptor.items() if k not in {'path','approval_report'}),rid
        assert binding['approval_report']['sha256']==descriptor['approval_report']['sha256'],rid
        for location in (binding['path'],binding['original_path'],binding['approval_report']['path']):
            assert not Path(location).is_absolute() and '..' not in Path(location).parts,rid
        assert binding['path']==binding['original_path'],rid
        assert sha(active_release.safe_path(root,binding['vendored_path']))==descriptor['sha256'],rid

def check(root=ROOT):
    root=Path(root)
    authority=json.loads((root/active_release.NAME).read_text())
    corrected=authority.get('schema')==active_release.CORRECTED_SCHEMA
    rows=active_release.load(root)
    assert rows, 'No review authority'
    kept={r['entry_id'] for r in rows.values() if r['decision']=='retain'}
    withdrawn=active_release.withdrawn_ids(rows)
    paths=active_release.active_paths(root)
    active={p.stem for p in paths}
    assert kept <= active and not withdrawn & active
    ledger_file=active_release.ledger_path(root)
    assert sha(ledger_file)==authority['source_ledger_sha256'], 'Active ledger hash differs'
    if corrected:
        release_manifest=json.loads(active_release.release_manifest_path(root).read_text())
        assert release_manifest['active_review_sha256']==sha(root/active_release.NAME),'Authority/manifest digest differs'
        assert release_manifest['source_ledger_sha256']==authority['source_ledger_sha256'],'Manifest/ledger digest differs'
        binding=authority['correction_consensus']
        consensus_path=active_release.safe_path(root,authority['correction_consensus_path'])
        assert sha(consensus_path)==binding['receipt']['sha256'],'Published consensus hash differs'
        consensus=json.loads(consensus_path.read_text())
        assert consensus['status']==binding['status']=='ALL_THREE_APPROVE_EXACT_FINAL_CORRECTIONS'
        assert consensus['required_reviewers']==binding['required_reviewers']==['REVIEWER_A','REVIEWER_B','REVIEWER_C']
        assert consensus['ledger_sha256']==authority['source_ledger_sha256']==binding['ledger']['sha256']
        assert sorted(consensus['corrected_record_ids'])==binding['corrected_record_ids']
        previous=json.loads((root/authority['previous_authority']).read_bytes())
    ledger=json.loads(ledger_file.read_text())
    ledger={x['record_id']:x for x in ledger}
    assert set(rows)==set(ledger) and len(ledger)==authority.get('reviewed_population',425)
    for rid,row in rows.items():
        assert sha(root/row['archive_path'])==row['original_entry_sha256'],rid
        if corrected:
            digest=hashlib.sha256(json.dumps(ledger[rid],sort_keys=True,ensure_ascii=False,separators=(',',':')).encode()).hexdigest()
            assert digest==row['record_sha256']==row['decision_sha256'],rid
            assert row['human_approval_created'] is False,rid
            assert row.get('source_correspondence_flags',[])==ledger[rid].get('source_correspondence_flags',[]),rid
            assert row.get('source_correspondence')==ledger[rid].get('source_correspondence'),rid
            assert row['decision']==('retain' if ledger[rid]['release_status']=='RETAINED' else 'withdraw'),rid
        else:
            audit=ledger[rid]['audit']
            assert hashlib.sha256(json.dumps(audit,sort_keys=True,ensure_ascii=False).encode()).hexdigest()==row['audit_sha256'],rid
        if row['decision']=='withdraw':
            assert not (root/row['entry_path']).exists(),rid
            if corrected and previous['records'][rid]['decision']=='retain':
                record=ledger[rid];state=publish_corrected_review.source_state(record)
                assert state['status']==row['semantic_status']=='SOURCE_MISMATCH',rid
                assert row['reason']==state['reason'] and row['release_status']=='EXCLUDED',rid
                assert rid in binding['corrected_record_ids'],rid
                dossier=active_release.safe_path(root,row['withdrawal_dossier'])
                assert sha(dossier)==row['withdrawal_dossier_sha256'],rid
                assert sha(dossier.with_suffix('.json'))==row['withdrawal_dossier_json_sha256'],rid
                assert json.loads(dossier.with_suffix('.json').read_bytes())==record,rid
                check_supporting_evidence(root,rid,row,record)
                old=previous['records'][rid]
                assert row['historical_artifacts']=={key:old[key] for key in ('certificate','certificate_sha256','dossier','dossier_sha256') if key in old},rid
                assert not any(key in row for key in ('certificate','build_record','final_theorems')),rid
            continue
        assert sha(root/row['certificate'])==row['certificate_sha256']==ledger[rid]['lean_sha256'],rid
        assert sha(root/row['dossier'])==row['dossier_sha256'],rid
        dossier_json=(root/row['dossier']).with_suffix('.json')
        if corrected:
            assert sha(dossier_json)==row['dossier_json_sha256'],rid
            for asset in row['evidence_files']:
                assert sha(active_release.safe_path(root,asset['path']))==asset['sha256'],rid
            check_supporting_evidence(root,rid,row,ledger[rid])
        packet=json.loads(dossier_json.read_text())
        assert packet==ledger[rid],rid
        assert packet['release_status']=='RETAINED' and not packet['blockers'],rid
        proof=packet['build_record']
        assert proof['status']=='PASS' and proof['selected_theorems_present'],rid
        assert proof['selected_theorem_trust_tier']=='KERNEL_ONLY',rid
        assert {x['name'] for x in proof['selected_theorems']}==set(row['final_theorems']),rid
    if corrected:
        assert release_manifest['reviewed_population']==len(ledger)
        assert release_manifest['retained_reviewed']==len(kept)
        assert release_manifest['excluded_reviewed']==len(withdrawn)
        assert release_manifest['outside_review_unchanged']==len(active-kept)
        assert release_manifest['entry_count']==len(active)
        old_ledger=json.loads(active_release.safe_path(root,previous.get('ledger','releases/'+previous['release']+'/ledger.json')).read_bytes())
        assert binding['admission']==consensus['admission'],'Published admission roster differs from consensus'
        publish_corrected_review.validate_admission(consensus['admission'],old_ledger,list(ledger.values()),binding['corrected_record_ids'])
        plan=publish_corrected_review.withdrawal_plan(old_ledger,list(ledger.values()),previous['records'],authority['release'])
        assert authority.get('withdrawn_card_removals')==plan,'Withdrawal removal plan differs from ledger'
        assert sha(root/authority['previous_authority'])==authority['previous_authority_sha256']
        for name,pin in authority['outside_review_entries'].items():
            assert sha(active_release.safe_path(root,name))==pin,rid
        for name,pin in authority['retained_historical_files'].items():
            assert sha(active_release.safe_path(root,name))==pin,name
    with sqlite3.connect(active_release.database_path(root).resolve().as_uri()+'?mode=ro',uri=True) as db:
        assert db.execute('PRAGMA integrity_check').fetchone()==('ok',)
        for table,key in [('entries','id'),('entries_fts','id')]:
            assert {r[0] for r in db.execute('SELECT '+key+' FROM '+table)}==active,table
        for table,key in [('tags','entry_id'),('relations','entry_id'),('relations','related_id')]:
            assert {r[0] for r in db.execute('SELECT '+key+' FROM '+table)} <= active,table
        for rid,row in rows.items():
            if row['decision']=='retain':
                statement,refutes=db.execute('SELECT statement,refutes FROM entries WHERE id=?',(row['entry_id'],)).fetchone()
                assert statement==ledger[rid]['current_fields']['witness'].strip(),rid
                if corrected:
                    assert refutes==ledger[rid]['current_fields']['claim_quote'].strip(),rid
    site=root/'site/index.html'
    if corrected:
        assert site.is_file(),'Corrected release requires site/index.html'
    if site.exists():
        match=re.search(r'<script id="bugbank-data" type="application/json">(.*?)</script>',site.read_text(),re.S)
        data=json.loads(match.group(1))
        assert {x['id'] for x in data['entries']}==active
        assert all(set(x['related']) <= active for x in data['entries'])
        if corrected:
            expected_entries,projector=build_site.project_entries(root)
            assert data['entries']==expected_entries,'Rendered site content differs from canonical corrected cards'
            site_assets.validate(root,site.parent,expected_entries,projector.assets)
    result={'reviewed':len(ledger),'retained_with_dossier_and_kernel_proof':len(kept),'withdrawn':len(withdrawn),
            'active_bank_entries':len(active),'outside_review_unchanged':len(active-kept),'passed':True}
    print(json.dumps(result))
    return result

if __name__=='__main__':check()
