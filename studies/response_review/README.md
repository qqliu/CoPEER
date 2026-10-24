# Saved-evidence verification (Experiment B)

This study examines the mathematical evidence in 48 saved responses: one response
from Gemini 3.1 Pro and one from Nemotron 3 Super 120B on each of 24 randomly sampled
benchmark inputs. Each response received two blinded reviews by LLM agents. The
primary review was assigned separately for each response; R1–R4 each served as a
first and second reviewer on different responses. Eight flagged cases also
received adjudication. Exact reviewer model versions are not recorded in the
original protocol or review metadata.

Run the offline replay from the repository root with Python 3.10 or newer:

```sh
python3 -B studies/response_review/replay.py
```

The command verifies the distributed hashes, reproduces the 24-input sample,
replays the frozen parser and scoring functions on all 48 saved answers, checks
the assigned reviews, and reproduces the reported first-review tables. It makes
no model calls and does not change any recorded judgment. The `frozen_functions/`
modules contain only the pure functions and constants extracted from the original
bound parser/scorer sources; their function AST hashes were checked during export.

Parsing the full saved text reproduces every recorded candidate slot and score.
Four records differ only in parser metadata: P09, P25 and P48 count two candidate
array occurrences instead of one; P46 identifies a complete JSON object where
the recorded metadata identifies an array fallback. The replay reports these
differences explicitly and preserves the original audit fields.

## Results and interpretation

| Configuration | Reference hits: valid / invalid / unresolved | Reference misses: valid / invalid / unresolved |
|---|---:|---:|
| Gemini 3.1 Pro | 18 / 0 / 2 | 3 / 1 / 0 |
| Nemotron 3 Super 120B | 16 / 2 / 0 | 5 / 0 / 1 |

These are the original first-review assessments in `B_RESULTS_v1.json`.
`B_ADJUDICATION_SUMMARY_v2.json` preserves the later adjudication and its separate
source-assumptions interpretation. Under that interpretation, P31 is an invalid
objection to the source because its supplied witness violates the source's
assumptions. Nemotron's reference-hit evidence then has 15 valid and 3 invalid
assessments. The original table and all line-selection scores stay unchanged.
`B_ADJUDICATION_SCOPE_REVIEW.md` explains the scope of P31, P35 and P43.

## Contents

- `packets/`: the 48 blinded source-and-response packets, including line labels.
- `readings/`: 96 initial assessments, eight adjudications, and their Python and
  Lean checking sources. These are recorded LLM assessments, with kernel, exact
  computation, and analytic evidence distinguished by the J3 labels.
- `B_PROTOCOL_v1.md`, `ASSESSMENT_TEMPLATE.json`, `READER_ASSIGNMENT_PLAN.json`:
  study instructions, rubric, and first/second-review assignments.
- `B_COMMITMENT.json`, `PRIMARY_POPULATION_IDS.json`, `B_SAMPLE_FREEZE.json`:
  sampling commitment, population, chosen records, and the released packet key.
- `saved_attempts/`: saved answers and selected generation metadata needed to
  replay parsing and scoring, with model names and recorded usage preserved.
- `REFERENCE_ITEMS_SAMPLE.json`: the 24 sampled reference items used by the scorer.
- `B_RESULTS_v1.json`, `B_JOINT_VIEW_v1.json`, `B_ADJUDICATION_SUMMARY_v2.json`:
  original first-review results and separately labeled additional analyses.
- `READING_LOCKS.json`, `PACKETS_MANIFEST.json`, `MANIFEST.json`: content hashes.
- `original_analysis/`: original analysis source retained for inspection. Its
  research-directory layout is not portable; use `replay.py` for this release.

The checker scripts are additional inspectable evidence. Python scripts use the
standard library. The ten Lean files import Mathlib; this experiment folder does
not contain the original compiler receipts or a pinned Lean environment. The
offline replay verifies their distributed contents but does not claim to rerun
Lean or replace the recorded mathematical reviews.

## Distribution transformations

The export removes machine paths, account/session identifiers, raw execution logs,
and internal coordination pointers. Third-party contact emails and one published
source's residential contact address are redacted in place; source line labels,
mathematical content, source author attribution, and citations are preserved.
Reader IDs and generation model names are preserved.

`MANIFEST.json` identifies both distributed and original content hashes for copied
artifacts. `READING_LOCKS.json` records the checks against the last original lock
for each assessment. Hashes inside the original result and adjudication files
refer to the original evidence unless explicitly named as distributed hashes.
The sampling seed retains its original committed input digests. The packet and
sample manifests additionally identify the distributed file hashes and paths.
