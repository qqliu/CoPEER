# Twelve source-conjecture deposits

This directory supplies the twelve records reported in the paper's Appendix V tables, together with their source statements, exact arithmetic checkers, saved model proof audits, and deposition-time validation results. The [index](index.json) maps each table row to its card, checker, provenance and recorded result. The [source list](sources.json) retains the cited authors, titles and versions.

These are the twelve draft additions to a 673-entry deposition database. The 661 entries used in the earlier retrieval experiments are supplied separately in [the retrieval snapshot](../../studies/proof_development/retrieval_snapshot.json), and are not duplicated here. Nine records came from `gpt-6-astra` runs, two from `gpt-5.6-sol` runs, and the short-zero-sum record came from screening a contradiction already present in its source. These labels describe generation provenance, not literature priority. The original experimental conditions and model-audit judgments are retained.

## Inspection and reproduction

From the repository root, check file hashes, all twelve table-to-artifact mappings, checker syntax, recorded exit codes and the delivered Sun parent/claim bindings:

```sh
python3 -B mathematics/discoveries/verify.py --check
```

The validation above inspects saved evidence without running the mathematical searches again. To rerun the twelve supplied deterministic exact checkers in temporary copies using the Python standard library:

```sh
python3 -B mathematics/discoveries/verify.py --replay
```

The original release reports exit code zero for all twelve checkers; [recorded_validation.json](recorded_validation.json) preserves that report and its source manifest hash. No new scientific result or model call was generated for this export. A finite checker certifies its stated finite computation; any universal argument is recorded in the corresponding card, proof or later formalization.

## Contents and source bindings

- `original_cards/`: all twelve original Markdown cards recovered from the retained review archive. Every file is byte-identical to the hash in the original discovery release manifest. Archived references to the original research checkout are preserved in these source records.
- `entries/`: twelve complete logical cards in JSON, plus readable Markdown views with portable evidence links. The JSON cards were extracted directly from the retained deposition database; its hash, each logical-card hash, and the original Markdown hashes are in `index.json`.
- `certificates/`: the twelve exact checker programs and saved evidence bundles. The six later deposits include their source inputs, baseline writeups and independent model audits alongside their checkers.
- `provenance/`: the earlier six records' saved source inputs and original proof/audit records; for short zero sums, the original source-screening decision replaces a model audit because no solver call was made.
- `MANIFEST.json`: delivered-file hashes and original source hashes. Source authors, model names, mathematical claims, verdicts and numerical results are preserved. Machine paths and execution identity fields are normalized or omitted. Original hashes in audit records continue to identify the original artifacts. The Sun checker's parent hash is rebound to its distributed, anonymized baseline; its mathematical instructions and claim hashes are unchanged.

The source-input files preserve the mathematical statements supplied in the recorded experiments. Full published papers can be accessed through the versioned primary-source links in the cards and source list.

## Later updates

The deposits preserve what was recorded at deposition; the current manuscript and [mathematical proof guide](../README.md) present the subsequent mathematical and source-attribution updates, including the following:

- The cube construction is a pullback of a published Long–Wagner set. Later formalizations establish the stated families.
- The index-ratio pair already appeared in the source's version 3 before the experiment; it refutes the archived version 2 statement.
- The original Toda witness `1 + q^2` is unimodal after the source's regrading. The stronger `B_2` witness was found during later mathematical formalization and is recorded separately from the original run.
- The rook witness lies within the source's stated exhaustive range through size eight; the manuscript retains that qualification.
- [Shaebani’s prior work](https://arxiv.org/abs/0909.2769v1) already gives the fall-coloring construction covering the frozen coloring of `C_9[K_2]` and explicitly discusses that graph. The current advancement establishes the source-specific refutation, necessity and exact counting for the stated odd-cycle family, and its formalization.
- [Hegde, Kumar and Pratibha](https://arxiv.org/abs/2609.18474v1) independently give the same two-threshold construction attaining `9/22`. The current theorem characterizes the unique optimum and stability within that two-threshold family; it does not assert a global optimum over all three-colorings or priority for attaining `9/22`.
- The Sun counterexample refutes the **second assertion of Conjecture 1.1(i)**, concerning coefficientwise q-log-convexity of the `V_{r,m}` family. This refutes the conjunction supplied as the experiment’s target; it does not separately resolve the other three assertions. Broader wording in the original card is an archival record, not the current claim. The exact source is [arXiv version 4](https://arxiv.org/abs/2505.02767v4).
- Later Lean results are supplied in the existing [mathematics directory](../) and [formal replay environment](../../bugbank/lean/README.md). The original deposit status remains `draft` in these archived records.
