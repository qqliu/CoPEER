import contextlib
import hashlib
import io
import json
from pathlib import Path
import sqlite3
import tempfile
import unittest
from unittest import mock
import yaml
from scripts import active_release, build_db, build_site, qq_sync
from test_qq_sync_full import dossier, metadata_for

class ActiveReviewTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root/'source').mkdir()
        (self.root/'sources.yaml').write_text('qedbench-canonical-600: Fixture source\n')
        qq_sync.export_bundle([dossier('rec')],self.root/'source','frozen',self.root/'bundle')
        self.bundle = qq_sync.load_bundle(self.root/'bundle')
        self.metadata = metadata_for('rec')
        self.state = {'schema_version':1,'records':{}}
        self.plan = qq_sync.plan_sync(self.bundle,self.metadata,self.state,self.root)
        self.state = qq_sync.apply_plan(self.plan,self.bundle,self.metadata,self.state,self.root)
        self.entry = self.root/'entries/algebra/rec.md'
        self.original = self.entry.read_bytes()

    def policy(self, decision='withdraw'):
        archive=self.root/'archive/rec.md';archive.parent.mkdir(exist_ok=True);archive.write_bytes(self.original)
        row={'entry_id':'rec','entry_path':'entries/algebra/rec.md','archive_path':'archive/rec.md',
          'original_entry_sha256':hashlib.sha256(self.original).hexdigest(),'audit_sha256':'a'*64,
          'entry_sha256':hashlib.sha256(self.original).hexdigest(),'decision':decision}
        (self.root/'active_review.json').write_text(json.dumps({'schema':active_release.SCHEMA,'records':{'rec':row}}))

    def test_withdrawal_survives_rebuild_including_restored_old_markdown(self):
        self.policy()
        # Keep the old file deliberately: both build surfaces must ignore it.
        self.assertEqual(active_release.active_paths(self.root),[])
        with mock.patch.object(build_db,'ROOT',self.root),contextlib.redirect_stdout(io.StringIO()):
            build_db.main(self.root/'new.sqlite')
        with sqlite3.connect(self.root/'new.sqlite') as db:
            for table in ['entries','tags','relations','entries_fts']:
                self.assertEqual(db.execute('SELECT COUNT(*) FROM '+table).fetchone()[0],0)
        with mock.patch.object(build_site,'ROOT',self.root),mock.patch.object(build_site,'OUT',self.root/'site'),contextlib.redirect_stdout(io.StringIO()):
            build_site.main()
        self.assertNotIn('Witness for rec.',(self.root/'site/index.html').read_text())

    def test_stale_metadata_and_precomputed_plan_cannot_reimport(self):
        self.policy();self.entry.unlink()
        plan=qq_sync.plan_sync(self.bundle,self.metadata,self.state,self.root)
        self.assertEqual(plan.changes,());self.assertEqual(plan.unreleased,('rec',))
        qq_sync.apply_plan(plan,self.bundle,self.metadata,self.state,self.root)
        self.assertFalse(self.entry.exists())
        with self.assertRaisesRegex(qq_sync.SyncError,'source-review authority'):
            qq_sync.apply_plan(self.plan,self.bundle,self.metadata,self.state,self.root)

    def test_bootstrap_does_not_republish_archived_entry(self):
        self.policy();self.entry.unlink()
        meta,state=qq_sync.bootstrap_crosswalk(self.root,self.bundle)
        self.assertFalse(meta['records']['rec']['publish'])
        self.assertEqual(meta['records']['rec']['entry_path'],'entries/algebra/rec.md')
        self.assertEqual(qq_sync.plan_sync(self.bundle,meta,state,self.root).changes,())

    def test_retained_repair_is_hash_bound_and_protected_from_old_bundle(self):
        self.policy('retain')
        self.assertEqual(active_release.active_paths(self.root),[self.entry])
        self.assertEqual(qq_sync.plan_sync(self.bundle,self.metadata,self.state,self.root).changes,())
        self.entry.write_bytes(self.original+b'Unaudited change')
        with self.assertRaisesRegex(ValueError,'changed without a new audit'):
            active_release.active_paths(self.root)

    def test_unknown_relations_still_fail_but_withdrawn_relations_are_pruned(self):
        self.policy()
        rows=active_release.load(self.root)
        entries=active_release.prune_relations([{'related':['rec','unknown']}],rows)
        self.assertEqual(entries[0]['related'],['unknown'])

if __name__=='__main__':unittest.main()
