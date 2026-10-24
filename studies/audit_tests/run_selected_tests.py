#!/usr/bin/env python3
"""Select existing synthetic tests without rerunning protected historical inputs.

This file only supplies test selection and package-relative import paths.
The original development-test files are shipped in full.
"""
import argparse
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / 'tests_new'))
EXCLUDED = ('test_variant4_unauthorized_axiom.UnauthorizedAxiomGate.'
            'test_builder_never_detects_a_dirty_audit_only_byte_identity')
CLEAN_CONTROLS = [
    'test_variant3_source_context.PublishSideSourceContext.test_positive_control_untouched_source_context_is_accepted',
    'test_variant3_source_context.ScorerSideReferenceLines.test_positive_control_untouched_reference_resolves_and_accounts',
    'test_variant4_unauthorized_axiom.UnauthorizedAxiomGate.test_positive_control_clean_audit_is_accepted',
]

def flatten(suite):
    for item in suite:
        if isinstance(item, unittest.TestSuite):
            yield from flatten(item)
        else:
            yield item

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--synthetic-tests', action='store_true',
                        help='Run the 21 original tests that do not need the protected historical ledger.')
    args = parser.parse_args()
    loader = unittest.TestLoader()
    if args.synthetic_tests:
        original = loader.loadTestsFromNames([
            'test_variant3_source_context', 'test_variant4_unauthorized_axiom'])
        tests = [test for test in flatten(original) if test.id() != EXCLUDED]
        if len(tests) != 21:
            raise RuntimeError('Expected exactly 21 original synthetic tests; selection drifted.')
    else:
        tests = list(flatten(loader.loadTestsFromNames(CLEAN_CONTROLS)))
        if len(tests) != 3:
            raise RuntimeError('Expected exactly three named clean controls.')
    result = unittest.TextTestRunner(verbosity=2).run(unittest.TestSuite(tests))
    return 0 if result.wasSuccessful() else 1

if __name__ == '__main__':
    sys.exit(main())
