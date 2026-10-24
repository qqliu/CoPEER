# Natural objection-replacement pairs: fixed-roster artifact audit

This package preserves all **16** records marked `RETAINED` and
`REPLACED_INVALID` in the completed 425-record release ledger. It adds no new
semantic labels. Selection is defined by the historical replacement outcome;
these records cannot estimate repair yield, error prevalence, or a causal
effect of source review.

The artifact audit finds:

| Binding check | Records |
|---|---:|
| Fixed replacement roster, with no dropped rows | 16 |
| Frozen source-packet hash matches | 16 |
| Identical stored problem and source-context strings | 16 |
| Identical stored challenged-quote strings | 15 |
| Historical Lean bytes recovered from the frozen packet | 15 |
| Historical successful compilation authenticated to exact bytes | 4 |
| Historical compilation unbound in the documented bounded search | 12 |
| Current certificate and compilation logs authenticated | 16 |
| Same-quote pairs with both historical and current compilation evidence | 3 |

“Identical” compares the stored UTF-8 field strings. It does not establish
that the stored excerpt contains every source hypothesis, revalidate a live
webpage, or constitute an independent human source-fidelity judgment.
“Unbound” means that this bounded search did not authenticate an old-byte
receipt; it does not mean that the historical certificate failed compilation.

The fourth authenticated historical certificate is
`Algorithms_27__sol3`. Its challenged-quote text changes, so it remains in
the fixed roster but is outside the strict three-pair package. The historical
Lean hash of `mse_605342__ans609345` was not recovered by the documented
embedded-source extraction recipe. Every exclusion is explicit in
[RESULTS.json](RESULTS.json).

## Three paired examples

- **Main exhibit candidate:** [endpoint order in gap sorting](pairs/SE_cs_81391__q/EXHIBIT.md).
- [Finite equality versus an eventual asymptotic assertion](pairs/SE_math_4219732__q/EXHIBIT.md).
- [Gaussian ensemble mismatch](pairs/mse_811862__ans811879/EXHIBIT.md).

Each pair contains the unchanged stored source context and challenged quote,
raw historical and replacement witnesses, the existing audit's explanation,
exact selected theorem headers, and complete old/current Lean files. The
certificate files, compiler logs, axiom logs, and receipts are copied without
changing their bytes. Additional compiler-environment and instrumented-source
evidence is pinned by repository path and hash. Receipt commands retain their
original worktree paths; a relocated file is used only after its bytes match
the recorded hash.

Both proofs compiling is a fact about their encoded propositions. Whether
their objects and assumptions match the quoted mathematics is a separate
semantic judgment. The old raw text includes some broader numerical-search
or universality assertions; reproducing that text does not certify those
assertions. These are inspection exhibits, not blinded evaluation prompts.

## Endpoint exhibit and supplementary relevance lemma

The stored source passage at line `0024` explicitly says
`My initial array is A = {x_0, ..., x_n} and i have x_0 < x_n`.
The historical array is `[3,4,2,5,1]`; the replacement is
`[3,5,2,6,1,7,4]`. The selected current certificate already checks the
replacement's endpoint inequality, first exchange, sorted output, and failure
of the claimed first-entry conclusion. Its definitions and proofs also retain
the original example.

[SourceContractBridge.lean](SourceContractBridge.lean) is a supplementary
artifact: the exact 9,669-byte current certificate is its unchanged prefix,
followed by a definition of the endpoint predicate and three new lemmas.
These establish the original array's failure of that predicate, its inability
to satisfy the predicate together with the proposed objection conditions,
and the replacement's satisfaction of those conditions by reuse of the
existing theorem. This mechanizes the specified endpoint mismatch; it does
not prove that prose and formal predicates have identical meaning, or that
the entire source proof is invalid.

The new build receipt is
[SourceContractBridge.RECEIPT.json](SourceContractBridge.RECEIPT.json), with
[compiler/axiom output](SourceContractBridge.compile.log). Its status and
hashes are the authority for successful verification. The initial elaboration
attempt and diagnostic are preserved separately; it is not a successful
certificate. Neither historical nor current source certificate was edited.

## Reproduction

From the research repository, run:

```sh
python3 astra/final_afternoon_20260920/repair_pair_audit/generate.py
```

This rechecks the frozen roster, source and receipt hashes, regenerates the
three paired exhibits, and writes `RESULTS.json`. It does not compile Lean,
call models, access the network, or relabel examples. It fails if pinned inputs
change. `FROZEN_INPUTS.json` preserves the complete initial read-only audit,
including the search scope, all 16 rows, and unavailable-receipt cases.

The supplementary Lean build is separate from that read-only generator. Its
receipt records the exact command, source and compiler hashes, selected
declarations, prefix identity, exit code, and log hash. A compiler replay would
be a new execution, not a claim about an old receipt.
