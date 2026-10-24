import Mathlib
/-! Original constant -1 sequence in actual 2-adic integers. Its first
canonical digit is its residue modulo2, represented in {0,1}; Mathlib's
toZMod_spec gives the reduction modulo the maximal ideal. -/
namespace ProofWiki98579CodexExpansion
instance : Fact (Nat.Prime 2) := ⟨by decide⟩
noncomputable def x (_ : ℕ) : ℤ_[2] := -1
noncomputable def firstDigit (z : ℤ_[2]) : ℕ := (PadicInt.toZMod z).val

theorem first_digit_minus_one : firstDigit (-1) = 1 := by
  simp [firstDigit]
  decide

def qualifying : Set ℕ := {n | ∃ b : ℕ, b ≤ 2-2 ∧ firstDigit (x n) = b}

theorem qualifying_empty : qualifying = ∅ := by
  ext n
  simp [qualifying, x, first_digit_minus_one]

theorem refutes_finite_set_has_maximum :
    (∀ n, firstDigit (x n) = 1) ∧ qualifying.Finite ∧
    ¬ ∃ N : ℕ, IsGreatest qualifying N := by
  refine ⟨fun _ => first_digit_minus_one, ?_, ?_⟩
  · rw [qualifying_empty]
    exact Set.finite_empty
  · rw [qualifying_empty]
    rintro ⟨N, h⟩
    exact h.1
end ProofWiki98579CodexExpansion
