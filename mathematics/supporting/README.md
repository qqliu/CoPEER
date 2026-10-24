# Additional formal artifacts cited in the appendices

These seven unchanged, standalone core-Lean sources preserve the particular
formal statements cited in the appendices on the structural case studies and on the further
certified families. They complement the 28 follow-up
files covered by the main Lean replay inventory.

| File in `sources/` | Paper claim and selected statement |
|---|---|
| `C9K2_frozen_coloring.lean` | Appendix A's original finite-coloring certificate, `C9K2.frozen_six_colouring_certificate`; the full conjecture antecedent is supplied by the later graph proofs. |
| `PrimeBlowup.lean` | The source conjecture fails at the doubled nine-cycle, including its antecedent: `Recol.not_conjecture1`. |
| `RainbowSchur.lean` | Exact ordered-triple count for every positive size parameter and the asymptotic contradiction: `witness_count`, `not_tightnessConjecture`. |
| `RookSpectrum.lean` | Count 155 on the eight-by-eight permutation grid: `RookSpectrum.not_conjecture310`, `RookSpectrum.rpCount_G8`. |
| `TodaNumerator_Exact.lean` | The later type-B2 witness using the exact denominators-cleared recurrence: `Exact.not_conjecture73_exact`. Its relation to the source rational functions uses the algebraic argument described in Appendix M. |
| `ShortZeroSums_Conjecture.lean` | General wrapper for the printed source-internal contradiction: `Gen.not_conjecture62`. |
| `ShortZeroSums_Conjecture_Sanity.lean` | Equivalent formulation and true-instance checks away from the refuting instance, including `Rev.conj62_true_at_C2_C4`. |

`index.json` binds every proof, log and projected receipt by SHA-256. The receipts
retain selected declarations and mathematical scope. The accompanying 14 logs
record earlier compilation and axiom output under Lean 4.30.0 and 4.34.0. For the
two short-zero-sum wrapper files, the original receipt assesses success from the
saved compiler text and does not record a process exit code. Mutation outcomes
are preserved as recorded review observations; individual mutant logs were not
retained. These seven files were **not newly compiled during this export** and
are separate from the 312-source packaging replay.

From the repository root, verify the distributed evidence with Python's standard
library:

```sh
python mathematics/supporting/verify.py
```

For an optional fresh compilation, install the desired pinned Elan toolchain
and run, for example:

```sh
elan run leanprover/lean4:v4.30.0 lean mathematics/supporting/sources/PrimeBlowup.lean
elan run leanprover/lean4:v4.34.0 lean mathematics/supporting/sources/RainbowSchur.lean
```

Every file is self-contained and needs no Mathlib or first-party imports.
Each includes its original axiom-print commands. The saved reviews concern
formal/source scope; later stronger formalizations and earlier discoveries
retain their separate provenance in the paper.
