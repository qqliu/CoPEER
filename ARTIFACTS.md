# Paper-to-artifact guide

This guide connects the results in [the paper](paper/co-peer.pdf) to their files and replay commands; results are named by their stable LaTeX labels and topics rather than section numbers. Table, figure, and proposition identifiers below are LaTeX labels in [paper/source/main.tex](paper/source/main.tex); supporting analyses are named by topic. Component READMEs give dependencies, data schemas, and the precise scope of each check.

Run commands from the repository root unless stated otherwise. A **saved-result replay** recomputes quantities from recorded responses, labels, and usage; it makes no model calls and does not introduce new scientific judgments. A **formal replay** runs Lean on the supplied statements. Source interpretation, human review, model review, and compilation evidence retain their separate meanings in the records.

## Main results and resource

| Paper location (stable labels) | Evidence and entry point | What can be reproduced or inspected |
|---|---|---|
| Dossiers and populations (`tab:population-map`) | [Resource index](bugbank/index.json), [dossiers](bugbank/dossiers/), [line-numbered sources](bugbank/sources/), [selected formal declarations](bugbank/lean/selected_declarations.json), [census guide](bugbank/annotations/README.md) | The 284 dossiers of the earlier evaluated collection, 265 source units, certificate bindings, and population membership; the current human-verified core (147 records) is listed in the next row. The benchmark files also retain the withdrawn diagnostic explicitly. |
| Human-approved core and localization results (`tab:localization`, `tab:ccl-primary-results`) | [Membership manifest](bugbank/core/membership.json), [core guide and verifier](bugbank/core/README.md), [core replay](benchmark/core/README.md), [expected scores](benchmark/core/expected_scores.json) | The 147 retained records (137 source units, 147 Lean certificates), the 100 original-primary and 131 scorable benchmark texts, and their scores recomputed from the same saved answers. |
| Broader benchmark results (191-input set) | [Benchmark guide](benchmark/README.md), [items](benchmark/items.jsonl), [selections](benchmark/selections.jsonl), [exact saved answers](benchmark/answers/), [aggregates](benchmark/aggregates.json), [successful replay](benchmark/results/VERIFIED_RESULTS.json) | All 191-input Hit@1/Hit@3 counts and intervals, usable answers, and baselines of the earlier evaluated collection, retained as archival evidence. Fourteen reporting views map to 13 model configurations; the consolidated Haiku view is used. |
| Experiment B, `tab:b-results` | [Saved-evidence verification](studies/response_review/README.md), [primary results](studies/response_review/B_RESULTS_v1.json), [joint view](studies/response_review/B_JOINT_VIEW_v1.json) | The 24 sampled inputs, 48 generated attempts, 96 model readings, and eight adjudications. The recorded P31 interpretation is supplied separately from the original table. These are model-reader judgments. |
| `tab:instruction-main` | [Instruction studies](studies/instructions/README.md), [specified repairs](studies/repairs/README.md), [proof development](studies/proof_development/README.md), [open-problem retrieval](studies/open_problem_retrieval/README.md) | The complementary experiments summarized in the main text, with their own tasks, outcomes, and accounting. Their detailed mappings appear below. |
| counterexamples and mathematical progress | [Mathematics guide](mathematics/README.md), [principal index](mathematics/index.json), [additional statements](mathematics/extensions/index.json) | Exact failure classification and repair, structural coloring results, the optimum of a specified construction, and further formal follow-ups. See the mathematical map below. |

The current core benchmark replay uses only Python's standard library:

```sh
python3 -B benchmark/core/replay.py --release . --membership bugbank/core/membership.json --output /tmp/copeer-core-scores.json --with-intervals
```

The broader benchmark, sensitivity analysis, accounting and saved-response review also use only the standard library:

```sh
python3 -B benchmark/code/reproduce.py --output /tmp/copeer-benchmark.json
python3 -B benchmark/code/reproduce_sensitivities.py --output /tmp/copeer-sensitivities.json
python3 -B benchmark/accounting/replay.py
python3 -B studies/response_review/replay.py
```

Add `--all-populations` to the first command to include all 255 scored evaluation texts and 20 pilot texts. Add `--counts-only` for a faster count-and-parser check. Add `--comparisons` to the sensitivity command for the paired comparisons and baseline resampling; this requires substantially more bootstrap computation. Saved [sensitivity results](benchmark/results/VERIFIED_SENSITIVITIES.json) are also included.

## Reviews, source connection, and corpus accounting

| Paper location (stable labels) | Distributed evidence | Replay or inspection scope |
|---|---|---|
| selected auditing exhibits and prior acceptance | [Scientific exhibit projections](bugbank/reviews/source_continuity/source_trust/auditing_exhibits.json), [withdrawal notice](bugbank/reviews/source_continuity/source_trust/source_notice_0709_2689.json), [source-count reconciliation](bugbank/reviews/source_continuity/source_trust/source_trust_reconciliation.json) | The quoted exhibits, 8/200 and 5/43 source counts, and recorded perfect-rubric examples. The reconciliation is a version-specific snapshot, identified separately from the latest 284-record census. |
| Release-only earlier collection display (formerly `tab:corpus-sources`; both venue/mechanism tables and current category figure; removed from the paper on 2026-09-26, evidence retained) | [Current 284 annotations and identity operands](bugbank/annotations/records/), [saved summary](bugbank/annotations/records/generated/verified_counterexample_summary.json), [exact table fragments](bugbank/annotations/tables/) | Counts, source venues, witness objects, failure categories, 18 documented families and 70 documented repairs, with source-excerpt offsets. These are documentation labels. |
| `tab:recent-human-review`, `tab:human-source-joint-full`, `tab:source-concern-cases` | [Review guide](bugbank/reviews/README.md), [cohort index](bugbank/reviews/cohorts.json), [expected counts](bugbank/reviews/expected_results.json), [original 100](bugbank/reviews/original100/), [selected 33](bugbank/reviews/selected33/), [supplements](bugbank/reviews/scoped_supplements/), [selected 30](bugbank/reviews/selected30/), [random 100](bugbank/reviews/random100/) | Deidentified human judgments, available packets, stated review populations, and disagreements. The random audit includes its sample design, exact interval calculation, and nine flagged cases. Replay reconstructs the 91/100 joint approvals, weighted 91.0% estimate, interval, and component counts. |
| matched certificates and source admissibility | [Continuity guide](bugbank/reviews/source_continuity/README.md), [16-pair index](bugbank/reviews/source_continuity/PAIR_INDEX.json), [sorting bridge](bugbank/reviews/source_continuity/matched_pairs/SourceContractBridge.lean), [saved replay inventory](bugbank/reviews/source_continuity/earlier_versions/replay/MANIFEST.json) | All 16 old/current certificate pairs; 12 recovered old sources with 24 recorded compiler outcomes; 123 theorem/lemma audits; source interpretations and Gaussian correction. Static verification checks hashes and saved counts. |
| reference-line review and alternative false assertions | [Reference-line reviews](bugbank/reviews/reference_lines/), [Sonnet miss analysis](bugbank/reviews/sonnet_misses/) | Two disjoint 40-input human reference checks (35 then 38 approvals). The separate 30-case Sonnet analysis retains its model-assisted judgments and packets: 12 alternative false assertions, 15 lines not false as written, and three source/annotation issues. |
| Release-only earlier census (formerly `tab:ccl_refutation_role_census`; table removed from the paper on 2026-09-26, evidence retained) | [191-input earlier benchmark membership](benchmark/items.jsonl), [dossiers](bugbank/dossiers/), [census tables](bugbank/annotations/tables/), [paper table source](paper/source/main.tex) | The designated primary inputs and saved witness/role classifications. The benchmark scorer reproduces answer-selection results; these descriptive classifications are supplied for inspection. |
| Release-only earlier collection display (formerly `tab:structure-agreement`, `tab:structure-by-corpus`, `tab:structure-categories`; corpus procedures; removed from the paper on 2026-09-26, evidence retained) | [Earlier 401-record census](bugbank/annotations/initial401/), [annotations and aggregates](bugbank/annotations/initial401/results/), [recoding and corrections](bugbank/annotations/initial401/review/) | All 401 primary/final annotation rows and the fixed 24-record recoding sample, including agreements, uncertainties, corrections, 56 documented families, and 117 documented repairs. |
| 487 → 449 → 401 audit lineage | [Saved audit analysis](bugbank/annotations/initial401/results/audit_analysis.json), [census guide](bugbank/annotations/README.md) | All 487 record lineages, stage decisions, hash bindings, and saved aggregates. The bounded census command checks the distributed labels and counts; the original full audit pipeline is preserved as documentary source rather than a portable end-to-end execution. |

```sh
python3 -B bugbank/reviews/reproduce.py --check
python3 -B bugbank/reviews/source_continuity/verify.py
python3 -B bugbank/annotations/inspect.py
```

Review replay checks recorded judgments, not new human or model assessments. Original review rows whose packet revision was not recorded retain that status. [Resource support files](bugbank/support/) provide the additional source PDF/excerpt and executable evidence used by the specifically supported records; [phrase-continuity records](bugbank/review-continuity/) preserve the related review-to-text checks.

## Benchmark protocol, sensitivities, and costs

| Paper location (stable labels) | Evidence | Reproduction |
|---|---|---|
| `tab:local_models` | [Generation settings and exact prompts](benchmark/code/generation/README.md), [scoring settings](benchmark/code/settings.json) | Inspect recorded model environments and inference settings. Original generation drivers are included with their execution dependencies; saved-answer replay needs no provider access. |
| Release-only earlier failure table (formerly `tab:itt-valid-failures`; table removed from the paper on 2026-09-26, evidence retained) | [Per-response outcomes](benchmark/outcomes_derived.jsonl), [selected responses](benchmark/selections.jsonl), [parser/scorer](benchmark/code/) | The earlier-collection benchmark command reconstructs all scored outcomes and failure categories from saved response text and final status. |
| Release-only earlier sensitivities (formerly `tab:m27-sensitivity`, `tab:gold-sensitivity`; tables removed from the paper on 2026-09-26; the current exclusion sensitivities are in bugbank/reviews/version_resolution/) | [Reference versions and expected transitions](benchmark/code/sensitivity_data/), [saved sensitivity replay](benchmark/results/VERIFIED_SENSITIVITIES.json) | The sensitivity command reuses the same answers for the 18 revised reference sets and the 190-input source-mapping sensitivity. |
| paired contrasts and comparison discussion | [Saved comparisons](benchmark/code/sensitivity_data/comparison_expected.json), [sensitivity code](benchmark/code/reproduce_sensitivities.py) | `--comparisons` reproduces the main-set model pairs, GPT-OSS paired difference, baseline contrasts, and chance-corrected results. |
| Main token columns; release-only earlier ledger (formerly `tab:ccl-complete-cost-ledger`; table removed from the paper on 2026-09-26, evidence retained) | [Token-accounting guide](benchmark/accounting/README.md), [selected usage records](benchmark/accounting/selected_records.jsonl), [campaign attempts](benchmark/accounting/campaign_attempts.jsonl), [rules](benchmark/accounting/usage_rules.py) | The accounting command reconstructs selected-run and campaign totals from 3,809 unique selected records and 6,982 physical attempts, retaining partial observations, unknown usage, and conservative budget charges separately. |

## Complementary experiments

| Paper location (stable labels) | Evidence and command | Scope |
|---|---|---|
| Instruction study: `tab:primary-witness-components`, `tab:instruction-main`, `tab:proofs100-toolfree`, `tab:main-results`, `tab:cost-repro`, `tab:proofs100-fourarm-full-components` | [Instruction-study guide](studies/instructions/README.md); `python3 -B studies/instructions/replay.py`; `python3 -B studies/instructions/replay_intervals.py` | Exact prompts, 100-proof study inputs, responses, grades, accepted-solver token components, all four instruction arms, and saved/recomputed paired intervals. The primary Opus reproduction and earlier original run have separate records. The interval command requires NumPy. |
| Instruction reference checks: `tab:reference-sensitivity`, `tab:reference-grade-strata`, `tab:claims60-evidence`, `tab:claims60-corrected-components`, `tab:claims60-corrected-intervals`, `tab:claims60-all-sensitivities` | [Instruction reference-validity evidence](studies/instructions/reference_validity/), [corrected claims60 accounting](studies/instructions/corrected_claims60_accounting/), [reference78 coverage](bugbank/annotations/reference78/COVERAGE.json); same two commands | All 720 claims60 cells, corrected token components and intervals, source-validity and tool-use sensitivities, and the 60/78 reference-grading diagnostic. Replaying saved grades does not create new reference-validity judgments. |
| `tab:repair_outcomes`, `tab:repair_resources` | [Specified-repair guide](studies/repairs/README.md); `python3 -B studies/repairs/replay.py` | All 288 task/condition/solver/attempt cells for 16 supplied corrections, packets, prompts, 246 saved Lean files, evaluator versions, and 96 first-attempt usage records. The guide separately explains optional fresh checker execution and its dependencies. |
| `tab:proof50-results` | [Proof-development guide](studies/proof_development/README.md); `python3 -B studies/proof_development/replay.py` | Fifty paired tasks, three solvers, and two protocols, each with and without retrieval: 600 selected drafts, saved grades, and paired cost intervals. The original 661-entry retrieval snapshot is supplied separately from the current corpus; the guide includes a portable SQLite database builder. |
| `tab:historical_retrieval` | [Open-problem retrieval guide](studies/open_problem_retrieval/README.md); `python3 -B studies/open_problem_retrieval/replay.py` | The 31 original targets, five hard targets, 22 continuations, and two six-target panels. Final endpoints give 12/11 accepted outcomes among 36 targets; 58 stage observations and the two panels retain their own denominators. These are saved run-local audit outcomes. |
| 604-task witness checks | [Executable-twin guide](studies/executable_checks/README.md); `python3 -B studies/executable_checks/replay.py` | All 604 search outcomes and 351 proposed-witness checking outcomes: 348 confirmed and three rejected. This command reproduces recorded counts; it does not execute the saved programs. |
| 955 checker programs and selected 16 algorithmic records | [604-task audit and selected algorithm artifacts](studies/executable_checks/bindings/README.md), [saved program bindings](studies/executable_checks/bindings/audit/existing_955_program_bindings.json) | Exact saved search/check programs, selected results, and the earlier two-execution audit receipts. The selected 16 are distinct from the 16 repair tasks and the 16 continuity pairs. |

The experiment READMEs identify each original runner, grader, prompt, source snapshot, and token-accounting basis. Release replay uses saved outputs and grades. `python3 -B studies/replay_reviewed_projections.py` additionally verifies the exported cohort joins, source bindings, and all-instruction token-component rows. Any additional inference requires the providers, environments, and execution settings documented for that experiment.

## Mathematical statements and proofs

The [formal replay manifest](bugbank/lean/replay_manifest.json) enumerates the original 284 certificate files and 28 follow-up files, with 407 selected declarations. [Lean setup and replay instructions](bugbank/lean/README.md) pin Lean 4.30.0 and the exact Mathlib dependencies. Fifteen core-only follow-ups also have recorded Lean 4.34.0 builds. [Packaging validation](bugbank/lean/replay_validation.json) records 311 fresh successful file replays; the remaining `Cube8Mod36` process was resource-terminated locally, with its earlier successful builds retained.

| Paper result | Formal artifact or written proof | Scope of the result |
|---|---|---|
| `prop:sqrt` | [Exact failure classification](mathematics/extensions/sqrt_boundary/SqrtFailureBoundary.lean), [repair](mathematics/extensions/sqrt_repair/SE_cs_97637_a97647_repair.lean), written proof in [paper](paper/source/main.tex) | Positive perfect squares are exactly the faulty algorithm's failures; the corrected strict guard gives the integer square root for every allowed input. The source's earlier repair is credited. |
| `prop:cycle-readable`; `prop:cycle-blowup-frozen` | [CycleBlowupAllN.lean](mathematics/theorems/CycleBlowupAllN.lean) | For odd lengths at least five, frozen six-colorings exist exactly at multiples of three, with count `90 · 2^n`; source-specific conjecture hypotheses and consequence are included. |
| Larger clique replacements | [C11K3.lean](mathematics/theorems/C11K3.lean), [AllOdd.lean](mathematics/theorems/AllOdd.lean), [Q3Law.lean](mathematics/theorems/Q3Law.lean), [recorded builds](mathematics/builds/) | The fixed `C11[K3]` witness and families covering every odd `n ≥ 9`; the written argument connects the larger-bag results to the source implication. |
| `thm:schur`; `prop:schur-template-optimum` | [SchurTemplateComposed.lean](mathematics/theorems/SchurTemplateComposed.lean), written derivation in [paper](paper/source/main.tex) | Limiting density, unique optimum `9/22`, and stability for the specified two-threshold construction. |
| `tab:projective-cube-families` | [Cube5Mod16.lean](mathematics/theorems/Cube5Mod16.lean), [Cube7Mod24.lean](mathematics/theorems/Cube7Mod24.lean), [Cube8Mod36.lean](mathematics/theorems/Cube8Mod36.lean), [saved receipts](mathematics/builds/cube_families.json) | The three projective-cube-free families and their cardinalities. The recorded attribution identifies the previously published construction underlying the dimension-five case. |
| layered boundary and pullback | [LayeredBoundaryAllD.lean](mathematics/extensions/layered_boundary/LayeredBoundaryAllD.lean), [PullbackLemma.lean](mathematics/extensions/layered_boundary/PullbackLemma.lean) | Boundary arithmetic and the pullback theorem under its cube-free-base assumption. |
| `tab:explanation-census` | [Twelve explanation packages](mathematics/explanations/), [square-root failure and repair package](mathematics/extensions/sqrt_boundary/SqrtFailureBoundary.lean), [scope index](mathematics/extensions/index.json) | Thirteen selected packages with explicitly scoped family/repair statements; three also prove the intended final statement after repairing its local argument. |
| `tab:retained-mathematical-breadth` | [Resource dossiers](bugbank/dossiers/), [284 corpus certificates](bugbank/certificates/), [selected declarations](bugbank/lean/selected_declarations.json) | Seven representative mathematical certificate examples with their source passages and checked statements; one of the seven is in the current human-verified core (membership in [bugbank/core/membership.json](bugbank/core/membership.json)). Record identifiers in the table locate their files. |
| `tab:certified-research-extensions` | [Additional-statement index](mathematics/extensions/index.json): [Qrious](mathematics/extensions/04_qrious_unimodality/), [supertoken](mathematics/extensions/06_supertoken_metric/), [Gaussian polynomial](mathematics/extensions/07_fake_gaussian/), [Sun](mathematics/extensions/09_sun_qlogconvex/); also [supporting sources](mathematics/supporting/README.md) | Exact selected statements, axiom scope, receipts, source connections, and known-construction overlaps. Coefficientwise assertions retain that meaning. |
| Original finite coloring certificate and additional research kernels | [Seven supporting sources and receipts](mathematics/supporting/index.json) | Original `C9K2`, full `PrimeBlowup`, exact `RainbowSchur` count, `RookSpectrum`, regrading-robust `TodaNumerator_Exact`, and the short-zero-sums contradiction plus sanity checks. These carry saved build evidence and are outside the 312-file fresh-replay inventory. |
| `tab:new-conjecture-counterexamples`, `tab:additional-astra-refutations` | [Twelve discovery deposits](mathematics/discoveries/README.md), [deposit index](mathematics/discoveries/index.json), [exact original cards](mathematics/discoveries/original_cards/) | Source inputs, proof drafts, audits, exact checkers, results, and deposit cards for all twelve rows. The index and later-scope notes connect original deposits to subsequent formal results and qualifications. |
| `prop:transport`, `prop:partial`, `prop:sharp-comparison`, `prop:perturb` | Written statements, constructions, and proofs in [paper/source/main.tex](paper/source/main.tex) | Refutation transport, partial identification, sharp paired comparison bounds, and prediction-aware reference perturbations. These analytic results are supplied as written proofs. |

After the dependency setup in the formal README:

```sh
python3 -B bugbank/lean/replay.py --check-inventory
python3 -B bugbank/lean/replay.py --exclude Cube8Mod36 --jobs 1 --output /tmp/copeer-lean-replay
python3 -B mathematics/supporting/verify.py
python3 -B mathematics/discoveries/verify.py --check
```

The first command checks hashes without invoking Lean. The second compiles the standard selection and audits its selected declarations. The last two verify the supporting and discovery inventories and saved evidence; they do not claim new compilation. Optional exact discovery-checker execution is documented in the discovery guide. Supporting core Lean files can be compiled individually with, for example, `elan run leanprover/lean4:v4.30.0 lean mathematics/supporting/sources/PrimeBlowup.lean`.

`Cube8Mod36.lean` took about 30–37 minutes in its recorded successful runs; the original job reserved 160 GB, which is an allocation rather than a measured minimum. On a suitable machine, use `python3 -B bugbank/lean/replay.py --select Cube8Mod36 --jobs 1 --timeout 7200 --output /tmp/copeer-cube8-replay`. The saved receipts are available for inspection without repeating that computation.

## Figures, manuscript, and integrity checks

| Paper location (stable labels) | Source and replay |
|---|---|
| `fig:palettes` and `fig:scope` / `fig:objection-dossier` | Inline TikZ in [paper/source/main.tex](paper/source/main.tex); render with the manuscript build. The diagrams illustrate the coloring mechanism and the two distinct scopes of the path counterexample. |
| `fig:schur-template-structure` | [Exact submitted PDF](paper/figures/schur_template_structure.pdf), [plot source](paper/figures/source/plot_schur_template.py), [figure instructions](paper/figures/README.md). Run `python3 paper/figures/source/plot_schur_template.py --output /tmp/schur_template_structure.pdf`. The plotted grid illustrates the objective; the mathematical proof is mapped above. |
| Release-only earlier collection display (formerly `fig:verified-counterexample-categories`; removed from the paper on 2026-09-26, evidence retained) | [Exact submitted PDF](paper/figures/verified_counterexample_categories.pdf), [record-level current census and original renderer](bugbank/annotations/records/). The bounded census check reproduces its category counts. |
| `tab:related`; bibliography | Citations and comparison text are embedded in [paper/source/main.tex](paper/source/main.tex). These are literature comparisons, not additional experimental observations. |
| Manuscript and all embedded tables/appendices | [Paper folder guide](paper/README.md): the verified PDF `paper/co-peer.pdf`, the arXiv source bundle `paper/co-peer-arxiv-source.tar.gz`, and its extracted copy under `paper/source/` (compile with `pdflatex main.tex` three times; `main.bbl` is included). |
| Admission/integrity procedures and attack-set claims | [Integrity guide](studies/audit_tests/README.md), [attack fixtures](studies/audit_tests/attack_set/). This includes six source/artifact-rebinding cases, three clean controls, runnable selected tests, and separately identified original audit receipts. |

Run the integrity checks from their directory:

```sh
cd studies/audit_tests
python3 -B verify_public_hashes.py
python3 -B attack_set/run_attack_set.py
python3 -B run_selected_tests.py
python3 -B run_selected_tests.py --synthetic-tests
```

The integrity README distinguishes these portable checks from the saved larger test suite and Lean-mutation receipts. Component manifests bind distributed files; original hashes retained inside projected archival records identify their original bytes. All portable commands above operate on the release paths, while archived research drivers remain identified as provenance in their component guides.
