# Historical executable audit and selected algorithm tests

This static supplement extends `studies/executable_checks/`, which already supplies all 604 inputs/search results, all 351 witness-check results and 955 Python programs. It adds the saved historical audit receipt and the positively selected 16-record algorithm test stage. No experiments, program replay, model calls, or new judgments were performed for this supplement.

## Historical 955-program audit

`audit/CODEX_HANDOFF_SUMMARY.md` is the saved cold-audit PASS record: 604 searches, 351 witness checks, 348 confirmed witnesses and three rejected witnesses. It records that every search/checker program passed the exact-arithmetic/import audit and deterministic double execution. `audit/source/audit_task8_codex_handoff.py` is the original documentary auditor; `validate_dynamic_one` uses hash seeds 0 and 1 and compares complete stdout bytes. The 16 pre-handoff searches have a documented human-readable stdout exception while retaining the arithmetic/import and double-execution checks. `audit/existing_955_program_bindings.json` binds the 955 already-distributed program copies to original/distributed hashes.

The original auditor expects the research-tree layout and private execution-provenance files. It is provided for inspection, not as a portable release entry point. The saved summary is an aggregate execution receipt; this supplement does not invent per-execution stdout receipts or claim a new replay. Current publication-byte hashes are recorded separately from original-byte hashes.

## Positively selected algorithm16 stage

`algorithm16/selected_ids.json` freezes the 16 selected records. This supplement includes their two stored selection judgments, exact stage-2 prompt/schema source, all 16 search records, all 16 independent verification records and both Python programs per record. The saved result is 12 BUG_FOUND plus four BOUND_VIOLATION_FOUND, with 16 CONFIRMED verifications. The original programs remain available for inspection; they were not executed for this release.

This positively selected stage is not a recall estimate. The saved overlap analysis records 12 jointly observed records with the twin frame, three confirmed by both workflows and nine confirmed only by this algorithm stage. Four selected algorithm records are outside the twin frame. Unobserved comparisons are not failures. These 16 are separate from the prescribed Lean-repair experiment.

Known source gap: the search protocol refers to `qedbench_certificate_availability_triage/data/records_alg_graph.jsonl`, but that exact original source file is absent from this checkout. Its complete original problem/solution inputs are therefore not recreated here. The stored selected claim/source quote, search report and executable source are retained. This supplement closes the saved-result and historical-audit-receipt gap, not the missing full original-input archive.

Operational machine paths are normalized. Provider sessions, event streams, credentials, reviewer identity fields and private human responses are excluded. Bibliographic source content is preserved. MANIFEST.json records each copied/projected source and both hashes.
