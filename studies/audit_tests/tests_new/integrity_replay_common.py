"""Shared loading and rebinding helpers for the parallel integrity replay.

NEW file. Reads the frozen pipeline read-only; modifies nothing outside
integrity/. No Lean, no model call,
no network. Every fixture below is synthetic and is never review evidence.

Two real pipeline entry points are exercised:

  PUBLISH  quality/bank_refresh/
           isolated_COMBINED109_V4_final/scripts/publish_corrected_review.py
           (sha256 e4845e45871c644f08c33898f4a1a53d62c2a343dc99468e46c48f4fb8f8ad08)
           whose validate_ledger() holds the only Python-side selected-declaration
           audit gate (disallowed_axioms / unsafe / uses_native_reduction).

  SCORER   quality/runtime/
           resolve_and_score_corrected.py
           (sha256 034c4666b39fd701f5919badf79c5153cd3d6bff4857ff6336b1603e52b36b1b)

Fixtures are reused from the existing suites by import only (the codebase's own
idiom of borrowing a bound setUp, as tests/test_corrected_review.py does with
test_active_release.ActiveReviewTests.setUp). Nothing in those files is edited.
"""
import hashlib
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1] / 'code'
QC = REPO / 'quality'
BANK = QC / 'bank'
RUNTIME = QC / 'runtime'
PUBLISH_SRC = BANK / 'scripts/publish_corrected_review.py'
SCORER_SRC = RUNTIME / 'resolve_and_score_corrected.py'
BUILDER_SRC = QC / 'build_extension_release.py'

PINNED = {
    PUBLISH_SRC: 'e4845e45871c644f08c33898f4a1a53d62c2a343dc99468e46c48f4fb8f8ad08',
    SCORER_SRC: '034c4666b39fd701f5919badf79c5153cd3d6bff4857ff6336b1603e52b36b1b',
    # 989b74cb… is the builder actually pinned by the staged release
    # (releases/corrected_resource_20260923_v4/CONSENSUS.json builder_sha256 and
    # EXTENSION_SELECTED30_FOLLOWON_TEST_RECEIPT_v1.json). The earlier
    # EXTENSION_BUILDER_RECEIPT.json pin b3374fc0… is superseded.
    BUILDER_SRC: 'ca90e89449963fa21b37952ad413cbd11be9fdbe7064301ce55ffd4bfee62260',
}


def sha256_file(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def assert_frozen_inputs_unchanged():
    """Refuse to interpret any result if a frozen input drifted under us."""
    drift = {str(p): (want, sha256_file(p)) for p, want in PINNED.items() if sha256_file(p) != want}
    if drift:
        raise AssertionError('frozen pipeline input drift: ' + json.dumps(drift, indent=2))


for _p in (str(QC), str(RUNTIME), str(BANK / 'tests'), str(BANK)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

assert_frozen_inputs_unchanged()

import test_corrected_review as tcr                    # noqa: E402  bank suite (read-only import)
import test_resolve_and_score_corrected as trs         # noqa: E402  scorer suite (read-only import)
import build_extension_release as builder              # noqa: E402  extension release builder

publish = tcr.publish       # the real publish_corrected_review module
scorer = trs.s              # the real frozen resolve_and_score_corrected module
Fixture = trs.Fixture       # the scorer suite's synthetic fixture builder


# --------------------------------------------------------------------------- #
# PUBLISH-side helpers (operate only on the suite's own temporary bank)
# --------------------------------------------------------------------------- #
OLD_LEDGER_REL = 'releases/human_review_20260917/ledger.json'


def rebind_bank_authority(case):
    """Re-pin active_review.json and the isolation marker to the bytes on disk.

    This is the 'consistently rebound manifest' capability an attacker with write
    access to the staging checkout would have.
    """
    root = case.root
    authority = json.loads((root / 'active_review.json').read_bytes())
    authority['source_ledger_sha256'] = publish.digest(root / OLD_LEDGER_REL)
    (root / 'active_review.json').write_bytes(publish.jb(authority))
    marker = json.loads((root / publish.MARKER).read_bytes())
    marker['source_authority_sha256'] = publish.digest(root / 'active_review.json')
    (root / publish.MARKER).write_bytes(publish.jb(marker))
    case.authority = authority


def write_prior_ledger(case, ledger):
    (case.root / OLD_LEDGER_REL).write_bytes(publish.jb(ledger))


def read_prior_ledger(case):
    return json.loads((case.root / OLD_LEDGER_REL).read_bytes())


def selected_audit(case):
    """The audit block of the retained record's selected declaration."""
    return case.new[0]['build_record']['selected_theorems'][0]['audit']


# --------------------------------------------------------------------------- #
# SCORER-side helpers
# --------------------------------------------------------------------------- #
def reference_item(fixture, record_id='A'):
    return next(i for i in fixture.items if i['record_id'] == record_id)


def rebind_manifest_only(fixture):
    """Re-pin reference.json, the population hashes, the manifest and the registry.

    This is what a tamper AFTER the epoch was frozen can reach: the receipts
    already issued still carry the previous manifest/registry stamps.
    """
    fixture.update_masks()
    fixture.registry['manifest'] = fixture.put('synthetic/manifest.json', fixture.manifest)
    fixture.rd = fixture.put('synthetic/fresh/RUN_REGISTRY.json', fixture.registry)
    fixture.terminal['registry'] = fixture.rd
    fixture.terminal['manifest'] = fixture.registry['manifest']
    return fixture


def rebind_everything(fixture):
    """Also re-stamp every receipt, so no stamp contradicts the new manifest.

    Four places carry the manifest/registry identity and all four must be
    forged: the dispatch ticket, the attempt receipt's embedded dispatch, the
    attempt object inside the receipt, and the run record (plus its attempts).
    """
    rebind_manifest_only(fixture)
    stamps = fixture.stamps()
    for target in fixture.terminal['targets']:
        record = json.loads(fixture.read(target['record']))
        record.update(stamps)
        for attempt in record['attempts']:
            attempt.update(stamps)
        fixture.replace(target['record'], record)
        tickets = {}
        for descriptor in target['dispatch_receipts']:
            ticket = json.loads(fixture.read(descriptor))
            ticket.update(stamps)
            tickets[ticket['ticket_id']] = ticket
            fixture.replace(descriptor, ticket)
        for descriptor in target['attempt_receipts']:
            receipt = json.loads(fixture.read(descriptor))
            receipt['dispatch'] = tickets[receipt['dispatch']['ticket_id']]
            receipt['attempt'].update(stamps)
            fixture.replace(descriptor, receipt)
    return fixture
