# Reproduce the false-assertion identification results

The earlier evaluated collection contains 191 texts in its evaluation set; the current human-verified core and its replay are in [`core/`](core/README.md). This directory provides the saved model responses, reference labels, parser, scoring rules, and bootstrap code. The replay independently parses the answer files and checks every resulting score against the published results.

From the repository root, run:

```bash
python3 -B benchmark/code/reproduce.py --output /tmp/copeer-benchmark-replay.json
```

This reproduces the main-set Hit@1 and Hit@3 counts, their 95% confidence intervals, usable-answer counts, failure categories, and all five baseline means and intervals. It uses Python 3.9 or later and only its standard library. It needs a CPU and a few minutes; the saved-answer replay works offline without a GPU, model installation, credentials, or provider account.

To check all populations, including the 255 scored evaluation texts and the 20 pilot texts:

```bash
python3 -B benchmark/code/reproduce.py --all-populations --output /tmp/copeer-all-results.json
```

For a faster check of all answer parses and all counts, add `--counts-only`. The existing successful full replay is [replay/VERIFIED_RESULTS.json](results/VERIFIED_RESULTS.json).

## Data and source files

- `items.jsonl`: 285 line-numbered inputs, with reference labels, split assignments, and current population masks. Of these, 284 belong to the current resource; the withdrawn diagnostic remains explicitly identified. The 255 scored evaluation texts include the 191 main texts.
- `selections.jsonl`: one selected output per view and input, its answer hash, candidate slots, and final attempt status. Fourteen reporting views cover 13 model configurations.
- `benchmark/answers/`: the exact selected answer bytes, named by SHA-256.
- `../bugbank/sources/`: the same source lines and labels, plus the problem-cluster identifiers used for resampling.
- `aggregates.json`: the reported rates, intervals, and recorded token-accounting summaries.
- `accounting/`: numeric usage inputs, original accounting rules, and a portable replay of the table and campaign totals.
- `outcomes_derived.jsonl`: an inspectable outcome for each scored response. The replay recomputes these outcomes from answer text and status metadata and compares every row.
- `code/frozen_common.py` and `code/frozen_score.py`: verbatim scientific function and constant statements extracted from the frozen parser and scorer. `code/provenance.json` records original source hashes, distributed hashes, and unchanged scientific AST hashes.
- `code/settings.json`: view identifiers, visible-answer rules, original bootstrap seed tags, baseline comparison values, and the mapping from the 14 reporting views to the 13 manuscript rows.
- `code/generation/`: exact prompt templates, recorded inference settings, and anonymized source snapshots of the original generation drivers. Its README explains the execution dependencies.

The manuscript uses the consolidated `EXP5__claude-haiku-4-5-20251001` view for Haiku. The `EXP1__claude-haiku-4-5-20251001` view preserves an earlier reporting scope of the same physical lane. They are separate reporting views and share some responses; their costs should not be added.

## Scoring and intervals

The parser selects the last recognized candidates object, applies the frozen normalization rules, and keeps the original first three candidate positions. Invalid or duplicate positions stay empty; later positions do not move forward. Local-model answers are parsed after the last closing `</think>` tag, exactly as in the recorded pipeline. The replay verifies both the complete answer hash and the visible-text hash, then checks the hash of the full parser audit.

The frozen outcome rule uses the recorded final attempt class and stop evidence. Budget exhaustion, protocol violations, setup failures, transport failures, empty answers, and invalid candidate slots contribute zero to the reported all-input match rates. The replay reconstructs the fields needed by this rule from `final_attempt_status`; it checks all 3,850 scored outcomes and parses all 3,990 selections.

Confidence intervals use 10,000 percentile-bootstrap resamples of merged problem clusters within source group. Related inputs stay together. The exact seed tags are retained in `code/settings.json`, so the replay reproduces the stored intervals. The five baselines are random-line expectation, longest line, most words, most mathematical symbols, and greatest TF–IDF similarity to the document centroid. The exported scorer also contains the original comparison code that reselects the strongest deterministic baseline inside each bootstrap replicate.

The portable replay above verifies answer scoring. The separate [token-accounting package](accounting/README.md) recomputes Table 2's recorded token counts and Appendix P's campaign totals from the released numeric usage projections:

```bash
python3 -B benchmark/accounting/replay.py
```

Its inputs bind 3,809 unique selected records to all 3,990 item/view selections and retain 6,982 distinct physical attempts for campaign accounting. They preserve native usage fields, partial observations, unknown usage, and conservative budget charges, with original evidence hashes. These are numeric projections of the recorded evidence; private provider envelopes and session transcripts are excluded, and usage that was never logged remains unknown.

## Reference-label and comparison analyses

The original, corrected, and final reference labels for all 285 inputs are in `code/sensitivity_data/gold_versions.json`, with hashes of their source files. The fixed main set contains 18 changed reference sets; the same selected answers can be scored against each version. The source-mapping sensitivity removes the recorded conditional case `proofwiki_13793__codex_expansion` and uses the other 190 texts and 172 clusters. This post hoc analysis retains the same answers and final reference labels.

```bash
python3 -B benchmark/code/reproduce_sensitivities.py --output /tmp/copeer-sensitivities.json
```

This verifies every view's label-version totals and individual gain/loss transitions, and reproduces the 190-item rates and newly calculated intervals using their original seed tags. To also reproduce all 91 main-set model pairs for both Hit@1 and Hit@3, all model-to-baseline comparisons, chance-corrected results, and the strongest-baseline resampling comparisons, run:

```bash
python3 -B benchmark/code/reproduce_sensitivities.py --comparisons --output /tmp/copeer-comparisons.json
```

The full comparison command performs substantially more bootstrap calculations. `--counts-only` verifies all point estimates without recalculating intervals. Saved comparison results for all three populations are supplied in `code/sensitivity_data/comparison_expected.json`; `reproduce_sensitivities.py --comparisons` recomputes the main-population comparisons. The successful full main-population sensitivity replay is `replay/VERIFIED_SENSITIVITIES.json`. This covers the GPT-OSS paired difference and Sonnet's comparison with random-line selection reported in the paper.
