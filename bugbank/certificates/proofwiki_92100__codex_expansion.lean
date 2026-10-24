import Mathlib
/-! Refutes the literal universal quantifier over integers using actual real
trigonometric functions at x=pi/2. The primitive itself is not challenged. -/
namespace ProofWiki92100CodexExpansion
noncomputable def x : ℝ := Real.pi / 2

def claimedInterval (n : ℤ) : Prop :=
  2 * Real.pi * n < x ∧ x < 2 * Real.pi * n + Real.pi

theorem tangent_premise_holds : Real.tan (x / 2) ≠ 0 := by
  have h : x / 2 = Real.pi / 4 := by unfold x; ring
  rw [h, Real.tan_pi_div_four]
  norm_num

theorem refutes_tangent_interval_inference :
    Real.tan (x / 2) ≠ 0 ∧ Real.sin x ≠ 0 ∧
    ¬ claimedInterval 1 ∧
    ¬ (Real.tan (x / 2) ≠ 0 → ∀ n : ℤ, claimedInterval n) := by
  have hf : ¬ claimedInterval 1 := by
    intro h
    have := h.1
    dsimp [x] at this
    norm_num at this
    linarith [Real.pi_pos]
  refine ⟨tangent_premise_holds, ?_, hf, ?_⟩
  · simp [x]
  · intro h
    exact hf (h tangent_premise_holds 1)

theorem negative_control_n_zero_interval_holds : claimedInterval 0 := by
  dsimp [claimedInterval, x]
  norm_num
  exact Real.pi_pos
end ProofWiki92100CodexExpansion
