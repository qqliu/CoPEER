#!/usr/bin/env python3
"""Apply the six held-out attack fixtures to the REAL pipeline functions.

Read-only with respect to every frozen input: each attack builds its own
throwaway fixture (a temporary directory for the publish path, an in-memory
file map for the scorer path) and calls the actual production function. Nothing
outside integrity/ is written.

For each variant it records: detected yes/no, the responsible stage as
function + file:line taken from the real traceback, the reason string, and
whether the detection is an identity (hash/byte equality) check or a semantic
one. No Lean, no model call, no network.

    DISABLE_AUTOUPDATER=1 PYTHONDONTWRITEBYTECODE=1 python3 -B run_attack_set.py
"""
import hashlib
import json
import re
import subprocess
import sys
import time
import traceback
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / 'tests_new'))
import integrity_replay_common as c   # noqa: E402  (also verifies the frozen hashes)

PIPELINE_SOURCES = {str(c.PUBLISH_SRC), str(c.SCORER_SRC), str(c.BUILDER_SRC)}
FIXTURES = {
    'V1': 'V1_wrong_selected_declaration.json',
    'V2': 'V2_stale_receipt.json',
    'V3': 'V3_changed_source_context.json',
    'V4': 'V4_unauthorized_axiom.json',
    'V5': 'V5_duplicate_record.json',
    'V6': 'V6_corrupted_aggregate.json',
}


def utc_now():
    return subprocess.run(['date', '-u', '+%Y-%m-%dT%H:%M:%SZ'],
                          capture_output=True, text=True, check=True).stdout.strip()


def sha256_bytes(raw):
    return hashlib.sha256(raw).hexdigest()


def scrub(text):
    """Temporary-directory names differ per run; keep the ledger comparable."""
    return re.sub(r'/tmp/tmp[0-9A-Za-z_]+', '<TMPDIR>', text) if isinstance(text, str) else text


def responsible_stage(exc):
    """Deepest traceback frame inside a pipeline source, skipping the need() helper."""
    frames = [f for f in traceback.extract_tb(exc.__traceback__) if f.filename in PIPELINE_SOURCES]
    frames = [f for f in frames if f.name != 'need'] or frames
    if not frames:
        return None
    frame = frames[-1]
    return {'function': frame.name,
            'location': str(Path(frame.filename).relative_to(c.REPO)) + ':' + str(frame.lineno),
            'statement': frame.line}


class PublishCase(unittest.TestCase):
    """Only used to borrow the existing publisher fixture's bound setUp."""
    setUp = c.tcr.VersionedPublisherTests.setUp
    build = c.tcr.VersionedPublisherTests.build
    bind_fixture_ledger = c.tcr.VersionedPublisherTests.bind_fixture_ledger

    def runTest(self):
        pass


def publish_case():
    case = PublishCase()
    case.setUp()
    return case


# --------------------------------------------------------------------------- #
# the six attacks
# --------------------------------------------------------------------------- #
def attack_V1():
    case = publish_case()
    other = b'-- A DIFFERENT SYNTHETIC LEAN SOURCE, NOT THE SHIPPED CERTIFICATE\n'
    case.new[0]['build_record']['source_sha256'] = c.publish.sha(other)
    case.bind_fixture_ledger()
    return case.build


def attack_V2():
    case = publish_case()
    card = case.root / 'entries/algebra/kept.md'
    card.write_bytes(card.read_bytes() + b'\nA synthetic later edit of the current card.\n')
    return case.build


def attack_V3():
    fixture = c.Fixture()
    item = c.reference_item(fixture, 'A')
    gold, distractor = item['gold'][0], 7
    lines = {label: index for index, (label, _text) in enumerate(item['lines'])}
    i, j = lines[gold], lines[distractor]
    item['lines'][i][1], item['lines'][j][1] = item['lines'][j][1], item['lines'][i][1]
    c.rebind_everything(fixture)

    def run():
        resolution = fixture.resolve()
        c.scorer.account_costs(resolution, fixture.policy, fixture.read)
        c.scorer.statistics(resolution)
        carried = json.loads(fixture.read(fixture.manifest['reference_items']))
        accepted = next(x for x in carried['items'] if x['record_id'] == 'A')
        return {'complete': resolution['complete'],
                'accepted_gold_label': accepted['gold'],
                'accepted_text_under_gold': dict((l, t) for l, t in accepted['lines'])[accepted['gold'][0]]}
    return run


def attack_V4():
    case = publish_case()
    spec = json.loads((HERE / FIXTURES['V4']).read_bytes())
    case.new[0]['build_record']['selected_theorems'][0]['audit']['disallowed_axioms'] = \
        spec['mutation']['new_value']
    case.bind_fixture_ledger()
    return case.build


def attack_V5():
    case = publish_case()
    case.new[1]['record_id'] = 'kept'
    prior = c.read_prior_ledger(case)
    return lambda: c.publish.validate_ledger(prior, case.new, None)


def attack_V6():
    fixture = c.Fixture()
    resolution = fixture.resolve()
    key = sorted(fixture.policy['subject']['configurations'])[0]
    descriptor = fixture.policy['subject']['configurations'][key]['historical_cost_report']
    report = json.loads(fixture.read(descriptor))
    report['components']['charged_tokens'] += 1
    fixture.replace(descriptor, report)
    return lambda: c.scorer.account_costs(resolution, fixture.policy, fixture.read)


ATTACKS = {'V1': attack_V1, 'V2': attack_V2, 'V3': attack_V3,
           'V4': attack_V4, 'V5': attack_V5, 'V6': attack_V6}


def main():
    c.assert_frozen_inputs_unchanged()
    started = utc_now()
    rows = []
    for attack_id, filename in FIXTURES.items():
        fixture_path = HERE / filename
        spec = json.loads(fixture_path.read_bytes())
        expected = spec['expected']
        begin = time.time()
        row = {'attack_id': attack_id, 'variant': spec['variant'], 'held_out': spec['held_out'],
               'fixture': filename, 'fixture_sha256': sha256_bytes(fixture_path.read_bytes()),
               'target': spec['target'], 'expected_detected': expected['detected'],
               'expected_detection_class': expected['detection_class']}
        try:
            run = ATTACKS[attack_id]()
        except Exception as exc:                                  # setup must never fail silently
            row.update(status='SETUP_ERROR', detected=None,
                       reason=scrub(type(exc).__name__ + ': ' + str(exc)),
                       stage=responsible_stage(exc), match=False)
            row['seconds'] = round(time.time() - begin, 3)
            rows.append(row)
            continue
        try:
            accepted = run()
            row.update(detected=False, reason=None, stage=None, detection_class='none',
                       accepted_outcome=accepted if isinstance(accepted, dict) else 'staged')
        except Exception as exc:
            row.update(detected=True, reason=scrub(type(exc).__name__ + ': ' + str(exc)),
                       stage=responsible_stage(exc),
                       detection_class=expected['detection_class'] if expected['detected'] else 'unexpected')
        # Detection and stage are scored separately, so that a refusal arriving
        # from an EARLIER gate than predicted is recorded as a deviation instead
        # of being hidden by relaxing the pre-registered expectation.
        row['detection_match'] = (row['detected'] == expected['detected'])
        row['reason_match'] = (True if not expected['detected']
                               else bool(row['detected']) and expected['reason_contains'] in row['reason'])
        row['match'] = row['detection_match'] and row['reason_match']
        if row['match']:
            row['status'] = 'AS_PREREGISTERED'
        elif row['detection_match']:
            row['status'] = 'DETECTED_AT_A_DIFFERENT_STAGE_THAN_PREREGISTERED'
            row['deviation'] = ('pre-registered reason ' + repr(expected['reason_contains']) +
                                ' was not the one reached; an earlier gate refused first, so the '
                                'pre-registered gate stays unreached and untested by this fixture')
        else:
            row['status'] = 'DEVIATION'
        if not expected['detected']:
            row['expected_non_detection_note'] = expected['note']
        row['seconds'] = round(time.time() - begin, 3)
        rows.append(row)

    result = {'schema': 'integrity-replay-attack-set-results/v1',
              'started_utc': started, 'finished_utc': utc_now(),
              'python': sys.version.split()[0],
              'frozen_inputs_sha256': {str(p.relative_to(c.REPO)): c.sha256_file(p) for p in c.PINNED},
              'lean_executed': False, 'model_calls_performed': 0, 'network_used': False,
              'all_detections_as_preregistered': all(r.get('detection_match') for r in rows),
              'all_reasons_as_preregistered': all(r.get('reason_match') for r in rows),
              'all_as_preregistered': all(r['match'] for r in rows),
              'deviations': [{'attack_id': r['attack_id'], 'status': r['status'],
                              'observed_reason': r.get('reason'), 'stage': r.get('stage')}
                             for r in rows if not r['match']],
              'detected': sorted(r['attack_id'] for r in rows if r['detected']),
              'not_detected': sorted(r['attack_id'] for r in rows if r['detected'] is False),
              'rows': rows}
    out = HERE.parent / 'outputs' / 'ATTACK_SET_RESULTS.json'
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes((json.dumps(result, ensure_ascii=False, indent=2, sort_keys=False) + '\n').encode())
    print(json.dumps({'output': str(out), 'sha256': sha256_bytes(out.read_bytes()),
                      'all_detections_as_preregistered': result['all_detections_as_preregistered'],
                      'all_reasons_as_preregistered': result['all_reasons_as_preregistered'],
                      'detected': result['detected'], 'not_detected': result['not_detected'],
                      'deviations': result['deviations']}, indent=2))
    # Exit status tracks the primary endpoint (detected / not detected as
    # pre-registered). A stage deviation is reported, never silently accepted.
    return 0 if result['all_detections_as_preregistered'] else 1


if __name__ == '__main__':
    sys.exit(main())
