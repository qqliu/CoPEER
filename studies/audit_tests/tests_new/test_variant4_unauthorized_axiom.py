"""Variant (4), unauthorized axiom dependency, through the real Python gate.

Before this file the only coverage of variant (4) was the Lean mutant sweep
(m4_sorry, m7_native_decide in astra/repair_track_20260922/harness/mutants):
the Python publish gate at publish_corrected_review.validate_ledger had NO test
with audit['disallowed_axioms'] non-empty or audit['unsafe'] true.

The gate under test (publish_corrected_review.py lines 243-246):

    need(br.get('selected_theorems') and all(
            x['name'] == x['audit']['name'] and x['audit'].get('type') and
            not x['audit'].get('unsafe') and not x['audit'].get('disallowed_axioms') and
            not x['audit'].get('uses_native_reduction')
            for x in br['selected_theorems']),
         'Selected declaration evidence incomplete')

All fixtures are synthetic; no Lean is run and no approval is created.
"""
import unittest

import integrity_replay_common as c


class UnauthorizedAxiomGate(unittest.TestCase):
    """Borrows the existing publisher fixture without modifying it."""

    setUp = c.tcr.VersionedPublisherTests.setUp
    build = c.tcr.VersionedPublisherTests.build
    bind_fixture_ledger = c.tcr.VersionedPublisherTests.bind_fixture_ledger

    # -- positive control ---------------------------------------------------- #
    def test_positive_control_clean_audit_is_accepted(self):
        """Both flags clean: the same gate accepts and the release is staged."""
        audit = c.selected_audit(self)
        self.assertEqual(audit['disallowed_axioms'], [])
        self.assertFalse(audit['unsafe'])
        self.assertFalse(audit['uses_native_reduction'])
        _outputs, _authority, receipt = self.build()
        self.assertEqual(receipt['counts'],
                         {'reviewed': 2, 'retained': 1, 'withdrawn': 1, 'outside': 1, 'active': 2})

    # -- rejections ---------------------------------------------------------- #
    def test_disallowed_axiom_sorryAx_is_refused(self):
        c.selected_audit(self)['disallowed_axioms'] = ['sorryAx']
        self.bind_fixture_ledger()
        with self.assertRaisesRegex(ValueError, 'Selected declaration evidence incomplete'):
            self.build()

    def test_disallowed_axiom_list_with_several_names_is_refused(self):
        c.selected_audit(self)['disallowed_axioms'] = ['sorryAx', 'Classical.choice_unchecked']
        self.bind_fixture_ledger()
        with self.assertRaisesRegex(ValueError, 'Selected declaration evidence incomplete'):
            self.build()

    def test_unsafe_declaration_is_refused(self):
        c.selected_audit(self)['unsafe'] = True
        self.bind_fixture_ledger()
        with self.assertRaisesRegex(ValueError, 'Selected declaration evidence incomplete'):
            self.build()

    def test_native_reduction_is_refused(self):
        """Same clause; the Lean counterpart is mutant m7_native_decide."""
        c.selected_audit(self)['uses_native_reduction'] = True
        self.bind_fixture_ledger()
        with self.assertRaisesRegex(ValueError, 'Selected declaration evidence incomplete'):
            self.build()

    def test_missing_audit_type_is_refused(self):
        c.selected_audit(self)['type'] = ''
        self.bind_fixture_ledger()
        with self.assertRaisesRegex(ValueError, 'Selected declaration evidence incomplete'):
            self.build()

    def test_gate_is_reached_through_validate_ledger_not_only_build(self):
        """Pin the responsible stage: the refusal comes from validate_ledger."""
        c.selected_audit(self)['disallowed_axioms'] = ['sorryAx']
        self.bind_fixture_ledger()
        prior = c.read_prior_ledger(self)
        with self.assertRaisesRegex(ValueError, 'Selected declaration evidence incomplete'):
            c.publish.validate_ledger(prior, self.new, self.expected)

    # -- documented non-coverage -------------------------------------------- #
    def test_extension_builder_and_scorer_have_no_axiom_gate(self):
        """EXPECTED NON-DETECTION, recorded rather than worked around.

        build_extension_release.py and resolve_and_score_corrected.py contain no
        axiom/unsafe predicate at all, so an unauthorized-axiom record is invisible
        to them; variant (4) is gated only by the publish step (plus the Lean
        validator sweep). If a future edit adds such a gate this test fails and
        the report's coverage table must be updated.
        """
        for source in (c.BUILDER_SRC, c.SCORER_SRC):
            text = source.read_text()
            for token in ('disallowed_axioms', 'sorryAx', 'uses_native_reduction'):
                self.assertNotIn(token, text, str(source) + ' now mentions ' + token)

    def test_builder_never_detects_a_dirty_audit_only_byte_identity(self):
        """EXPECTED NON-DETECTION at the builder, recorded as measured.

        Part 1: planting disallowed_axioms=['sorryAx'] on a NON-selected30 record
        passes build_extension_release.alignment with no error at all.
        Part 2: planting it on a selected30 record is refused, but for a
        byte-identity reason ('Selected30 ledger record altered'), never because
        an axiom was noticed. The builder has no axiom semantics.
        """
        import copy
        ledger, manifest, allowed, _pins = c.builder.read_inputs()
        selected = {r['record_id'] for r in manifest['rows']}

        def dirty(revised, record_id):
            record = next(r for r in revised if r['record_id'] == record_id)
            theorems = (record.get('build_record') or {}).get('selected_theorems')
            if not theorems:
                record.setdefault('build_record', {})['selected_theorems'] = [
                    {'name': 'X', 'audit': {'name': 'X', 'type': 'True', 'disallowed_axioms': ['sorryAx']}}]
            else:
                theorems[0].setdefault('audit', {})['disallowed_axioms'] = ['sorryAx']

        outside_id = next(r['record_id'] for r in ledger if r['record_id'] not in selected)
        revised = copy.deepcopy(ledger)
        dirty(revised, outside_id)
        report = c.builder.alignment(ledger, revised, manifest)   # accepted, no exception
        self.assertEqual(report['selected30_record_count'], 30)

        revised = copy.deepcopy(ledger)
        dirty(revised, sorted(selected)[0])
        with self.assertRaisesRegex(ValueError, 'Selected30 ledger record altered') as caught:
            c.builder.alignment(ledger, revised, manifest)
        self.assertNotIn('axiom', str(caught.exception).lower())


if __name__ == '__main__':
    unittest.main(verbosity=2)
