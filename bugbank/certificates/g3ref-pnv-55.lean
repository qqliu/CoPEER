import Mathlib

/-! This refutes the arithmetic inference from the Sylow congruence and
 divisibility conditions. It does not assert existence of a group with 105
 Sylow subgroups, or refute the original non-simplicity theorem. -/
namespace G3refPnv55
def n13 (k : ℕ) : ℕ := 1 + 13 * k

theorem refutes_only_possible_k_is_zero :
    Nat.Prime 13 ∧ n13 8 = 105 ∧ n13 8 ∣ 105 ∧ (8 : ℕ) ≠ 0 ∧
    ¬ (∀ k : ℕ, n13 k ∣ 105 → k = 0) := by
  refine ⟨by norm_num, by decide, by decide, by decide, ?_⟩
  intro h
  have := h 8 (by decide)
  omega

theorem negative_control_k_one_is_not_valid : ¬ n13 1 ∣ 105 := by decide
end G3refPnv55
