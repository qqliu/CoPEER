# Integrity fixtures and recorded results

This directory supports the paper's six-fixture check of the publication and scoring pipeline. The recorded result is five refusals and one expected non-detection: consistently rebinding changed source text was accepted. The saved stale-receipt fixture was refused earlier than its predicted stage; that deviation is preserved.

## Contents and scope

- `attack_set/`: six original fixture specifications, the complete runner with package-path/output-path adaptations, and a projection of the recorded result.
- `code/`: the bounded production-module and existing-test-fixture dependency closure needed by these six checks. The two frozen scoring designs are distinct historical versions and are included separately.
- `tests_new/`: the complete original development test sources. `run_selected_tests.py` chooses either three existing clean controls or the 21 existing synthetic tests.
- `POSITIVE_CONTROLS.json` and `logs/`: recorded results from the original environment, including 169 existing tests, 22 development tests and eight previously saved Lean-mutant rows. These are historical records, not newly reproduced results in this package.
- `HASHES.json`: projected original historical hash inventory. Its hash values describe original source artifacts, not newly projected file bytes. `TRANSFORMATIONS.json` maps every copied original SHA256 to its public file SHA256. `PUBLIC_MANIFEST.json` is the current package inventory.
- `INTEGRITY_REPLAY_REPORT.md`: the scientific result and scope, projected from the original report.

The original projection was prepared without executing tests. Release integration then ran the four commands below: package hashes verified, all six detection predictions matched, all three clean controls passed, and all 21 selected synthetic tests passed. `REPLAY_VALIDATION.json` records these fresh bounded checks; `outputs/ATTACK_SET_RESULTS.json` contains the fresh six-fixture result. The original saved evidence remains unchanged. The 169-test and 22-test totals above retain their original recorded scope.

## Commands

Use Python 3.9 or later (the recorded run used Python 3.9.21), PyYAML 6 or later, a system `date` command, and SQLite with FTS5 support from Python's sqlite3 module. `requirements.txt` describes the Python dependency; install it in an environment of your choice before running these commands. No model credentials or Lean installation are used by these commands.

From this directory:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -B verify_public_hashes.py
PYTHONDONTWRITEBYTECODE=1 python3 -B attack_set/run_attack_set.py
PYTHONDONTWRITEBYTECODE=1 python3 -B run_selected_tests.py
PYTHONDONTWRITEBYTECODE=1 python3 -B run_selected_tests.py --synthetic-tests
```

The attack command writes `outputs/ATTACK_SET_RESULTS.json`, preserving the saved result under `attack_set/`. Its expected scientific outcomes are detected V1,V2,V4,V5,V6 and not detected V3. All detection predictions match; V2 retains its stage/reason deviation. Exit zero means detection expectations match, not that every attack was refused. Timestamps, durations, output paths, projected-source hashes and traceback locations can differ. No full-output byte equality is expected after projection.

The default selected-test command invokes exactly three original clean controls. `--synthetic-tests` invokes 21 original development tests, including those controls. It does not claim the original 22-test total. The omitted method is `UnauthorizedAxiomGate.test_builder_never_detects_a_dirty_audit_only_byte_identity`, which reads and hashes 468 protected historical input files. Its source and recorded result remain available, but those inputs are intentionally not copied into this bounded package. The full original 169-test suites likewise are documented by their preserved receipts/logs, not offered as complete runnable suite closures here. No replacement fixture or mock is substituted for the omitted test.

## What the result establishes

These checks apply real production functions to small fixture data. They check byte identities, recorded declarations/axiom flags, duplicate identities and cost totals. The accepted source-rebinding case demonstrates that internally consistent metadata cannot establish source correspondence. This is not an independent security audit, a current-corpus end-to-end attack, or a fresh Lean-validation result. The original `held_out` and `as_preregistered` field names are preserved as recorded author assertions; the package does not establish external registration or independent unseen attack authorship.

Personal project paths and account identifiers were removed. Fixed coordination-reviewer tokens were consistently replaced with neutral role labels in production and fixture code; they are not human-review identities. Scientific model attribution (the original preparation used Claude Opus 5), source outcomes and disagreements remain. Production decision predicates, mutations, endpoint definitions and test assertions are unchanged except for these documented path/label/hash adaptations.

## Integration provenance

The first integration attempt exposed a missing runtime dependency. The original `registry.py` was added byte for byte under `code/quality/runtime/`, and the documented bounded checks then passed. `INTEGRATION_TRANSFORMATIONS.json` records its source hash and the assembly changes. Production predicates and test assertions were unchanged. The fresh V2 result retains the documented earlier-stage refusal.
