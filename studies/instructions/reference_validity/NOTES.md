# Section 4 fixes: stratified Table 1 and tool-use sensitivity

Offline recomputation from the frozen September grades and accepted-attempt usage receipts. No model, API or Slurm
call. Paired percentile bootstrap, 20000 resamples, seed 20260917, the same index draw as the paper. Every input is
sha256-pinned in `MANIFEST.json`. Each `.tex` file is a bare `tabular` in the style of `generated/witness_primary_table.tex`
(booktabs, `\shortstack` intervals) and can be `\input` directly; captions are the author's, except the tool-use
definition sentence supplied in `toolfree_sensitivity_caption.tex`.

## stratified_primary_table.tex (with stratified_grades_table.tex and stratified_primary.json)

**What it shows.** Table 1 (catches search/review, paired catch difference in pp with CI, output-token ratio with CI,
full-token ratio with CI) recomputed for all three models on nested reference-audit tiers: all 100; the 71 whose
reference joins an audited ledger record by exact witness; the 43 retained with the witness kept as written; the 42
supported by the automated source audit; the 22 whose whole frozen proof matches the source (the paper's existing
sensitivity set); the 15 with exact source text; and, separately, the 13 whose reference the audit invalidated
(10 excluded as wrong, blocker `SEMANTIC_EXCLUDED`, plus 3 retained only with a replaced witness) and the 15 the audit
left unresolved (`SEMANTIC_UNRESOLVED`). The companion grades table gives, per tier, model and arm, the counts of
CAUGHT_MATCHING / CAUGHT_DIFFERENT / FALSE_CATCH / MISSED. The all-100 block reproduces `witness_primary_table.tex` and
the 22 block reproduces `reference_sensitivity_table.tex` byte for byte (`reproduced_*.tex` are the exact renderings;
the script exits 2 if they differ). The output-ratio finding is stable across tiers: Sol 0.67-0.76, Gemini 0.66-0.88
(1.12 on the 13 invalidated), Opus 0.69-0.82, with catch differences whose intervals include zero everywhere except
Opus on the 43 (+9.3 [+0.0, +20.9]) and the three models on the 15 exact-source references (+6.7 [+0.0, +20.0], one task).
On the 13 invalidated references the grader still awarded CAUGHT_MATCHING in 60 of 78 model-arm cells (Sol 22, Gemini 19,
Opus 19 of 26 each), so the model grader inherits the reference-fidelity gap rather than exposing it.

**What it does not show.** The tiers are selected subsets defined by an automated audit and a text-binding rule; none
is a random sample, none is new human approval, and the 29 never-audited references are simply unknown (they are the
100 minus the 71, not a "good" or "bad" tier). Kept-as-written (43) is release status, not source fidelity; only the 42
and its sub-tiers carry a source-consistency check. The grades are the frozen model-grader grades, unchanged. Intervals
on tiers of 13-22 tasks are wide and pointwise; the full-token column stays uninformative (see below) at every tier.

**Caveat to print beside it.** *All tiers are post hoc, non-random subsets selected by an automated audit; the grades are
the unchanged September model-grader grades, and a CAUGHT_MATCHING grade on an invalidated reference records agreement
with a reference the audit rejected, not a correct catch.*

## toolfree_sensitivity_table.tex (with toolfree_sensitivity_caption.tex and toolfree_sensitivity.json)

**What it shows.** For each model, the number of cells whose accepted attempt executed tools in the search (S) and review
(R) arms, then the output, full-token and input-only ratios with CIs on all 100 tasks and on the tool-free task subset.
Tool use is defined exactly as in the prior flawhunt scripts (`noexec.py`): a cell used tools iff its usage record has
`extra_exec_count > 0`, i.e. at least one shell command or tool execution beyond the single print-only read of the input
file; a task is tool-free iff both of its cells have `extra_exec_count = 0`. Sol: 1 S cell and 3 R cells on 4 tasks;
tool-free n=96, output 0.676 [0.604, 0.761], full 0.977 [0.971, 0.983], input-only 0.996 [0.995, 0.997]. Gemini: 2 S
cells and 5 R cells on 6 tasks; tool-free n=94, output 0.843 [0.774, 0.916], full 0.955 [0.937, 0.976], input-only
0.998 [0.997, 0.999]. The published Gemini full-token ratio 0.650 comes from those 6 tasks (one of them,
`arxiv_1904.10482v2`, ran 24 extra executions in the review arm). On tool-free cells input is the same in both arms by
construction, so the full-token ratio there is just a diluted output ratio and carries no separate information.

**What it does not show.** `extra_exec_count` is a harness count; it does not say whether the executed command was
mathematical tool use, and it is not recorded at all for the archived Opus run (`n/r`), so no tool-free row exists for
Opus. The subset is defined by an outcome of the run, so its ratios are conditional descriptive statistics, not a
pre-registered contrast. Tool use is dropped by task, not by cell, to preserve the pairing. Full tokens count accepted
solver attempts only (no grader, no rejected attempts) and Opus counts are provisional per-line sums.

**Caveat to print beside it.** *The tool-free subset is selected post hoc by an unenforced prompt prohibition observed in
the run logs; input tokens are near-identical across arms on those cells, so the full-token ratio there restates the
output ratio and should not be read as an independent cost result.*

## Files

- `common.py` shared read-only loaders (token conventions and tool-use definition documented in its docstring)
- `stratified_primary.py` -> `stratified_primary_table.tex`, `stratified_grades_table.tex`, `stratified_primary.json`,
  `reproduced_witness_primary_table.tex`, `reproduced_reference_sensitivity_table.tex`
- `toolfree_sensitivity.py` -> `toolfree_sensitivity_table.tex`, `toolfree_sensitivity_caption.tex`, `toolfree_sensitivity.json`
- `build_manifest.py` -> `MANIFEST.json` (sha256 of every input and output, seed, resamples, commands)
