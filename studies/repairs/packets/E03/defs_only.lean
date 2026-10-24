/-
Record SE_cs_13118__a13122 (E03): Mathlib file (reals and arbitrary fields).

The source's summation operator is `Sigma(T)(n) = ∑_{k=1}^{n-1} T(k)` (lower limit k = 1),
stated below in `Finset.Icc` form.  The located line asserts, for `c ≠ 1` and `n ≥ 1`, the
closed form `Sigma(c^·)(n) = (c^n - 1)/(c - 1)`; read universally over the reals it is
`LocalClaim`.  Lean's `/` on ℝ is total (`x / 0 = 0`) and `n - 1` is truncated on ℕ.
-/
import Mathlib
namespace SE_cs_13118_a13122_explanation_real

/-- The source's operator `Sigma(T)(n) = ∑_{k=1}^{n-1} T(k)` in `Finset.Icc` form. -/
def Sigma {K : Type*} [Field K] (T : ℕ → K) (n : ℕ) : K := ∑ k ∈ Finset.Icc 1 (n - 1), T k

/-- The located line, read universally on its stated domain (`c ≠ 1`, `n ≥ 1`) over ℝ. -/
def LocalClaim : Prop :=
  ∀ (c : ℝ) (n : ℕ), c ≠ 1 → 1 ≤ n →
    Sigma (fun k => c ^ k) n = (c ^ n - 1) / (c - 1)

end SE_cs_13118_a13122_explanation_real
