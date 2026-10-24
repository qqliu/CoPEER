import Mathlib

/-! This refutes only the explicitly printed general four-positive-variable lemma.
The original power-allocation problem separately asserts positivity of its
objective denominator. Therefore these negative-denominator examples do not
refute the proposed optimum or a use of the corrected positive-denominator lemma. -/
namespace MSE4671334

def Claim : Prop := ∀ a b c d : ℝ,
  0 < a → 0 < b → 0 < c → 0 < d → c ≠ d →
  ((a-b)/(c-d) ≤ a/c ↔ b/d ≥ a/c)

theorem forward_witness :
    (0 : ℝ) < 1 ∧ (0 : ℝ) < 3 ∧ (0 : ℝ) < 2 ∧
      (1 : ℝ) - 2 ≠ 0 ∧ (3 : ℝ)/2 ≥ 1/1 ∧
      ¬ ((1 : ℝ)-3)/(1-2) ≤ 1/1 := by norm_num

theorem reverse_witness :
    ((1 : ℝ)-1)/(1-2) ≤ 1/1 ∧ ¬ (1 : ℝ)/2 ≥ 1/1 := by norm_num

theorem claim_fails : ¬ Claim := by
  intro h
  have h' := h 1 3 1 2 (by norm_num) (by norm_num)
    (by norm_num) (by norm_num) (by norm_num)
  norm_num at h'
end MSE4671334
