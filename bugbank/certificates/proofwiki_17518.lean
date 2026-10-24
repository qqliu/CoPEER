import Mathlib
/-! The actual additive group ZMod 2 is a left quasigroup. The printed
membership antecedents do not impose equal images. -/
namespace ProofWiki17518
abbrev S := ZMod 2

def Lambda (a x y : S) : Prop := y = a + x

theorem parastrophe_hypothesis (a x b : S) : a + x = b ↔ -a + b = x := by
  constructor
  · intro h
    rw [← h]
    abel
  · intro h
    rw [← h]
    abel

theorem refutes_literal_displayed_injectivity :
    Lambda 0 0 (0 + 0) ∧ Lambda 0 1 (0 + 1) ∧
    (0 : S) ≠ 1 ∧
    ¬ (∀ a x₁ x₂ : S, Lambda a x₁ (a + x₁) ∧ Lambda a x₂ (a + x₂) → x₁ = x₂) := by
  refine ⟨rfl, rfl, by decide, ?_⟩
  intro h
  exact (by decide : (0 : S) ≠ 1) (h 0 0 1 ⟨rfl, rfl⟩)

theorem corrected_common_second_coordinate (a x₁ x₂ y : S)
    (h₁ : Lambda a x₁ y) (h₂ : Lambda a x₂ y) : x₁ = x₂ := by
  exact add_left_cancel (h₁.symm.trans h₂)
end ProofWiki17518
