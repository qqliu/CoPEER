import Mathlib
/-! Failure of the substitution x=|a|sec(theta) at a=0,x=1.
Real division in Lean is total, so the certificate uses the necessary reverse
equation; it does not falsely assert that Lean's 1/0 is undefined. -/
namespace ProofWiki13793CodexExpansion

def sourceBranch (a x : ℝ) : Prop := |a| < x
def substitution (a x : ℝ) : Prop :=
  ∃ θ : ℝ, Real.cos θ ≠ 0 ∧ x = |a| * (Real.cos θ)⁻¹

theorem refutes_substitution_without_nonzero :
    sourceBranch 0 1 ∧ ¬ substitution 0 1 ∧
    ¬ (∀ a x : ℝ, sourceBranch a x → substitution a x) := by
  have hn : ¬ substitution 0 1 := by simp [substitution]
  have hb : sourceBranch 0 1 := by norm_num [sourceBranch]
  exact ⟨hb, hn, fun h => hn (h 0 1 hb)⟩

theorem negative_control_nonzero_parameter : substitution 1 1 := by
  refine ⟨0, ?_, ?_⟩ <;> norm_num
end ProofWiki13793CodexExpansion
