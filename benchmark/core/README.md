# Replay the human-approved evaluation core

Run from the release root with Python 3 (standard library only):

```sh
python -B benchmark/core/replay.py \
  --release . \
  --membership bugbank/core/membership.json \
  --output /tmp/core_scores.json
```

This single command first reconstructs the retained resource from the anonymous
human-review evidence. It then verifies the saved model answers, parses them with
the unchanged scoring code, and reproduces the **100-input primary evaluation**
and **131-input scored evaluation**. It checks both endpoints against
`expected_scores.json`, including usable-answer counts, failure causes, baselines
and token accounting for precisely those inputs. Membership is fixed before
scores are calculated.

Add `--with-intervals` to reproduce all 66 confidence intervals using the original
group-stratified problem-cluster bootstrap with 10,000 resamples. Counts-only
replay checks every other reported numerical field. The 13 model configurations
and the separate active-Haiku reporting view use the existing saved outputs;
the two Haiku views share physical calls.

`reference_line_coverage.json` separately records optional reference-line checks
and the two three-question span-review samples. The replay preserves the
distinction between source-claim approval and reference-line review. It excludes
the three retained conflicts on unchanged reference-label sets under the fixed
membership policy.

The reported token amounts sum only the selected input rows in each view. The
JSON distinguishes complete recorded usage, observed lower bounds, incomplete
telemetry and budget charges. Campaign-wide costs are a separate analysis.

`PROVENANCE.json` binds the accepted scientific results, their independent
verification, and this public adapter. The active resource index may contain
only retained core entries. The original benchmark inputs, saved answers and
review evidence retain their original bindings for reproducibility. Neither this
command nor the interval replay calls a model or changes a mathematical judgment.
