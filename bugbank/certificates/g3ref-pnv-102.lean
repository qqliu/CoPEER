import Mathlib

/-! The displayed identity fails at a=2, in its prime-divisibility context.
This concerns an intermediate identity, not the original number-theory theorem.
Primality and divisibility are Mathlib's standard predicates. -/
namespace G3refPnv102
def lhs (a : ℤ) : ℤ := 4 * a ^ 4 - 4 * a ^ 2 + 4
def rhs (a : ℤ) : ℤ := (2 * a - 1) ^ 2 + 3

theorem refutes_claimed_algebraic_identity_at_a_two :
    Nat.Prime 13 ∧ (13 : ℤ) ∣ ((2 : ℤ)^4 - 2^2 + 1) ∧
    lhs 2 = 52 ∧ rhs 2 = 12 ∧ (13 : ℤ) ∣ lhs 2 ∧
    ¬ (13 : ℤ) ∣ rhs 2 ∧ lhs 2 ≠ rhs 2 := by
  norm_num [lhs, rhs]

theorem corrected_identity (a : ℤ) :
    lhs a = (2 * a^2 - 1)^2 + 3 := by
  unfold lhs
  ring

theorem negative_control_identity_holds_at_a_one : lhs 1 = rhs 1 := by
  norm_num [lhs, rhs]
end G3refPnv102
