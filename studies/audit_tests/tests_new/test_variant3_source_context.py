"""Variant (3), changed source context, and the stale-hash contrast.

Existing coverage of variant (3) was PARTIAL and identity-binding only
(fresh_record_wrong_freeze_rejected, shared_source_and_native_contract_drift_rejected,
test_original_source_problem_change_refused). This file measures how deep that
identity binding goes and where it stops, on both pipelines, and records the
stopping point as an expected NON-detection rather than forcing a pass.

Levels tested, per pipeline:
  L1 unbound      the bytes change, the pinned hash does not          -> expect DETECTED
  L2 partly bound the manifest/authority is re-pinned but the already
                  issued receipts still carry the previous stamps     -> expect DETECTED
  L3 fully bound  every hash that mentions the changed artifact is
                  recomputed consistently                            -> measured, and
                  found NOT DETECTED; the semantic content of the
                  source is never re-derived from anything external.

All fixtures are synthetic; no Lean, no model call, no network.
"""
import json
import unittest

import integrity_replay_common as c


class PublishSideSourceContext(unittest.TestCase):
    """publish_corrected_review: current_fields['source_context'] of a record."""

    setUp = c.tcr.VersionedPublisherTests.setUp
    build = c.tcr.VersionedPublisherTests.build
    bind_fixture_ledger = c.tcr.VersionedPublisherTests.bind_fixture_ledger

    def test_positive_control_untouched_source_context_is_accepted(self):
        _outputs, _authority, receipt = self.build()
        self.assertEqual(receipt['counts']['retained'], 1)

    def test_L1_unbound_source_context_change_is_refused(self):
        """Identity: the new ledger disagrees with the frozen prior ledger."""
        self.new[0]['current_fields']['source_context'] = 'TAMPERED SYNTHETIC CONTEXT'
        self.bind_fixture_ledger()
        with self.assertRaisesRegex(ValueError, 'Original source/problem changed'):
            self.build()

    def test_L1_unbound_problem_and_complete_source_changes_are_refused(self):
        for field in ('problem', 'complete_source'):
            with self.subTest(field=field):
                self.setUp()
                self.new[0]['current_fields'][field] = 'TAMPERED SYNTHETIC ' + field.upper()
                self.bind_fixture_ledger()
                with self.assertRaisesRegex(ValueError, 'Original source/problem changed'):
                    self.build()

    def test_L2_stale_receipt_prior_ledger_hash_drift_is_refused(self):
        """Identity contrast (variant 2 mechanism): prior ledger bytes edited,
        active_review.json's source_ledger_sha256 left stale."""
        prior = c.read_prior_ledger(self)
        prior[0]['current_fields']['source_context'] = 'REWRITTEN SYNTHETIC CONTEXT'
        c.write_prior_ledger(self, prior)
        with self.assertRaisesRegex(ValueError, 'Previous active ledger hash drift'):
            self.build()

    def test_L2_stale_isolation_marker_authority_drift_is_refused(self):
        prior = c.read_prior_ledger(self)
        prior[0]['current_fields']['source_context'] = 'REWRITTEN SYNTHETIC CONTEXT'
        c.write_prior_ledger(self, prior)
        authority = json.loads((self.root / 'active_review.json').read_bytes())
        authority['source_ledger_sha256'] = c.publish.digest(self.root / c.OLD_LEDGER_REL)
        (self.root / 'active_review.json').write_bytes(c.publish.jb(authority))
        # marker still pins the previous active_review.json bytes
        with self.assertRaisesRegex(ValueError, 'Isolated authority drift since checkout preparation'):
            self.build()

    def test_L3_consistently_rebound_source_context_change_is_NOT_detected(self):
        """EXPECTED NON-DETECTION, measured, not worked around.

        The same semantic edit applied to the prior ledger, the new ledger, the
        authority and the isolation marker is accepted: every equality the
        validator checks is an equality between two artifacts the editor rewrote.
        No mechanical stage re-reads the actual source to see that the context
        no longer says what it said. This is the gap Experiment A addresses.
        """
        rewritten = 'REBOUND SYNTHETIC CONTEXT (semantically different, consistently re-pinned)'
        prior = c.read_prior_ledger(self)
        prior[0]['current_fields']['source_context'] = rewritten
        c.write_prior_ledger(self, prior)
        self.new[0]['current_fields']['source_context'] = rewritten
        self.bind_fixture_ledger()
        c.rebind_bank_authority(self)

        _outputs, authority, receipt = self.build()
        self.assertEqual(receipt['counts'],
                         {'reviewed': 2, 'retained': 1, 'withdrawn': 1, 'outside': 1, 'active': 2})
        staged = json.loads(_outputs[self.root / authority['ledger']])
        self.assertEqual(staged[0]['current_fields']['source_context'], rewritten)


class ScorerSideReferenceLines(unittest.TestCase):
    """resolve_and_score_corrected: item['lines'] of a reference item."""

    def setUp(self):
        self.f = c.Fixture()

    def test_positive_control_untouched_reference_resolves_and_accounts(self):
        resolution = self.f.resolve()
        self.assertTrue(resolution['complete'])
        c.scorer.account_costs(resolution, self.f.policy, self.f.read)

    def test_L1_unbound_reference_bytes_are_refused_by_the_bound_reader(self):
        """Identity: resolve_and_score_corrected.bound_json, lines 57-60."""
        descriptor = dict(self.f.manifest['reference_items'])
        items = json.loads(self.f.read(self.f.manifest['reference_items']))['items']
        next(i for i in items if i['record_id'] == 'A')['lines'][6][1] = 'line 7 TAMPERED'
        raw = c.scorer.canonical({'items': items})
        with self.assertRaisesRegex(ValueError, 'Bound JSON hash drift'):
            c.scorer.bound_json(descriptor, lambda _d: raw)

    def test_L2_manifest_rebound_but_receipts_stale_is_refused(self):
        """Identity: every dispatch ticket stamps correction_manifest_sha256,
        so a source edit made after the epoch was frozen contradicts the
        receipts already issued (receipt_costs, lines 157-161)."""
        c.reference_item(self.f)['lines'][6][1] = 'line 7 ALTERED'
        c.rebind_manifest_only(self.f)
        with self.assertRaisesRegex(ValueError, 'Physical dispatch correction/freeze identity differs'):
            self.f.resolve()

    def test_L2_partial_restamp_still_caught_by_the_attempt_binding(self):
        """The identity is stamped in four places; forging three is not enough."""
        c.reference_item(self.f)['lines'][6][1] = 'line 7 ALTERED'
        c.rebind_manifest_only(self.f)
        stamps = self.f.stamps()
        for target in self.f.terminal['targets']:
            tickets = {}
            for descriptor in target['dispatch_receipts']:
                ticket = json.loads(self.f.read(descriptor))
                ticket.update(stamps)
                tickets[ticket['ticket_id']] = ticket
                self.f.replace(descriptor, ticket)
            for descriptor in target['attempt_receipts']:
                receipt = json.loads(self.f.read(descriptor))
                receipt['dispatch'] = tickets[receipt['dispatch']['ticket_id']]
                self.f.replace(descriptor, receipt)   # receipt['attempt'] left stale
        with self.assertRaisesRegex(ValueError, 'Physical attempt correction identity differs'):
            self.f.resolve()

    def test_L3_fully_rebound_source_line_change_is_NOT_detected(self):
        """EXPECTED NON-DETECTION, measured, not worked around."""
        c.reference_item(self.f)['lines'][6][1] = 'line 7 ALTERED SOURCE TEXT'
        c.rebind_everything(self.f)
        resolution = self.f.resolve()
        self.assertTrue(resolution['complete'])
        c.scorer.account_costs(resolution, self.f.policy, self.f.read)
        c.scorer.statistics(resolution)
        carried = json.loads(self.f.read(self.f.manifest['reference_items']))
        item = next(i for i in carried['items'] if i['record_id'] == 'A')
        self.assertEqual(item['lines'][6], [7, 'line 7 ALTERED SOURCE TEXT'])

    def test_L3_fully_rebound_gold_line_relabel_is_NOT_detected(self):
        """Worst case of the same gap: moving which line is the flaw.

        The gold label is the ground truth of the localization benchmark. Moved
        from line 2 to line 5 with every hash re-pinned, the pipeline accepts it
        and scores against the new answer key.
        """
        item = c.reference_item(self.f)
        self.assertEqual(item['gold'], [2])
        item['gold'] = [5]
        c.rebind_everything(self.f)
        resolution = self.f.resolve()
        self.assertTrue(resolution['complete'])
        c.scorer.account_costs(resolution, self.f.policy, self.f.read)
        c.scorer.statistics(resolution)
        carried = json.loads(self.f.read(self.f.manifest['reference_items']))
        self.assertEqual(next(i for i in carried['items'] if i['record_id'] == 'A')['gold'], [5])

    def test_scorer_output_records_no_external_source_of_truth_for_lines(self):
        """Why L3 cannot be detected here: the resolved result pins the reference
        file's own hash and nothing else. There is no independent copy of the
        source text for a validator to compare against."""
        resolution = self.f.resolve()
        self.assertEqual(resolution['population'], self.f.population)
        text = c.SCORER_SRC.read_text()
        self.assertNotIn('source_of_truth', text)
        self.assertIn('"lines"' if '"lines"' in text else "item[\"lines\"]", text)


if __name__ == '__main__':
    unittest.main(verbosity=2)
