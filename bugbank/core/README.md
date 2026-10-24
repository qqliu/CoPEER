# Human-approved current core

The retained core contains **147 dossiers from 137 source units**, with 147 distinct
certificate files. Of these dossiers, 113 have exact current scientific-content
bindings to saved positive reviews; 34 additionally rely on the project owner's
confirmation that earlier positive reviews apply to the current set. Every record
has a saved YES on each of source interpretation, witness validity and Lean
correspondence. Records with retained adverse human judgments or unresolved source
scope are excluded.

Run this script with the package root as `--release` (Python standard library only):

```sh
python -B bugbank/core/verify.py --release . --output core_verification.json
```

The script reconstructs the selected union from the anonymous review tables,
checks the continuity receipt and per-record scientific content/certificate hashes,
and recovers **100** entries in the original primary benchmark and **131** across
all originally scorable entries. These counts exclude three adverse judgments on
unchanged reference-label sets. Full original source-version identity for those
older line-review sheets is not established; their exclusions are conservative.
The original review tables remain available as evidence of both approvals and
exclusions. No private spreadsheets, reviewer identities, model calls or Lean
installation are needed.

`membership.json` includes all 284 screened IDs, the eligibility decisions, exact
current content hashes, source-unit mapping, and retained benchmark masks.
`policy.json` records the frozen inclusion rule. `author_continuity_receipt.json`
records the project-owner attestation. Both continuity tiers remain explicit; the
receipt adds no new human votes and does not claim multiple independent reviews
per record. These selected-core counts do not reuse the earlier random audit's
population interval as an accuracy interval for this selected union.

The verifier also checks the current gold labels, source text, group, split and
original benchmark roles against the immutable `benchmark/items.jsonl`, and
recomputes source units from the published 284-dossier annotation mapping. Preserve
these original benchmark and census files when pruning the resource index.
The current source and certificate content is checked even if other package metadata is
reorganized. Whole-file source/dossier hashes for the preselection release are
preserved in the internal audit; the public check hashes their scientific fields
and complete source-line arrays, and requires byte-identical certificates.
