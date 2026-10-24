# Codex Task-8 handoff summary

Cold audit: **PASS**. All completion gaps and validation gaps are zero. The auditor used no model, Lean, sbatch, or web access and did not mutate any search, verify, program, or provenance artifact; every executable was run from an isolated temporary copy.

## Part 1 — algorithm-test stage 2

Searches: **16/16** (12 `BUG_FOUND`, 4 `BOUND_VIOLATION_FOUND`). Verifications: **16/16** (16 `CONFIRMED`). The two pre-handoff Opus verdicts retain their documented legacy fields; all 14 Codex verdicts have exactly `record_id`, `verdict`, and `notes`.

| Stage | Opus (pre-handoff) | gpt-5.6-sol (pro) | Total |
| --- | --- | --- | --- |
| search | 16 | 0 | 16 |
| verify | 2 | 14 | 16 |

## Part 2 — executable twins

Searches: **604/604**. Required verifications: **351/351**, exactly the `WITNESS_FOUND` set. Verdicts: 348 `CONFIRMED`, 3 `REFUTED_WITNESS_INVALID`.

| Outcome | Count |
| --- | --- |
| WITNESS_FOUND | 351 |
| NO_WITNESS_EXHAUSTIVE | 12 |
| NO_WITNESS_INCONCLUSIVE | 221 |
| CLAIM_NOT_FINITELY_REFUTABLE | 20 |
| Total | 604 |

### Outcome × stratum × search executor

| Search executor | Stratum | WITNESS_FOUND | NO_WITNESS_EXHAUSTIVE | NO_WITNESS_INCONCLUSIVE | CLAIM_NOT_FINITELY_REFUTABLE | Search total | Verified CONFIRMED | Witness invalid | Cannot reproduce |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Fable (pre-handoff) | certified | 7 | 3 | 2 | 4 | 16 | 6 | 1 | 0 |
| gpt-5.6-sol (pro) | certified | 289 | 7 | 193 | 9 | 498 | 287 | 2 | 0 |
| gpt-5.6-sol (pro) | no_lean | 55 | 2 | 26 | 7 | 90 | 55 | 0 | 0 |

### Provenance and executable audit

The frozen Fable baseline contributes 16 searches. The exact remaining 588 searches and all 351 verifications are attributed one-to-one to unique `PUBLISHED` `gpt-5.6-sol` attempt manifests with `reasoning_mode=pro`, and to unique completion-log rows. All new Codex result schemas and canonical paths are exact. Every `test.py` and `verify.py` passed the independent stdlib/exact-arithmetic AST audit and deterministic double execution under distinct hash seeds; each Codex program's JSON stdout exactly equals its durable result. The 16 frozen Fable tests passed the same arithmetic/import and double-execution checks, with their documented human-readable stdout compatibility exception.
