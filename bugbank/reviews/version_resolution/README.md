# Review versions and final exclusions

This folder connects the recorded human judgments to the earlier 284-dossier collection and the current 147-dossier resource. It resolves membership and version questions without changing any review answer. All source and certificate paths in the JSON files are relative to the repository root.

## Current resource and benchmark

The current resource contains 147 dossiers. The main benchmark has 100 inputs, with 131 scorable inputs in total. The [membership ledger](../../core/membership.json) and [inclusion policy](../../core/policy.json) define these populations. They are different from the earlier 284-dossier resource, its 191-input primary benchmark and its 255 scorable inputs.

The earlier automated audit retained 18 dossiers with negative or inconclusive original human judgments; 13 retained their witness values and 5 received replacement witnesses. All 18 are excluded from the current 147/100/131 populations. Automated retention did not convert their human judgments into approvals. [Historical dispositions](historical18_dispositions.json) preserve the judgments, witness actions and final decisions.

## Nine negative cases in the final random audit

All nine have the same certificate bytes, source line arrays, problem, quoted claim, witness and reference labels as the reviewed versions. Their concerns cannot be dismissed here as applying only to superseded artifacts. All nine are excluded from the current resource and both benchmark populations. The table summarizes the recorded review concerns; it is not a new mathematical adjudication.

Q1 checks source fidelity; Q2 checks witness admissibility; Q3 checks correspondence with the Lean statement. Full original and distributed hashes, exact record IDs, selected declarations and exclusion reasons appear in [nine_audit_cases.json](nine_audit_cases.json). The packet links below open anonymous scientific projections; their file hashes differ from the original packet hashes.

| Packet | Negative checks | Recorded concern | Earlier benchmark | Certificate SHA-256 prefix | Final disposition |
|---|---|---|---|---|---|
| [A001](../random100/packets/A001.md) | Q3 | Formalization uses a hand-written carrier instead of the indexed group construction. | Primary191 | `51284638c1b1` | Excluded from 147/100/131 |
| [A002](../random100/packets/A002.md) | Q2, Q3 | Zero witness conflicts with an implicit nonzero parameter condition; Lean omits that condition. | Primary191 | `af06bbfe5425` | Excluded from 147/100/131 |
| [A023](../random100/packets/A023.md) | Q1, Q2, Q3 | Category labels and their translation do not establish the claimed mathematical refutation. | Primary191 | `c8e308ad5c7d` | Excluded from 147/100/131 |
| [A043](../random100/packets/A043.md) | Q3 | Transition law at population one is supplied directly rather than derived from the source model. | Primary191 | `76b30ad2964d` | Excluded from 147/100/131 |
| [A072](../random100/packets/A072.md) | Q3 | A Boolean instance is checked without formalizing the source formula and replacement operation. | Other scorable | `d47105809371` | Excluded from 147/100/131 |
| [A075](../random100/packets/A075.md) | Q1, Q3 | Source is humorous and “linear time” unspecified; Lean uses a hand-written runtime function. | Other scorable | `af1c203b5790` | Excluded from 147/100/131 |
| [A085](../random100/packets/A085.md) | Q1 | The source displays true equalities and doubt, rather than asserting the inferred false step. | Other scorable | `b0893e69a1ae` | Excluded from 147/100/131 |
| [A093](../random100/packets/A093.md) | Q1 | The passage is model setup with a typing requirement, rather than the asserted mathematical claim. | Not scored | `0e7eea1a1635` | Excluded from 147/100/131 |
| [A099](../random100/packets/A099.md) | Q1 | The quoted supposition belongs to a local case; the gap occurs later in generalization. | Not scored | `cf26d14808fe` | Excluded from 147/100/131 |

The final audit recorded 91 all-YES judgments among 100 sampled dossiers (63/67 primary and 28/33 other). One human reviewer reported AI assistance and personal checking of all 100, with prior project exposure for 28. The interval reported with this audit describes sampling uncertainty on the earlier 284-record frame under that procedure. It is neither a calibration of reviewer error nor a precision estimate for the subsequently selected 147 records. This sidecar does not establish a second independent review.

## Complete exclusion masks

[adverse_masks.json](adverse_masks.json) gives every ID, saved adverse judgment and population membership:

| Mask | IDs | Earlier primary remaining | Earlier scorable remaining | Overlap with current 100/131 |
|---|---:|---:|---:|---:|
| Negative or uncertain semantic reviews |31|173 of 191|230 of 255|0 / 0|
| Semantic reviews plus separate adverse line reviews |34|170 of 191|227 of 255|0 / 0|

The three additional line-review cases remain in the 147-record resource; their reference labels are excluded from both benchmark populations. The 31 semantic-review cases are excluded from the resource itself. Reapplying these masks to the current 100/131 inputs leaves those sets unchanged. No model outputs were rescored in this export.

## What the version evidence establishes

The original 100-review returns did not contain reviewer-supplied hashes of the particular dossier or Lean file read. Historical construction hashes identify archived files, not proof that a reviewer read those exact bytes. The final random 100 returns did provide original packet, input and certificate hashes; these agree with the archived originals. Public packets are anonymous scientific projections and retain both original and distributed hashes.

A negative Lean-correspondence judgment does not by itself establish that a localization line label is wrong. Semantic judgments, optional line checks and final scoring exclusions remain separate. Previously documented concerns keep their original negative judgments. Exclusion is not a new approval or a claim that a disputed record has been repaired.

The [export manifest](export_manifest.json) hashes the eleven files in this folder (five ledger files, the two sensitivity scripts with their outputs, and the continuity classification) and identifies the existing public evidence they use.

## Full adverse-mask exclusion sensitivity (descriptive)

`full_mask_sensitivity.py` sums the saved per-response outcomes of the earlier evaluated collection over the
frozen masks in `adverse_masks.json` (191 primary inputs -> 173 without the semantic-review mask -> 170 without
the combined mask; 255 scorable -> 230 -> 227), for all 14 saved reporting views, with unusable answers counted as
misses and no model, grader or bootstrap call. Output: `full_mask_sensitivity.json`; readable table:
`full_mask_sensitivity_table.md`. The current human-verified core has no overlap with the masks. Reproduce from
the repository root:

```sh
python3 -B bugbank/reviews/version_resolution/full_mask_sensitivity.py --release . --masks bugbank/reviews/version_resolution/adverse_masks.json --output /tmp/full_mask_sensitivity.json --table /tmp/full_mask_sensitivity_table.md
```

## Current-core subset sensitivity and continuity bindings

`current_subset_sensitivity.py` scores the 100 current primary inputs and their exact-line-reviewed (55),
separate-line-clean (27) and union (69) subsets under the current accepted-line sets, asserting that the 100-input
totals equal `benchmark/core/expected_scores.json`; outputs `current_subset_sensitivity.json` and
`current_subset_sensitivity_table.md`. `continuity_bindings_classification.json` classifies the 34 records whose
all-YES reviews apply to the current set by the authors' confirmation, by what the saved cohorts recorded.

```sh
python3 -B bugbank/reviews/version_resolution/current_subset_sensitivity.py --release . --output /tmp/current_subset_sensitivity.json --table /tmp/current_subset_sensitivity_table.md --continuity /tmp/continuity_bindings.json
```
