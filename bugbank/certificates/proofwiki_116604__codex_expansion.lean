import Mathlib
/-! The literal local identity F(x)=exp(x) fails at the positive real x=1.
The integral and exponential below are Mathlib's analytic definitions. -/
noncomputable section
namespace ProofWiki116604CodexExpansion
open scoped Interval

def F (x : ℝ) : ℝ := ∫ t in (1 : ℝ)..x, 1 / t

theorem refutes_published_exponential_identity :
    0 < (1 : ℝ) ∧ F 1 = 0 ∧ Real.exp 1 ≠ 0 ∧
    ¬ (∀ x : ℝ, 0 < x → F x = Real.exp x) := by
  have hf : F 1 = 0 := by simp [F]
  refine ⟨by norm_num, hf, Real.exp_ne_zero 1, ?_⟩
  intro h
  exact Real.exp_ne_zero 1 ((h 1 (by norm_num)).symm.trans hf)

theorem negative_control_logarithmic_comparator : F 1 = Real.log 1 := by
  simp [F]
end ProofWiki116604CodexExpansion
