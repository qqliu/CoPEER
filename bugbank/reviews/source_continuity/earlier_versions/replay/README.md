# Deterministic replay of superseded historical certificates

Claude, 2026-09-21, under Astra TASK-175 and TASK-177. Read-only with respect to the repository evidence and the
manuscript. No model calls. Nothing in `astra/` was written by this work.

## What this is

Twelve records on the `REPLACED_INVALID` roster had their superseded Lean certificate recovered from the frozen
dossier at its **exact recorded historical sha256**, then recompiled. Eleven were the set Astra's repair-pair audit
listed as recovered-but-without-an-authenticated-old-receipt; the twelfth (`mse_605342__ans609345`) is the separate
follow-up recovery Astra found by static inspection, kept in its own group.

Recovery recipe: `Vlean` block index 1 of the dossier `.tex`, minus exactly one wrapper-final newline. For eleven
files that leaves one terminal newline; for `mse_605342__ans609345` the block ends with three newlines and removing
exactly one leaves two, which an `rstrip()`-based extraction destroys. Every recovery is self-validating, because
the result is accepted only when its sha256 equals the historical hash recorded in the packet.

## Results

| | |
|---|---|
| Recovered at exact historical hash | 12 of 12 |
| Replayed PASS under Lean 4.30.0 | 12 |
| Replayed PASS under Lean 4.34.0 | 12 |
| Declarations inspected for transitive axioms | 123 |
| Files using `sorry` or native reduction | 0 |
| Axiom sets observed | none (78), `propext` (42), `propext` + `Quot.sound` (3) |

Three further candidate names (`above`, `records`, `is`) did not resolve. All three are artifacts of the extraction
regex reading the word "theorem" inside comment prose, e.g. "theorem above is not true merely because...". Every
real declaration was inspected.

## What this does and does not establish

It establishes **reproducibility now**: these exact bytes compile today under two pinned toolchains with clean
axioms. It does **not** authenticate that the original historical run occurred. The three strict
historical-receipt pairs in Astra's `repair_pair_audit` remain a separate and stronger provenance category.

It is **not** a count of compiler false positives, and must never be quoted as a frequency. Per Astra's semantic
reads (TASK-178), several of these modules already contain a source-admissible witness alongside an out-of-regime
headline — `mse_2605396__ans2605536` proves an admissible n=6,k=3 witness as well as the n=5,k=2 headline;
`proofwiki_69483` already uses r=s=n=3,j=1; `arxiv_1304.1796v2__source_enriched_codex` already includes the
source-specific p0 family; `reddit_learnmath_t6wb5n` contains an admissible x=3/2 witness. Those are
dossier/selected-object alignment cases. Which part of each record was actually repaired is a per-record semantic
question, settled by reading the selected declaration, the described witness and the source predicate separately —
not by the fact that a file compiles. The roster is replacement-defined and retrospective.

## Method note on the axiom inspection

Each driver is the recovered file's exact bytes as a prefix, followed only by `#print axioms` lines. No original
file was modified, and `prefix_unmodified` is recorded and verified per file. The first parser run was line-based
and silently skipped a wrapped output line covering a main refutation theorem; it was replaced with a DOTALL parse
over the full stdout, which is why `declarations_inspected` is reported per file rather than assumed complete.

## Files

- `MANIFEST.json` — every artifact with sha256 and size, plus the scope and interpretation limits
- `RECOMPILE_RESULTS_{eleven,twelfth}.json` — per-file commands, cwd, seconds, exit codes, before/after source hashes
- `AXIOMS_RESULTS_{eleven,twelfth}.json` — per-declaration transitive axioms, driver hashes, full stdout
- `recovered/` — the twelve recovered certificates at their historical hashes
- `axiom_drivers/` — the inspection drivers (exact prefix + `#print axioms` only)
- `compile_oldcerts.py`, `axioms_oldcerts.py` — the two scripts, as run
