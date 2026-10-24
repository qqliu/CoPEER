# Source continuity: matched certificates and saved replays

This package supplies the evidence for Appendix D.3, “Matched certificates
with different source admissibility.” It links the original and replacement
objections for the fixed 16-record audit and preserves the saved checking and
interpretation records. Exporting these files ran no Lean compiler, model, or
new semantic review.

The adjacent `source_trust/` projections preserve six selected Appendix A
scientific exhibits, the saved arXiv 0709.2689 withdrawal notice, and the
source-denominator reconciliation supporting 8/200 vetted answers, 5/43
accepted answers, and the two retained QEDBench examples with perfect recorded
human rubric scores. The reconciliation is its original version-specific
snapshot; its references to “current” status are not a new census of this
release. Human-reviewer identities and assignment metadata are omitted.

Start with [PAIR_INDEX.json](PAIR_INDEX.json). For every one of the 16 records,
`roster/` contains both Lean sources, the source dossier, the old/current
mathematical fields, and the replacement certificate's saved receipt and logs.
The stored problem and source-context strings agree in all 16 pairs; the
challenged quote agrees in 15. Selection was by the recorded replacement
outcome. These are audit exhibits, not a repair-yield experiment.

## Evidence map

- [matched_pairs/](matched_pairs/README.md) preserves the initial roster audit,
  the three same-quote pairs with authenticated retained old/new compilation
  evidence, and the sorting exhibit. The three records are `SE_cs_81391__q`,
  `SE_math_4219732__q`, and `mse_811862__ans811879`.
- [SourceContractBridge.lean](matched_pairs/SourceContractBridge.lean) and its
  [saved receipt](matched_pairs/SourceContractBridge.RECEIPT.json) check the
  sorting endpoint condition. The original array fails that condition; the
  replacement satisfies it. The failed initial elaboration is retained
  separately and is not counted as a successful build.
- [The replay manifest](earlier_versions/replay/MANIFEST.json) covers
  the other 12 historical sources: all 24 saved compilations passed, one each
  under Lean 4.30.0 and 4.34.0. Sources, commands, saved compiler-output tails,
  full axiom output, and axiom drivers are included. These later replays
  establish reproducibility of the recorded source bytes; four other records
  have authenticated earlier build receipts, kept separately in
  `roster/*/old_receipts/`.
- [The independent artifact review](earlier_versions/review/HISTORICAL_REPLAY_INDEPENDENT_REVIEW.md)
  accounts for all 123 theorem/lemma declarations: 78 use no axioms, 42 use
  `propext`, and three use `propext` with `Quot.sound`. Three axiom drivers also
  queried words extracted from comments and exited with unknown-name errors;
  their saved output still covers every genuine theorem/lemma declaration.
  This review is a saved model-assisted artifact audit, not a new human review.
- The [four-case](earlier_versions/review/REPAIR_PAIR_SEMANTIC_READ_FOUR.md)
  and [Reddit](earlier_versions/review/REPAIR_PAIR_SEMANTIC_READ_REDDIT.md)
  semantic readings explain per-record source assumptions and retained
  admissible alternatives. Compilation alone does not determine source
  applicability.
- [The Gaussian equality correction](earlier_versions/gaussian/)
  preserves the current fields and certificate for `mse_605342__ans609345`.
  This is distinct from the covariance/ensemble strict pair
  `mse_811862__ans811879`.

## Versions, hashes, and portability

From the supplement root, run:

```sh
python3 bugbank/reviews/source_continuity/verify.py
```

This checks every distributed payload hash and all 32 old/current Lean source
hashes, then checks the saved replay inventory and declaration counts. It
performs no compilation, model call, or new mathematical judgment.

The initial matched-pair snapshot reports 15 recovered historical sources.
The later replay recovers the sixteenth by preserving its two final newlines.
Both snapshots are retained; the combined index contains all 16 exact old
source hashes. Here “current” means the replacement version in this continuity
audit, not automatic identity with every subsequent release revision.

[MANIFEST.json](MANIFEST.json) records the SHA-256 of each original and
distributed file. Lean source bytes are unchanged. Operational machine paths
in receipts, saved logs, and archival scripts are replaced with
`RESEARCH_ROOT`, `USER_HOME`, `ARCHIVED_WORKTREE`, `ARCHIVED_REPLAY_ROOT`,
`ARCHIVED_COMPILER_ROOT`, `ARCHIVED_CHECK_ROOT`, or `MANUSCRIPT_ROOT`;
an internal review-workbook filename is replaced with
`ANONYMIZED_REVIEW_WORKBOOK`. Receipt-internal hashes continue to identify the original
bytes; the export manifest supplies the corresponding distributed hashes.
Scientific-field projections omit human-review and assignment metadata.
Source authors and mathematical source links are preserved.

Copied historical READMEs, scripts, and integration manifests describe their
original execution setting and may name unbundled repository locations.
They are archived provenance, not stand-alone commands for this relocated
package. Use the package-level formal instructions for any new compiler
execution. The saved compiler outcomes above are observations from the
recorded runs, not fresh results produced by this export.
