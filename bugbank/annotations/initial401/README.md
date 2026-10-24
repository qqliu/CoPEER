# Complete counterexample census and structural analysis

This analysis reads **all 401 released counterexample records**, retains
evidence-backed qualitative annotations, joins the historical audit stages,
and develops two later deposited constructions into analytic propositions.
It accompanies the focused ICLR 2027 manuscript in `paper_v2/`.

## Findings and their scope

| Documented property | Final records | Fraction of 401 |
| --- | ---: | ---: |
| Infinite counterexample family with a general argument | 56 | 14.0% |
| Justified nearby corrected claim or sufficient hypothesis | 117 | 29.2% |
| Alternative surviving an explicitly named boundary restriction | 71 | 17.7% |
| Reported bounded exhaustive domain | 133 | 33.2% |

The properties overlap: 30 records document both a family and a repair,
and 143 document at least one. There are 245 explicit intermediate-step
refutations, 55 explicit target-statement refutations, and 101 whose role
cannot be established from the packet. Only three packets supply an
argument excluding all smaller admissible instances under a stated size
measure; 89 report bounded/search-order minimality.

These are **documentation counts in a selected release**, not independent
mathematical certifications or estimates over mathematical errors generally.
Unflagged content may be absent, insufficiently argued, or missed by coding.
Different packet lengths and construction histories affect these frequencies.
Assistant review is not human signoff or independence across model families.

The separate 449-record replication analysis finds that 47 of its 48
held-out records still have a confirmed witness. Later holdout occurs in
42/136 reference-adjudicated records and 6/280 reference-corroborated
records, a descriptive rate ratio of 14.41. The direction is the same within
all five broad source families and nine of eleven original strata. Common
original-corpus weighting gives 14.52. Neither ratio estimates a causal
effect of adjudication or the probability that a theorem is false.

The 401 records represent 374 source units, 397 whitespace-normalized claim
texts, 401 witness texts, and 393 stored certificate hashes. These identity
checks do not identify mathematically equivalent constructions. All 27 extra
records beyond the source-unit count arise from multiple QEDBench solutions
to the same problem.

Two **later deposits, separate from the census**, yield:

- A unique optimum of `9/22` at thresholds `(4/11, 10/11)` in the specified
  two-threshold parity construction for rainbow Schur triples, including
  an exact quadratic loss formula. This is not an optimum over all colorings.
- Exactly `90 * 2**n` frozen labeled six-colorings of `C_n[K_2]` for odd
  `n >= 5` divisible by three, and at least one further recoloring component.
  This is a lower bound on components, not their exact total.

Complete analytic proofs are in the paper appendix. Their finite executable
checks supplement the proofs; these new propositions have no Lean
formalization, external priority claim, or causal attribution to retrieval.

## Data and review trail

- `inputs/population.json` pins the exact release membership, original input
  paths, and SHA-256 hashes. The eight input shards contain full packets.
  Its description mentions the four later deposits present at census freeze;
  subsequent discovery additions also remain outside the pinned 401 records.
- `CODEBOOK.md` is the frozen operational codebook, fixed before primary coding.
- `annotations/shard_*.json` are the eight immutable primary coding ledgers.
  Every positive flag has an exact source excerpt. Object and mechanism labels
  are descriptive indexing categories, not discovered natural classes.
- `review/independent_sample.json` is a blind recoding of 24 complete packets,
  selected as the three lowest hashes of `record_id + "review-v1"` per shard.
  `review/sample_manifest.json` binds selection, inputs, codebook, and recoding.
- Every initially positive family, repair, restriction, or global-minimality
  assignment received another complete-packet review: **277 assignments in
  191 records**. The canonical inputs are `positive_review_01_02_07.json`
  and `positive_review_03.json`, `04`, `05`, `06`, and `08`. Individual
  `01`, `02`, and `07` files remain as original review artifacts and must not
  be counted again alongside the combined file.
- `review/ADJUDICATION_POLICY.md`, `review/corrections.json`, and
  `review/positive_review_coverage.json` retain the conservative decision rule
  and corrections. Unresolved positive claims are excluded from final counts.
  Primary annotations and original audit verdicts are not overwritten.
- `results/annotated_records.json` contains every final record, uncertainty,
  exact evidence excerpt, and its source-field character offsets. The CSV is
  a compact label export; use JSON for evidence and notes.
- `results/census.json` includes final and primary counts, strata, agreement,
  documentation lengths, and analysis provenance. `results/audit_analysis.json`
  includes audit tables and hashes of all 3,747 consumed source files.
- Reviews of the mathematics, manuscript, and aggregation code are retained
  under `review/`. These are assistant reviews, not external peer review.

## Reproduce from the repository root

The census, audit, adjudication, tests, and exact mathematical checks use
Python's standard library (tested with Python 3.9). Rendering requires
Matplotlib and NumPy (tested with Matplotlib 3.9.4 and NumPy 2.0.2).
No model calls, network calls, or new solver searches are required.

```bash
python3 qedbench_certificate_availability_triage/analysis/counterexample_structure_20260910/adjudicate_reviews.py
python3 qedbench_certificate_availability_triage/analysis/counterexample_structure_20260910/analyze_census.py
python3 qedbench_certificate_availability_triage/analysis/counterexample_structure_20260910/audit_analysis.py
python3 qedbench_certificate_availability_triage/analysis/counterexample_structure_20260910/test_analysis.py
python3 qedbench_certificate_availability_triage/analysis/counterexample_structure_20260910/mathematical_checks.py --output qedbench_certificate_availability_triage/analysis/counterexample_structure_20260910/mathematical_checks.json
python3 qedbench_certificate_availability_triage/analysis/counterexample_structure_20260910/render_paper.py
python3 qedbench_certificate_availability_triage/analysis/counterexample_structure_20260910/plot_schur_template.py --output paper_v2/figures/schur_template_structure.pdf
```

Use `analyze_census.py --validate-only` to check inputs and labels without
rewriting its outputs. Use `render_paper.py --no-figures` to regenerate the
LaTeX tables/macros without plotting dependencies. The validators reject
changed frozen sources, incomplete or duplicate coverage, malformed labels,
and nonverbatim evidence. Do not run the audit under `python -O`: validation
must remain enabled.

The original repository's validation artifacts are required for replay;
the analysis folder alone is not a replacement for those frozen sources.
The numerical scripts regenerate from retained human-readable coding;
they do not recreate the qualitative judgments or their historical blindness.

## Manuscript and figures

The anonymous paper uses the official ICLR 2027 style. The
[author guidelines](https://iclr.cc/Conferences/2027/AuthorGuidelines) specify
at most nine main-text pages, excluding references, appendices, and disclosure
statements; the [AI policy](https://iclr.cc/Conferences/2027/AIPolicyForAuthors)
requires disclosure of the research uses described here (checked 2026-09-10).
The new main text
is in `paper_v2/sections/*_structure_*.tex` and
`04_counterexample_structural_theorems.tex`; the census and proof appendices
are in `paper_v2/appendix/counterexample_*.tex`. Earlier detailed methods,
experiments, discussion, and related work are preserved as appendices.
The new AI use statement discloses qualitative coding, analysis, mathematical
derivation, code, figures, and drafting.

`render_paper.py` writes six generated LaTeX files and the census/audit
figure. `plot_schur_template.py` writes the analytic Schur contour and its
metadata. The plotting grid does not prove the continuous optimum.

With a TeX installation providing the packages used by `paper_v2/main.tex`:

```bash
cd paper_v2
pdflatex -interaction=nonstopmode -halt-on-error main.tex
bibtex main
pdflatex -interaction=nonstopmode -halt-on-error main.tex
pdflatex -interaction=nonstopmode -halt-on-error main.tex
```

`results/verification.json` records the final checked manuscript pagination,
validation results, and artifact hashes. No new transfer intervention was
run, and these changes cannot guarantee an oral acceptance.
