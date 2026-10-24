from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

import yaml

from scripts.qq_sync import (
    BUNDLE_SCHEMA_VERSION,
    BundleError,
    apply_plan,
    bootstrap_crosswalk,
    export_bundle,
    load_bundle,
    load_json,
    plan_sync,
)


def dossier(record_id: str, *, cert: Path | None = None, corpus: str = "ProofWiki") -> dict:
    compiled = cert is not None
    return {
        "record_id": record_id,
        "corpus": corpus,
        "problem": f"Problem for {record_id}",
        "quote": "The flagged claim.",
        "flaw": "Every object has the asserted property.",
        "witness": f"Witness for {record_id}.",
        "explanation": "Direct evaluation falsifies the conclusion.",
        "verification_notes": "Checked independently.",
        "link": "https://example.test/source",
        "attribution": "Fixture author",
        "full_ref": f"records/{record_id}.json",
        "lean_compiled": compiled,
        "lean_path": cert,
        "certificate_route": "SELF_CONTAINED_LEAN" if compiled else "DESCOPE",
        "lean_note": None if compiled else "faithful Lean unavailable",
    }


def metadata_for(record_id: str, *, publish: bool = True, management: str = "generated") -> dict:
    return {
        "schema_version": 1,
        "records": {
            record_id: {
                "entry_id": record_id.replace("_", "-").lower(),
                "title": f"Title for {record_id}",
                "domain": "algebra",
                "subdomain": "fixtures",
                "tags": ["fixture"],
                "difficulty": 2,
                "related": [],
                "publish": publish,
                "management": management,
            }
        },
    }


def read_frontmatter(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    return yaml.safe_load(text.split("---\n", 2)[1])


class BundleTests(unittest.TestCase):
    def test_export_is_versioned_deterministic_and_checksummed(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            source = root / "source"
            source.mkdir()
            cert = source / "certs" / "rec_one.lean"
            cert.parent.mkdir()
            cert.write_text("theorem checked : True := True.intro\n", encoding="utf-8")

            out1, out2 = root / "bundle1", root / "bundle2"
            export_bundle([dossier("rec_one", cert=cert)], source, "abc123", out1)
            export_bundle([dossier("rec_one", cert=cert)], source, "abc123", out2)

            self.assertEqual(
                (out1 / "manifest.json").read_bytes(),
                (out2 / "manifest.json").read_bytes(),
            )
            self.assertEqual(
                (out1 / "records.jsonl").read_bytes(),
                (out2 / "records.jsonl").read_bytes(),
            )
            bundle = load_bundle(out1)
            self.assertEqual(bundle.manifest["schema_version"], BUNDLE_SCHEMA_VERSION)
            self.assertEqual(bundle.manifest["source_commit"], "abc123")
            self.assertEqual(bundle.manifest["record_count"], 1)
            self.assertEqual(bundle.manifest["certificate_count"], 1)
            self.assertTrue(bundle.records["rec_one"]["certificate"]["sha256"])

    def test_tampered_certificate_is_rejected_before_sync(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            source = root / "source"
            source.mkdir()
            cert = source / "rec.lean"
            cert.write_text("theorem checked : True := True.intro\n", encoding="utf-8")
            out = root / "bundle"
            export_bundle([dossier("rec", cert=cert)], source, "abc123", out)
            bundle = load_bundle(out)
            cert_path = out / bundle.records["rec"]["certificate"]["bundle_path"]
            cert_path.write_text("tampered\n", encoding="utf-8")

            with self.assertRaises(BundleError):
                load_bundle(out)

    def test_export_scrubs_private_runtime_paths_from_public_fields(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            source = root / "source"
            source.mkdir()
            row = dossier("rec")
            row["verification_notes"] = (
                "ran with /nfs/private/project/venv/bin/python; exact arithmetic"
            )

            bundle = export_bundle([row], source, "abc123", root / "bundle")

            notes = bundle.records["rec"]["verification_notes"]
            self.assertNotIn("/nfs/", notes)
            self.assertIn("[private path omitted]", notes)

    def test_certificate_outside_source_checkout_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            source = root / "source"
            source.mkdir()
            outside = root / "outside.lean"
            outside.write_text("theorem checked : True := True.intro\n", encoding="utf-8")

            with self.assertRaises(BundleError):
                export_bundle([dossier("rec", cert=outside)], source, "abc123", root / "bundle")


class CrosswalkTests(unittest.TestCase):
    def test_bootstrap_captures_editorial_metadata_and_management(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            source = root / "source"
            source.mkdir()
            cert = source / "rec.lean"
            cert.write_text("theorem checked : True := True.intro\n", encoding="utf-8")
            bundle_dir = root / "bundle"
            export_bundle([dossier("rec", cert=cert)], source, "abc123", bundle_dir)
            bundle = load_bundle(bundle_dir)

            entry = root / "entries" / "algebra" / "rec.md"
            entry.parent.mkdir(parents=True)
            entry.write_text(
                """---
id: rec
title: Existing title
type: counterexample
domain: algebra
subdomain: groups
tags: [groups, machine-checked]
refutes: False claim
statement: Concrete witness
source:
  book: qedbench-canonical-600
  item: rec
difficulty: 3
status: verified
related: []
formalized: [lean/canonical600/rec.lean]
---

## Object

Existing body.
""",
                encoding="utf-8",
            )
            vendored = root / "lean" / "canonical600" / "rec.lean"
            vendored.parent.mkdir(parents=True)
            vendored.write_bytes(cert.read_bytes())

            metadata, state = bootstrap_crosswalk(root, bundle)

            self.assertEqual(metadata["records"]["rec"]["title"], "Existing title")
            self.assertEqual(metadata["records"]["rec"]["difficulty"], 3)
            self.assertTrue(metadata["records"]["rec"]["publish"])
            self.assertEqual(metadata["records"]["rec"]["management"], "generated")
            self.assertEqual(state["records"]["rec"]["source_commit"], "abc123")
            self.assertTrue(state["records"]["rec"]["entry_sha256"])


class SyncTests(unittest.TestCase):
    def _bundle(self, root: Path, row: dict, commit: str = "abc123"):
        out = root / f"bundle-{commit}"
        export_bundle([row], root / "source", commit, out)
        return load_bundle(out)

    def test_apply_new_record_is_idempotent_and_records_dynamic_provenance(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            source = root / "source"
            source.mkdir()
            cert = source / "rec.lean"
            cert.write_text("theorem checked : True := True.intro\n", encoding="utf-8")
            bundle = self._bundle(root, dossier("rec", cert=cert), "feed1234")
            metadata = metadata_for("rec")
            state = {"schema_version": 1, "records": {}}

            plan = plan_sync(bundle, metadata, state, root)
            self.assertEqual([(c.record_id, c.action) for c in plan.changes], [("rec", "create")])
            state = apply_plan(plan, bundle, metadata, state, root)

            entry = root / "entries" / "algebra" / "rec.md"
            front = read_frontmatter(entry)
            self.assertEqual(front["imported_from"]["commit"], "feed1234")
            self.assertEqual(front["status"], "verified")
            self.assertTrue((root / front["formalized"][0]).exists())
            self.assertEqual(state["records"]["rec"]["source_commit"], "feed1234")

            second = plan_sync(bundle, metadata, state, root)
            self.assertTrue(second.clean)
            self.assertEqual(second.changes, ())

    def test_descope_is_draft_and_quarantine_is_tagged(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "source").mkdir()
            row = dossier(
                "rec",
                corpus="Quarantined refutations (counterexample already published)",
            )
            bundle = self._bundle(root, row)
            metadata = metadata_for("rec")
            state = {"schema_version": 1, "records": {}}

            plan = plan_sync(bundle, metadata, state, root)
            apply_plan(plan, bundle, metadata, state, root)
            front = read_frontmatter(root / "entries" / "algebra" / "rec.md")

            self.assertEqual(front["status"], "draft")
            self.assertIn("previously-published", front["tags"])
            self.assertNotIn("formalized", front)

    def test_missing_metadata_and_unreleased_records_are_never_written(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "source").mkdir()
            bundle = self._bundle(root, dossier("rec"))
            state = {"schema_version": 1, "records": {}}

            missing = plan_sync(bundle, {"schema_version": 1, "records": {}}, state, root)
            self.assertEqual(missing.pending_metadata, ("rec",))
            self.assertTrue(missing.has_blockers)

            unreleased = plan_sync(bundle, metadata_for("rec", publish=False), state, root)
            self.assertEqual(unreleased.unreleased, ("rec",))
            self.assertFalse(unreleased.has_blockers)
            self.assertFalse((root / "entries").exists())

    def test_local_edit_blocks_an_upstream_update(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            source = root / "source"
            source.mkdir()
            cert = source / "rec.lean"
            cert.write_text("theorem checked : True := True.intro\n", encoding="utf-8")
            metadata = metadata_for("rec")
            state = {"schema_version": 1, "records": {}}
            bundle1 = self._bundle(root, dossier("rec", cert=cert), "one")
            plan1 = plan_sync(bundle1, metadata, state, root)
            state = apply_plan(plan1, bundle1, metadata, state, root)

            entry = root / "entries" / "algebra" / "rec.md"
            entry.write_text(entry.read_text() + "\nEditorial addition.\n", encoding="utf-8")
            changed = dossier("rec", cert=cert)
            changed["witness"] = "A changed upstream witness."
            bundle2 = self._bundle(root, changed, "two")

            plan2 = plan_sync(bundle2, metadata, state, root)
            self.assertEqual(plan2.conflicts, ("rec: local entry changed since last sync",))
            self.assertTrue(plan2.has_blockers)

    def test_descope_record_can_be_promoted_when_a_certificate_lands(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            source = root / "source"
            source.mkdir()
            metadata = metadata_for("rec")
            state = {"schema_version": 1, "records": {}}

            bundle1 = self._bundle(root, dossier("rec"), "one")
            state = apply_plan(
                plan_sync(bundle1, metadata, state, root),
                bundle1,
                metadata,
                state,
                root,
            )

            cert = source / "rec.lean"
            cert.write_text("theorem checked : True := True.intro\n", encoding="utf-8")
            bundle2 = self._bundle(root, dossier("rec", cert=cert), "two")
            plan = plan_sync(bundle2, metadata, state, root)

            self.assertEqual(plan.conflicts, ())
            self.assertEqual([(c.record_id, c.action) for c in plan.changes], [("rec", "update")])
            state = apply_plan(plan, bundle2, metadata, state, root)
            front = read_frontmatter(root / "entries" / "algebra" / "rec.md")
            self.assertEqual(front["status"], "verified")
            self.assertTrue((root / front["formalized"][0]).is_file())
            self.assertIn("certificate_sha256", state["records"]["rec"])

    def test_removed_source_record_requires_manual_resolution(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            source = root / "source"
            source.mkdir()
            out = root / "empty-bundle"
            export_bundle([], source, "two", out)
            bundle = load_bundle(out)
            state = {
                "schema_version": 1,
                "records": {
                    "gone": {
                        "record_sha256": "old",
                        "entry_path": "entries/algebra/gone.md",
                        "entry_sha256": "old",
                        "source_commit": "one",
                        "management": "generated",
                    }
                },
            }

            plan = plan_sync(bundle, {"schema_version": 1, "records": {}}, state, root)
            self.assertEqual(plan.removed, ("gone",))
            self.assertTrue(plan.has_blockers)

    def test_preserved_entry_checks_its_local_formalization_pointer(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            source = root / "source"
            source.mkdir()
            bundle = self._bundle(root, dossier("rec"))
            entry = root / "entries" / "algebra" / "rec.md"
            entry.parent.mkdir(parents=True)
            entry.write_text("preserved\n", encoding="utf-8")
            metadata = metadata_for("rec", management="preserve")
            metadata["records"]["rec"].update({
                "entry_path": "entries/algebra/rec.md",
                "formalized": ["lean/qedbench/missing.lean"],
            })
            state = {
                "schema_version": 1,
                "records": {
                    "rec": {
                        "record_sha256": bundle.records["rec"]["record_sha256"],
                        "entry_path": "entries/algebra/rec.md",
                        "entry_sha256": "not-used-for-preserve",
                        "source_commit": "abc123",
                        "management": "preserve",
                    }
                },
            }

            plan = plan_sync(bundle, metadata, state, root)

            self.assertIn("rec: formalized path is missing: lean/qedbench/missing.lean",
                          plan.conflicts)
            self.assertTrue(plan.has_blockers)


class WorkflowTests(unittest.TestCase):
    def test_sync_workflow_checks_out_private_source_and_opens_review_pr(self):
        workflow = Path(".github/workflows/sync-qq.yml").read_text(encoding="utf-8")
        self.assertIn("PROOF_VERIFICATION_TOKEN", workflow)
        self.assertIn("example/research-source", workflow)
        self.assertIn("scripts/qq_sync.py apply", workflow)
        self.assertIn("gh pr create", workflow)
        self.assertIn("schedule:", workflow)


if __name__ == "__main__":
    unittest.main()
