"""Corrected-version regressions; all mathematical fixtures are synthetic."""
import copy
import contextlib
import hashlib
import io
import json
import re
from urllib.parse import urljoin,urlsplit
from pathlib import Path
import shutil
import tempfile
import types
import unittest
from unittest import mock
import yaml
from scripts import active_release,build_db,build_site,check_active_review,check_release_database,qq_sync,site_assets
from scripts import publish_corrected_review as publish
import test_active_release

class CorrectedImportProtection(unittest.TestCase):
    setUp = test_active_release.ActiveReviewTests.setUp
    policy = test_active_release.ActiveReviewTests.policy
    def corrected_policy(self):
        self.policy('retain')
        path=self.root/'active_review.json';data=json.loads(path.read_text())
        data.update(schema=active_release.CORRECTED_SCHEMA,release='corrected_v2',ledger='releases/corrected_v2/ledger.json',
            manifest='releases/corrected_v2/MANIFEST.json',database='releases/corrected_v2/bugbank.sqlite',
            previous_authority='releases/corrected_v2/archive/active_review.json',source_ledger_sha256='b'*64)
        data['records']['rec']['record_sha256']='c'*64
        # Replace both YAML statement and body so an old import would be observable.
        corrected=self.original.replace(b'Witness for rec.',b'Corrected witness for rec.')
        self.entry.write_bytes(corrected);data['records']['rec']['entry_sha256']=hashlib.sha256(corrected).hexdigest()
        path.write_text(json.dumps(data));return corrected

    def test_v2_stale_import_cannot_restore_old_prose(self):
        corrected=self.corrected_policy()
        plan=qq_sync.plan_sync(self.bundle,self.metadata,self.state,self.root)
        self.assertEqual(plan.changes,())
        qq_sync.apply_plan(plan,self.bundle,self.metadata,self.state,self.root)
        self.assertEqual(self.entry.read_bytes(),corrected)
        with self.assertRaisesRegex(qq_sync.SyncError,'source-review authority'):
            qq_sync.apply_plan(self.plan,self.bundle,self.metadata,self.state,self.root)
        self.assertEqual(active_release.active_paths(self.root),[self.entry])

    def test_v2_unaudited_old_card_restore_fails_and_selects_new_database(self):
        self.corrected_policy()
        self.assertEqual(active_release.database_path(self.root),self.root/'releases/corrected_v2/bugbank.sqlite')
        self.entry.write_bytes(self.original)
        with self.assertRaisesRegex(ValueError,'changed without a new audit'):
            active_release.active_paths(self.root)

    def test_v2_withdrawal_stale_import_cannot_restore_card(self):
        self.corrected_policy()
        path=self.root/'active_review.json';authority=json.loads(path.read_bytes())
        authority['records']['rec']['decision']='withdraw';path.write_bytes(publish.jb(authority))
        self.entry.unlink()
        plan=qq_sync.plan_sync(self.bundle,self.metadata,self.state,self.root)
        self.assertEqual(plan.changes,())
        qq_sync.apply_plan(plan,self.bundle,self.metadata,self.state,self.root)
        self.assertFalse(self.entry.exists())
        self.assertEqual(active_release.active_paths(self.root),[])
        with self.assertRaisesRegex(qq_sync.SyncError,'source-review authority'):
            qq_sync.apply_plan(self.plan,self.bundle,self.metadata,self.state,self.root)

class VersionedPublisherTests(unittest.TestCase):
    def setUp(self):
        temp=tempfile.TemporaryDirectory();self.addCleanup(temp.cleanup)
        self.root=Path(temp.name)/'bank';self.root.mkdir();self.research=Path(temp.name)/'research';self.research.mkdir()
        self.expected={'reviewed':2,'retained':1,'withdrawn':1,'outside':1}
        for module in (build_db,build_site,check_release_database):
            patcher=mock.patch.object(module,'ROOT',self.root);patcher.start();self.addCleanup(patcher.stop)
        out=mock.patch.object(build_site,'OUT',self.root/'site');out.start();self.addCleanup(out.stop)
        (self.root/'sources.yaml').write_text('fixture: Synthetic fixture\n')
        (self.root/'entries/algebra').mkdir(parents=True)
        self.meta={'id':'kept','title':'Synthetic witness','type':'counterexample','domain':'algebra','subdomain':'fixture',
            'tags':['fixture'],'statement':'old witness','refutes':'old source quotation','difficulty':1,'status':'draft',
            'source':{'book':'fixture','item':'kept'},'related':[]}
        def card(meta):return ('---\n'+yaml.safe_dump(meta)+'---\n\nOld prose.\n').encode()
        self.card=card(self.meta);(self.root/'entries/algebra/kept.md').write_bytes(self.card)
        outside={**self.meta,'id':'outside','source':{'book':'fixture','item':'outside'}}
        (self.root/'lean/fixture_instances').mkdir(parents=True)
        (self.root/'lean/fixture_instances/example.lean').write_text('-- OUTSIDE-SCOPE SYNTHETIC PUBLIC PROOF')
        outside['formalized']=['lean/fixture_instances/']
        (self.root/'public_fixture').mkdir()
        (self.root/'public_fixture/note.txt').write_text('Outside-scope linked evidence, unchanged.')
        (self.root/'entries/algebra/outside.md').write_bytes(card(outside)+b'\n[Outside evidence](../../public_fixture/note.txt)\n')
        cert=b'-- SYNTHETIC TEST ONLY, not mathematical evidence\n'
        (self.research/'fixture.lean').write_bytes(cert)
        event={'name':'Fixture.checked','audit':{'name':'Fixture.checked','type':'True','unsafe':False,'disallowed_axioms':[],
            'native_candidate_axioms':[],'uses_native_reduction':False,'axioms':[]}}
        br={'status':'PASS','source_sha256':publish.sha(cert),'selected_theorems_present':True,
            'selected_theorem_trust_tier':'KERNEL_ONLY','selected_theorems':[event]}
        fields={'problem':'Frozen problem','source_context':'Frozen context','complete_source':'Frozen complete source',
            'claim_quote':'old source quotation','witness':'old witness','flaw':'old flaw','explanation':'old explanation'}
        self.old=[{'record_id':'kept','release_status':'RETAINED','current_fields':fields,'audit':{'synthetic_fixture':True},
            'lean_path':'fixture.lean','lean_sha256':publish.sha(cert),'evidence_tier':'KERNEL_ONLY','build_record':br,'blockers':[],
            'human_approval_of_current_artifact':'NOT_ESTABLISHED_BY_THIS_AUTOMATED_RELEASE','historical_human_reviews':[]},
            {'record_id':'withdrawn','release_status':'EXCLUDED','current_fields':{},'audit':{'synthetic_fixture':True}}]
        release=self.root/'releases/human_review_20260917';release.mkdir(parents=True)
        (release/'ledger.json').write_bytes(publish.jb(self.old))
        rows={}
        for rid in ('kept','withdrawn'):
            archive='releases/human_review_20260917/archive/'+rid+'.md';path=self.root/archive;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(self.card)
            audit=self.old[0 if rid=='kept' else 1]['audit']
            rows[rid]={'entry_id':rid,'entry_path':'entries/algebra/'+rid+'.md','archive_path':archive,
                'original_entry_sha256':publish.sha(self.card),'entry_sha256':publish.sha(self.card),
                'audit_sha256':hashlib.sha256(json.dumps(audit,sort_keys=True,ensure_ascii=False).encode()).hexdigest(),
                'decision':'retain' if rid=='kept' else 'withdraw'}
        self.authority={'schema':active_release.SCHEMA,'release':'human_review_20260917','reviewed_population':2,
            'database':'releases/human_review_20260917/bugbank.sqlite','source_ledger_sha256':publish.digest(release/'ledger.json'),'records':rows}
        (self.root/'active_review.json').write_bytes(publish.jb(self.authority))
        with contextlib.redirect_stdout(io.StringIO()):build_db.main()
        shutil.copyfile(self.root/self.authority['database'],self.root/'bugbank.sqlite')
        prev=self.root/'releases/previous.sqlite';shutil.copyfile(self.root/'bugbank.sqlite',prev)
        def dbrec(name):return {'path':name,'sha256':publish.digest(self.root/name),'entry_count':2}
        (release/'MANIFEST.json').write_bytes(publish.jb({'database':self.authority['database'],'database_sha256':publish.digest(self.root/self.authority['database']),
            'entry_count':2,'frozen_database':dbrec('bugbank.sqlite'),'previous_release':dbrec('releases/previous.sqlite')}))
        workflow=self.root/'.github/workflows/validate.yml';workflow.parent.mkdir(parents=True)
        workflow.write_text('run: python3 scripts/check_release_database.py --manifest releases/human_review_20260917/MANIFEST.json\n')
        (self.root/publish.MARKER).write_bytes(publish.jb({'source_bank':str(self.root.parent/'live_not_used'),
            'isolated_bank':str(self.root),'source_authority_sha256':publish.digest(self.root/'active_review.json')}))
        self.new=copy.deepcopy(self.old);r=self.new[0];r['current_fields'].update(witness='corrected witness',flaw='corrected flaw',explanation='corrected explanation')
        r.update(revised_artifact_requires_new_human_review=True,human_approval_of_current_artifact='NOT_ESTABLISHED_FOR_CORRECTED_VERSION',
            source_correspondence_flags=[{'status':'CANNOT_DETERMINE','reason':'The synthetic source convention is unspecified.'}],
            source_correspondence={'status':'CANNOT_DETERMINE','reason':'The source convention remains unspecified after author-side review.','evidence_ids':[]})
        approval=self.research/'SYNTHETIC_PUBLIC_EVIDENCE_APPROVAL.json'
        approval.write_bytes(publish.jb({'actual_reviewer':'SYNTHETIC_REVIEWER_NOT_REAL'}))
        r['public_supporting_evidence']=[]
        for eid,kind in [('source-excerpt','source_supplement'),('census-result','ancillary_computation')]:
            evidence=self.research/(eid+'.txt');evidence.write_text('SYNTHETIC '+kind+' evidence, not a research finding.')
            r['public_supporting_evidence'].append({'evidence_id':eid,'kind':kind,'label':'Synthetic '+kind,
                'path':evidence.name,'sha256':publish.digest(evidence),'accepted_by':'SYNTHETIC_REVIEWER_NOT_REAL',
                'approval_report':{'path':approval.name,'sha256':publish.digest(approval)}})
        self.ledger=self.research/'accepted_ledger.json';self.ledger.write_bytes(publish.jb(self.new))
        report=self.research/'SYNTHETIC_TEST_REVIEW.txt';report.write_text('Synthetic test fixture, not actual review evidence.')
        self.acceptance=self.research/'SYNTHETIC_TEST_ACCEPTANCE.json'
        verifier_path=self.research/publish.CONSENSUS_VERIFIER;verifier_path.parent.mkdir(parents=True)
        verifier_path.write_text('def verify_consensus_receipt(descriptor, ledger_descriptor=None):\n    raise ValueError("Synthetic verifier cannot approve an actual release")\n')
        self.consensus=self.research/'SYNTHETIC_CONSENSUS.json'
        self.consensus.write_bytes(publish.jb({'schema':'copeer-all-three-correction-consensus/v1',
            'status':'ALL_THREE_APPROVE_EXACT_FINAL_CORRECTIONS','required_reviewers':['REVIEWER_A','REVIEWER_B','REVIEWER_C'],
            'ledger_sha256':publish.digest(self.ledger),'builder_sha256':publish.digest(verifier_path),
            'corrected_record_ids':['kept']}))
        self.acceptance.write_bytes(publish.jb({'status':'APPROVED_FOR_BANK_STAGING','ledger_sha256':publish.digest(self.ledger),
            'consensus':{'path':self.consensus.name,'sha256':publish.digest(self.consensus)},
            'coordinator':'SYNTHETIC_TEST_ONLY','review_evidence':[{'path':report.name,'sha256':publish.digest(report)}]}))
        self.bind_fixture_ledger()
        # Consumer bridge unit tests explicitly mock provider replay. These are
        # not consensus approvals or a final accepted-ledger integration.
        def replay(descriptor,ledger_descriptor):
            self.assertEqual(descriptor['path'],self.consensus.name)
            self.assertEqual(ledger_descriptor['path'],self.ledger.name)
            return json.loads(self.consensus.read_bytes())
        self.replay=mock.Mock(side_effect=replay)
        self.loader=mock.patch.object(publish,'load_verifier_bytes',return_value=types.SimpleNamespace(verify_consensus_receipt=self.replay))
        self.loader.start();self.addCleanup(self.loader.stop)

    def build(self):return publish.build(self.root,self.research,self.ledger,self.acceptance,'corrected_fixture',self.expected)

    def bind_fixture_ledger(self):
        self.ledger.write_bytes(publish.jb(self.new))
        consensus=json.loads(self.consensus.read_bytes());consensus['ledger_sha256']=publish.digest(self.ledger)
        retained=sorted(r['record_id'] for r in self.new if r['release_status']=='RETAINED')
        excluded=sorted(r['record_id'] for r in self.new if r['release_status']=='EXCLUDED')
        newly_excluded=sorted(set(excluded)-{'withdrawn'})
        consensus['admission']={'schema':'current-resource-admission/v1',
            'historical_retained_record_ids':['kept'],'historical_excluded_record_ids':['withdrawn'],
            'current_retained_record_ids':retained,'current_excluded_record_ids':excluded,
            'newly_excluded_record_ids':newly_excluded,'current_retained_ids_sha256':publish.record_sha(retained),
            'counts':{'total_rows':2,'historical_retained':1,'historical_excluded':1,'current_retained':len(retained),
                'current_excluded':len(excluded),'newly_excluded':len(newly_excluded)},
            'corrected_execution_record_ids':['kept'],'current_retained_corrected_record_ids':retained,
            'diagnostic_only_corrected_record_ids':newly_excluded,'diagnostic_only_excluded_from_current_metrics':True,
            'execution_policy':'Synthetic fixture. No actual execution or approval.'}
        self.consensus.write_bytes(publish.jb(consensus))
        acceptance=json.loads(self.acceptance.read_bytes());acceptance['ledger_sha256']=publish.digest(self.ledger)
        acceptance['consensus']['sha256']=publish.digest(self.consensus)
        self.acceptance.write_bytes(publish.jb(acceptance))

    def withdrawal_fixture(self):
        # Synthetic approval replay is still mocked; no actual R221 decision.
        r=self.new[0];r['release_status']='EXCLUDED'
        r['source_correspondence']={'status':'SOURCE_MISMATCH',
            'reason':'The accepted synthetic source supplement shows that the objection targets a different source claim.',
            'evidence_ids':['source-excerpt']}
        self.bind_fixture_ledger();self.expected=None # Production derives counts, including zero retained.
        cert='lean/prior_fixture/kept.lean';dossier='dossiers/prior_fixture/kept.html'
        (self.root/cert).parent.mkdir(parents=True);(self.root/cert).write_bytes(b'-- Historical selected proof; not source validation.\n')
        (self.root/dossier).parent.mkdir(parents=True);(self.root/dossier).write_bytes(b'<html><a href="../../lean/prior_fixture/kept.lean">Historical proof</a></html>')
        row=self.authority['records']['kept'];row.update(certificate=cert,certificate_sha256=publish.digest(self.root/cert),
            dossier=dossier,dossier_sha256=publish.digest(self.root/dossier))
        (self.root/'active_review.json').write_bytes(publish.jb(self.authority))
        marker=json.loads((self.root/publish.MARKER).read_bytes());marker['source_authority_sha256']=publish.digest(self.root/'active_review.json')
        (self.root/publish.MARKER).write_bytes(publish.jb(marker))

    def test_source_mismatch_withdrawal_updates_current_consumers_preserves_history(self):
        self.withdrawal_fixture()
        old_authority=(self.root/'active_review.json').read_bytes()
        frozen=publish.digest(self.root/'bugbank.sqlite')
        historical={str(p.relative_to(self.root)):p.read_bytes() for folder in ('releases','lean','dossiers')
            for p in (self.root/folder).rglob('*') if p.is_file()}
        outputs,authority,receipt=self.build()
        self.assertEqual(receipt['counts'],{'reviewed':2,'retained':0,'withdrawn':2,'outside':1,'active':1})
        publish.stage(outputs,self.root,self.research)
        with contextlib.redirect_stdout(io.StringIO()):build_db.main()
        manifest=publish.finish_manifest(self.root,authority,receipt)
        with contextlib.redirect_stdout(io.StringIO()):build_site.main()
        with contextlib.redirect_stdout(io.StringIO()):
            checked=check_active_review.check(self.root)
            logical=check_release_database.check_release(self.root/authority['manifest'])
        self.assertEqual(logical['result'],'PASS');self.assertEqual(checked['active_bank_entries'],1)
        self.assertEqual(manifest['excluded_reviewed'],2);self.assertEqual(manifest['retained_reviewed'],0)
        row=authority['records']['kept']
        self.assertEqual(row['decision'],'withdraw');self.assertEqual(row['semantic_status'],'SOURCE_MISMATCH')
        self.assertEqual((self.root/row['archive_path']).read_bytes(),self.card)
        self.assertEqual((self.root/authority['previous_authority']).read_bytes(),old_authority)
        self.assertEqual(publish.digest(self.root/'bugbank.sqlite'),frozen)
        self.assertFalse((self.root/'entries/algebra/kept.md').exists())
        self.assertEqual(json.loads((self.root/authority['ledger']).read_bytes()),self.new)
        for path,raw in historical.items():self.assertEqual((self.root/path).read_bytes(),raw,path)
        entries,projector=build_site.project_entries(self.root)
        self.assertEqual([e['id'] for e in entries],['outside'])
        site_assets.validate(self.root,self.root/'site',entries,projector.assets)
        html=(self.root/'site/bank'/row['withdrawal_dossier']).read_text()
        self.assertIn('excluded from the current active bank',html)
        self.assertIn('SOURCE_MISMATCH',html)
        self.assertTrue(all((self.root/'site/bank'/b['vendored_path']).is_file() for b in row['public_supporting_evidence']))
        # A stale current card is rejected, even though active_paths excludes it.
        (self.root/'entries/algebra/kept.md').write_bytes(self.card)
        with self.assertRaises(AssertionError):check_active_review.check(self.root)

    def test_withdrawal_prewrite_tamper_guards_preserve_bank(self):
        self.withdrawal_fixture();outputs,authority,_=self.build()
        original_authority=(self.root/'active_review.json').read_bytes()
        item=authority['withdrawn_card_removals'][0];card=self.root/item['entry_path']
        historic=self.root/authority['records']['kept']['historical_artifacts']['certificate']
        for mutation in ('archive','removal_hash','outside_target','card','historical','ledger','replay'):
            with self.subTest(mutation=mutation):
                changed=dict(outputs);saved=historic.read_bytes()
                if mutation=='archive':changed[self.root/item['archive_path']]=b'not the archived card'
                if mutation in {'removal_hash','outside_target'}:
                    data=json.loads(changed[self.root/'active_review.json'])
                    data['withdrawn_card_removals'][0]['entry_sha256' if mutation=='removal_hash' else 'entry_path']='0'*64 if mutation=='removal_hash' else 'entries/algebra/outside.md'
                    changed[self.root/'active_review.json']=publish.jb(data)
                if mutation=='card':card.write_bytes(b'changed card')
                if mutation=='historical':historic.write_bytes(b'changed historical proof')
                if mutation=='ledger':changed[self.root/authority['ledger']]=b'[]'
                if mutation=='replay':self.replay.side_effect=ValueError('No real all-three withdrawal approval')
                with self.assertRaises(ValueError):publish.stage(changed,self.root,self.research)
                self.assertEqual((self.root/'active_review.json').read_bytes(),original_authority)
                self.assertFalse((self.root/'releases/corrected_fixture').exists())
                card.write_bytes(self.card);historic.write_bytes(saved)

    def test_withdrawal_requires_source_mismatch_accepted_supplement_and_no_human_transfer(self):
        self.withdrawal_fixture()
        for mutation in ('status','retained_mismatch','reason','no_evidence','computation_only','human','historical_restore'):
            changed=copy.deepcopy(self.new)
            with self.subTest(mutation=mutation):
                if mutation=='status':changed[0]['source_correspondence']['status']='CANNOT_DETERMINE'
                if mutation=='retained_mismatch':changed[0]['release_status']='RETAINED'
                if mutation=='reason':changed[0]['source_correspondence']['reason']='short'
                if mutation=='no_evidence':changed[0]['public_supporting_evidence']=[]
                if mutation=='computation_only':changed[0]['source_correspondence']['evidence_ids']=['census-result']
                if mutation=='human':changed[0]['human_approval_of_current_artifact']='APPROVED_BY_HUMAN'
                if mutation=='historical_restore':changed[1]['release_status']='RETAINED'
                with self.assertRaises(ValueError):publish.validate_ledger(self.old,changed)
        supplement=self.research/'source-excerpt.txt';supplement.write_bytes(b'changed mismatch evidence')
        with self.assertRaisesRegex(ValueError,'Evidence hash differs'):self.build()
        self.assertFalse((self.root/'releases/corrected_fixture').exists())

    def test_withdrawal_consensus_admission_roster_tamper_refused(self):
        self.withdrawal_fixture();original=json.loads(self.consensus.read_bytes())
        for field,value in [('current_retained_record_ids',['kept']),('newly_excluded_record_ids',[]),
                            ('diagnostic_only_corrected_record_ids',[]),('diagnostic_only_excluded_from_current_metrics',False),
                            ('current_retained_ids_sha256','0'*64)]:
            with self.subTest(field=field):
                changed=copy.deepcopy(original);changed['admission'][field]=value
                self.consensus.write_bytes(publish.jb(changed))
                acceptance=json.loads(self.acceptance.read_bytes());acceptance['consensus']['sha256']=publish.digest(self.consensus)
                self.acceptance.write_bytes(publish.jb(acceptance))
                with self.assertRaisesRegex(ValueError,'admission roster'):self.build()
                self.assertFalse((self.root/'releases/corrected_fixture').exists())

    def test_versioned_refresh_updates_all_consumers_preserves_historical_and_outside(self):
        frozen=publish.digest(self.root/'bugbank.sqlite');outside=(self.root/'entries/algebra/outside.md').read_bytes()
        outputs,authority,receipt=self.build();publish.stage(outputs,self.root,self.research)
        with contextlib.redirect_stdout(io.StringIO()):build_db.main()
        manifest=publish.finish_manifest(self.root,authority,receipt)
        with contextlib.redirect_stdout(io.StringIO()):build_site.main()
        with contextlib.redirect_stdout(io.StringIO()):
            result=check_active_review.check(self.root)
            logical=check_release_database.check_release(self.root/authority['manifest'])
        self.assertTrue(result['passed']);self.assertEqual(logical['result'],'PASS')
        self.assertEqual(publish.digest(self.root/'bugbank.sqlite'),frozen)
        self.assertEqual((self.root/'entries/algebra/outside.md').read_bytes(),outside)
        self.assertFalse((self.root/'entries/algebra/withdrawn.md').exists())
        raw=(self.root/'entries/algebra/kept.md').read_text();meta=publish.parse_card(raw.encode())
        self.assertEqual(meta['statement'],'corrected witness');self.assertEqual(meta['status'],'draft')
        self.assertIn('CANNOT_DETERMINE',raw);self.assertNotIn('old explanation',raw)
        self.assertEqual(manifest['database'],'releases/corrected_fixture/bugbank.sqlite')
        self.assertIn('--manifest releases/corrected_fixture/MANIFEST.json',(self.root/'.github/workflows/validate.yml').read_text())
        manifest_path=self.root/authority['manifest'];original_manifest=manifest_path.read_bytes()
        tampered=json.loads(original_manifest);tampered['active_review_sha256']='0'*64
        manifest_path.write_bytes(publish.jb(tampered))
        with self.assertRaisesRegex(AssertionError,'Authority/manifest'):
            check_active_review.check(self.root)
        manifest_path.write_bytes(original_manifest)
        (self.root/'dossiers/corrected_fixture/kept.json').write_bytes(b'{}')
        with self.assertRaises(AssertionError):check_active_review.check(self.root)

    def staged_fixture(self):
        outputs,authority,receipt=self.build();publish.stage(outputs,self.root,self.research)
        with contextlib.redirect_stdout(io.StringIO()):build_db.main()
        publish.finish_manifest(self.root,authority,receipt)
        with contextlib.redirect_stdout(io.StringIO()):build_site.main()
        return authority

    def test_deployment_links_at_project_subpath_corrected_and_outside(self):
        authority=self.staged_fixture()
        entries,projector=build_site.project_entries(self.root)
        site_assets.validate(self.root,self.root/'site',entries,projector.assets)
        for entry in entries:
            urls=[m['target'].strip('<>') for m in site_assets.MD_LINK.finditer(entry['body'])]+entry['formalized']
            self.assertTrue(urls,entry['id'])
            for url in urls:
                if site_assets.is_external(url):continue
                deployed=urljoin('https://example.invalid/project/index.html',url)
                self.assertTrue(urlsplit(deployed).path.startswith('/project/bank/'),deployed)
                self.assertTrue((self.root/'site'/urlsplit(url).path).is_file(),url)
        row=authority['records']['kept']
        dossier=(self.root/'site/bank'/row['dossier']).read_text()
        self.assertIn('Synthetic source_supplement',dossier)
        self.assertIn('Synthetic ancillary_computation',dossier)
        for binding in row['public_supporting_evidence']:
            self.assertEqual(publish.digest(self.root/'site/bank'/binding['vendored_path']),binding['sha256'])
        missing=self.root/'site/bank'/row['public_supporting_evidence'][0]['vendored_path'];missing.unlink()
        with self.assertRaisesRegex(ValueError,'deployed asset'):
            check_active_review.check(self.root)

    def test_stale_site_content_or_missing_site_refused(self):
        self.staged_fixture();path=self.root/'site/index.html';raw=path.read_text()
        match=re.search(r'(<script id="bugbank-data" type="application/json">)(.*?)(</script>)',raw,re.S)
        original=json.loads(match[2])
        for field in ('statement','refutes','body','status','formalized','source_correspondence_status'):
            with self.subTest(field=field):
                changed=copy.deepcopy(original)
                changed['entries'][0][field]=['stale.lean'] if field=='formalized' else 'STALE_SITE_VALUE'
                replacement=json.dumps(changed,ensure_ascii=False).replace('</','<\\/')
                path.write_text(raw[:match.start(2)]+replacement+raw[match.end(2):])
                with self.assertRaisesRegex(AssertionError,'Rendered site content'):
                    check_active_review.check(self.root)
        path.unlink()
        with self.assertRaisesRegex(AssertionError,'requires site/index.html'):
            check_active_review.check(self.root)

    def test_missing_or_changed_supporting_evidence_fails_before_staging(self):
        path=self.research/self.new[0]['public_supporting_evidence'][0]['path']
        original=path.read_bytes();path.write_bytes(b'changed')
        with self.assertRaisesRegex(ValueError,'Evidence hash differs'):self.build()
        path.unlink()
        with self.assertRaises(FileNotFoundError):self.build()
        self.assertFalse((self.root/'releases/corrected_fixture').exists())
        path.write_bytes(original)
        wrong=copy.deepcopy(self.new[0]);wrong['public_supporting_evidence'][0]['accepted_by']='UNVERIFIED_OTHER_REVIEWER'
        with self.assertRaisesRegex(ValueError,'approval identity'):
            publish.supporting_assets(wrong,self.research,'corrected_fixture')

    def test_resolved_supplement_keeps_historical_flag_without_active_uncertainty(self):
        row=copy.deepcopy(self.new[0]);row['source_correspondence_flags'][0]['status']='SOURCE_LIMITED'
        row['source_correspondence']={'status':'RESOLVED_WITH_SOURCE_SUPPLEMENT',
            'reason':'Author-side review resolves the displayed comparator using the accepted dated source supplement.',
            'evidence_ids':['source-excerpt']}
        publish.supporting_assets(row,self.research,'corrected_fixture')
        raw=publish.render_card(self.meta,row,'corrected_fixture','lean/new.lean','dossiers/new.html','archive/old.md')
        meta=publish.parse_card(raw)
        self.assertEqual(meta['status'],'verified')
        self.assertEqual(meta['source_correspondence_status'],'RESOLVED_WITH_SOURCE_SUPPLEMENT')
        self.assertIn(b'SOURCE_LIMITED',raw)
        self.assertNotIn(b'### Unresolved source correspondence',raw)
        row['source_correspondence']['evidence_ids']=[]
        with self.assertRaisesRegex(ValueError,'accepted source supplement'):publish.source_state(row)
        row.pop('source_correspondence')
        self.assertEqual(publish.source_state(row)['status'],'SOURCE_LIMITED')
        meta=publish.parse_card(publish.render_card(self.meta,row,'corrected_fixture','lean/new.lean','dossiers/new.html','archive/old.md'))
        self.assertEqual(meta['status'],'draft')

    def test_preserved_source_flags_stay_uncertain_without_new_approval(self):
        row=copy.deepcopy(self.new[0]);row.pop('source_correspondence')
        for state in ('SOURCE_LIMITED','CANNOT_DETERMINE','UNRESOLVED'):
            row['source_correspondence_flags'][0]['status']=state
            before=copy.deepcopy(row)
            projected=publish.source_state(row)
            self.assertEqual(projected,{'status':state,
                'reason':'No separately reviewed active status supplied; preserved source flags remain applicable.',
                'evidence_ids':[]})
            raw=publish.render_card(self.meta,row,'corrected_fixture','lean/new.lean','dossiers/new.html','archive/old.md')
            meta=publish.parse_card(raw)
            self.assertEqual(meta['status'],'draft')
            self.assertEqual(meta['source_correspondence_status'],state)
            self.assertIn(b'not new human approval',raw)
            self.assertEqual(row,before)
        row['source_correspondence_flags'] += [{'status':'CANNOT_DETERMINE','reason':'A second preserved source limitation.'}]
        self.assertEqual(publish.source_state(row)['status'],'UNRESOLVED')
        row['source_correspondence_flags'][0]['status']='AUTHOR_REVIEWED'
        with self.assertRaisesRegex(ValueError,'Unsupported historical'):publish.source_state(row)

    def test_literal_function_evaluation_is_not_a_site_link(self):
        p=site_assets.Projector(self.root)
        entry={'body':'[(f⊕g)∘(f⊕h)](1)=1.','formalized':[]}
        projected=p.entry(entry,self.root/'entries/algebra/kept.md')
        self.assertEqual(projected['body'],'\\[(f⊕g)∘(f⊕h)](1)=1.')
        self.assertEqual(list(site_assets.MD_LINK.finditer(projected['body'])),[])
        self.assertEqual(p.assets,{})

    def test_v1_optional_site_behavior_remains_available(self):
        authority=self.staged_fixture()
        authority['schema']=active_release.SCHEMA
        for record in self.new:
            authority['records'][record['record_id']]['audit_sha256']=hashlib.sha256(
                json.dumps(record['audit'],sort_keys=True,ensure_ascii=False).encode()).hexdigest()
        (self.root/'active_review.json').write_bytes(publish.jb(authority))
        (self.root/'site/index.html').unlink()
        with contextlib.redirect_stdout(io.StringIO()):result=check_active_review.check(self.root)
        self.assertTrue(result['passed'])

    def test_mandatory_consensus_absent_or_wrong_ledger_or_missing_reviewer_refused(self):
        original=self.acceptance.read_bytes();acceptance=json.loads(original);acceptance.pop('consensus')
        self.acceptance.write_bytes(publish.jb(acceptance))
        with self.assertRaisesRegex(ValueError,'Mandatory all-three'):self.build()
        self.acceptance.write_bytes(original)
        consensus=json.loads(self.consensus.read_bytes())
        for key,value,match in [('ledger_sha256','0'*64,'different final ledger'),
                                 ('required_reviewers',['REVIEWER_A','REVIEWER_B'],'three actual reviewer'),
                                 ('corrected_record_ids',[],'every final changed')]:
            changed={**consensus,key:value};self.consensus.write_bytes(publish.jb(changed))
            acceptance=json.loads(original);acceptance['consensus']['sha256']=publish.digest(self.consensus)
            self.acceptance.write_bytes(publish.jb(acceptance))
            with self.assertRaisesRegex(ValueError,match):self.build()
        self.assertFalse((self.root/'releases/corrected_fixture').exists())

    def test_real_verifier_invocation_failure_propagates_and_code_hash_is_bound(self):
        self.loader.stop() # Execute the synthetic verifier that refuses, not a simulated approval.
        with self.assertRaisesRegex(ValueError,'cannot approve an actual release'):self.build()
        path=self.research/publish.CONSENSUS_VERIFIER;path.write_text('# changed verifier bytes')
        with self.assertRaisesRegex(ValueError,'Evidence hash differs'):self.build()
        self.assertFalse((self.root/'releases/corrected_fixture').exists())

    def test_consensus_replayed_again_before_write_and_failure_leaves_bank_unchanged(self):
        outputs,authority,receipt=self.build();before=(self.root/'active_review.json').read_bytes()
        self.assertEqual(self.replay.call_count,1)
        self.replay.side_effect=ValueError('Actual consensus replay rejects changed approval bytes')
        with self.assertRaisesRegex(ValueError,'changed approval bytes'):
            publish.stage(outputs,self.root,self.research)
        self.assertEqual((self.root/'active_review.json').read_bytes(),before)
        self.assertFalse((self.root/'releases/corrected_fixture').exists())
        self.assertEqual(self.replay.call_count,2)

    def test_absolute_equivalent_descriptors_are_portable_without_changing_hashes(self):
        row=copy.deepcopy(self.new[0]);descriptor=row['public_supporting_evidence'][0]
        descriptor['path']=str(self.research/descriptor['path'])
        descriptor['approval_report']['path']=str(self.research/descriptor['approval_report']['path'])
        original=copy.deepcopy(descriptor)
        assets,bindings=publish.supporting_assets(row,self.research,'corrected_fixture')
        bound=bindings[0]
        self.assertEqual(bound['path'],'source-excerpt.txt')
        self.assertEqual(bound['original_path'],'source-excerpt.txt')
        self.assertEqual(bound['approval_report']['path'],'SYNTHETIC_PUBLIC_EVIDENCE_APPROVAL.json')
        self.assertEqual(bound['sha256'],original['sha256'])
        self.assertEqual(bound['source_descriptor_sha256'],publish.record_sha(original))
        self.assertEqual(descriptor,original)
        self.assertEqual(publish.sha(assets[bound['vendored_path']]),original['sha256'])
        with self.assertRaisesRegex(ValueError,'outside research root'):
            publish.canonical_descriptor(self.research,{'path':'../outside.txt','sha256':'0'*64})
        with self.assertRaisesRegex(ValueError,'Evidence hash differs'):
            publish.read_bound(self.research,{'path':original['path'],'sha256':'0'*64})

    def test_live_unmarked_checkout_and_unaccepted_ledger_refused(self):
        marker=(self.root/publish.MARKER).read_bytes();(self.root/publish.MARKER).unlink()
        with self.assertRaisesRegex(ValueError,'isolated'):self.build()
        (self.root/publish.MARKER).write_bytes(marker)
        self.acceptance.write_bytes(publish.jb({'status':'PENDING','ledger_sha256':publish.digest(self.ledger)}))
        with self.assertRaisesRegex(ValueError,'not approved'):self.build()

    def test_source_mutation_withdrawal_restore_and_human_approval_refused(self):
        for kind in ('source','withdrawal','human'):
            changed=copy.deepcopy(self.new)
            if kind=='source':changed[0]['current_fields']['problem']='changed source'
            if kind=='withdrawal':changed[1]['release_status']='RETAINED'
            if kind=='human':changed[0]['human_approval_of_current_artifact']='YES_FROM_AUTHOR_QA'
            with self.assertRaises(ValueError):publish.validate_ledger(self.old,changed,self.expected)

if __name__=='__main__':unittest.main()
