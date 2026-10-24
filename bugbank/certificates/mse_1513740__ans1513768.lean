import Mathlib

/-! The source has a proved small base case.  Use k = 2, rather than k = 1:
the claimed new system contains two equations, and two is not strictly less
than two.  This refutes the printed strict size bound, not the possibility of
a repaired induction or the original theorem about differential operators. -/
namespace MSE1513740

def sizePhi (k : ℕ) : ℕ := k + 1
def sizePhiPrime : ℕ := 2

theorem certificate :
    1 < (2 : ℕ) ∧ sizePhi 2 = 3 ∧ sizePhiPrime = 2 ∧
      ¬ sizePhiPrime < 2 := by decide

theorem asserted_decrease_not_universal :
    ¬ ∀ k : ℕ, 1 < k → sizePhiPrime < k := by
  intro h
  exact (by decide : ¬ sizePhiPrime < 2) (h 2 (by decide))

/-- The printed inequality is valid only for k >= 3. -/
theorem asserted_holds_ge_three (k : ℕ) (h : 3 ≤ k) : sizePhiPrime < k := by
  unfold sizePhiPrime
  omega

/-- A comparison with k+1 is a different, valid bound for the k=2 witness. -/
theorem corrected_decrease_at_two : sizePhiPrime < sizePhi 2 := by decide
end MSE1513740
