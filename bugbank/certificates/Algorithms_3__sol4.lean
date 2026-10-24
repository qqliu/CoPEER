import Mathlib
namespace QEDReview3sol4
/-- At the original delta=1, both Bernoulli measures named in the source are the same. -/
noncomputable def halfCoin : MeasureTheory.Measure Bool :=
  (PMF.bernoulli (1 / 2) (by norm_num)).toMeasure
noncomputable def geometricBoundAtOne (n : ℕ) : ℝ :=
  ((1 + 1 : ℝ) ^ 4 / (1 + 2 * 1 : ℝ) ^ 3) ^ n
noncomputable def claimedKLBoundAtOne (n : ℕ) : ℝ :=
  Real.exp (-(n : ℝ) * (InformationTheory.klDiv halfCoin halfCoin).toReal)
/-- Original witness, now using Mathlib's measure-theoretic KL divergence. -/
theorem refuted (n : ℕ) (hn : 0 < n) :
    (0 : ℝ) < 1 ∧
    InformationTheory.klDiv halfCoin halfCoin = 0 ∧
    geometricBoundAtOne n = (16 / 27 : ℝ) ^ n ∧
    claimedKLBoundAtOne n = 1 ∧
    geometricBoundAtOne n < claimedKLBoundAtOne n := by
  have hkl : InformationTheory.klDiv halfCoin halfCoin = 0 := by
    unfold halfCoin
    exact InformationTheory.klDiv_self _
  have hbound : claimedKLBoundAtOne n = 1 := by
    simp [claimedKLBoundAtOne, hkl]
  refine ⟨by norm_num, hkl, ?_, hbound, ?_⟩
  · norm_num [geometricBoundAtOne]
  · rw [hbound]
    have he : geometricBoundAtOne n = (16 / 27 : ℝ) ^ n := by norm_num [geometricBoundAtOne]
    rw [he]
    exact pow_lt_one₀ (by norm_num) (by norm_num) (Nat.ne_of_gt hn)
end QEDReview3sol4
