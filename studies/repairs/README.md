# Specified repairs

This release supports the paper's repair-study outcome and resource tables: 16 source-derived tasks, conditions A and B, and the reported Opus 5.5, Sonnet 5, and GPT-OSS 120B solvers. Condition A supplies source context, definitions, the located defect, a repair template, and proof obligations. Condition B additionally supplies the checked counterexample. The study allows three attempts per task and condition.

Run the complete offline aggregate and file-integrity replay from the repository root:

```sh
python3 -B studies/repairs/replay.py
```

This requires only Python 3.8 or later and makes no model calls. It verifies the saved grades and proof hashes, first-attempt PASS/FAIL/Absent counts, runtime-compliant counts, success within three attempts, and first-attempt token totals including cache components and incomplete-usage flags.

- `results.json` contains 288 selected cells and the expected per-attempt summaries. Original checker verdicts and verdicts after the private-helper audit are separate fields.
- `cells/` contains anonymized run summaries, available submissions and prompts, grades, and the five relevant helper-audit receipts. The 246 saved Lean submissions are byte-for-byte identical to those graded. A missing submission is represented by its saved cell record, rather than an empty proof file.
- `tokens.json` contains all 96 selected first attempts. Native usage is complete for 91; five retain observed partial counts. Their condition totals are lower bounds. Full tokens include ordinary input, cache creation, cache reads, and output as separately reported; GPT-OSS prompt tokens already include its entire input.
- `packets/` supplies the task, source passage, definitions, counterexample, and repair specification for every task. Counterexamples and checker references were withheld from condition A where required by the experimental design.
- `harness/`, `evaluator_records/`, and `evaluator_records_v2/` supply validator code, fixed grammars, hidden checker inputs, and Lean environment pins. The saved grades use v2 for E05/E11, v3 for E10, and v1 otherwise. The v3 wrapper imports the byte-identical original `validate.py`; modifications to exported support code are limited to paths and anonymized commentary.
- `checker_reference/audit_private_axioms_roster.py` preserves the audit algorithm for inspection. Here `private` is Lean's declaration visibility modifier. This file documents the original full-roster audit driver; the selected saved audit receipts are the evidence used by the offline replay.
- `provenance/` provides native numeric usage receipts, per-request usage rows, a selected/predecessor recovery ledger, and support-version bindings for the 20 grades using the older helper. Original hashes and historical grade stamps are preserved.
- `MANIFEST.json` binds every exported file by SHA-256 and records original hashes where a file was transformed.

For optional fresh Lean checking, install Lean 4.30.0, Mathlib at the revision in `harness/lean_env/lake-manifest.json`, and Linux `bubblewrap`; build Mathlib dependencies in a separate project and set `COPEER_LEAN_PROJECT` to its absolute path. From this directory, run `bash evaluator_records/check_record.sh E01 cells/<cell_id>/SUBMISSION.lean` for a v1 task, `bash evaluator_records_v2/check_record_v2.sh E05 ...` for E05/E11, or `bash harness/validate_v3_lambda/check_record_v3.sh E10 ...` for E10. These commands produce new grades; the offline replay above checks the released results without regenerating them. Fresh Lean checking was not rerun during release assembly.

The release is an explicit selection of the reported study, including all three attempts. Pilots, rehearsal cells, unreported additional solvers, raw provider streams, authentication configuration, workstation identifiers, and internal coordination files are outside this export. The recovery ledger retains the selected and predecessor records with their original statuses and evidence hashes; token totals count only the selected first attempt, as in the paper.
