import Mathlib

/-! Standard binomial coefficients replace the bounded Pascal lookup table.
F is defined at every natural index by the source's recurrence and initial data.
The primary discrepancy is (0,1); (1,1) independently gives an interior failure. -/
namespace QEDCert.mse_206158__ans271036

def F : ℕ → ℕ → ℕ
  | _, 0 => 1
  | 0, _ + 1 => 0
  | n + 1, m + 1 => F n (m + 1) + F (n + 1) m
termination_by n m => n + m

theorem source_boundary : (∀ n, F n 0 = 1) ∧ (∀ m, F 0 (m+1) = 0) := by
  constructor <;> intro n <;> simp [F]

theorem source_recurrence (n m : ℕ) :
    F (n+1) (m+1) = F n (m+1) + F (n+1) m := by rw [F]

theorem whole_boundary_line_clashes (m : ℕ) :
    F 0 (m+1) ≠ (0+(m+1)).choose 0 := by simp [F]

theorem certificate :
    F 0 1 = 0 ∧ Nat.choose (0+1) 0 = 1 ∧
    F 0 1 ≠ Nat.choose (0+1) 0 ∧
    F 1 1 = 1 ∧ Nat.choose (1+1) 1 = 2 ∧
    F 1 1 ≠ Nat.choose (1+1) 1 := by norm_num [F, Nat.choose]

theorem claim_fails : ¬ ∀ n m, F n m = (n+m).choose n := by
  intro h
  exact whole_boundary_line_clashes 0 (h 0 1)
end QEDCert.mse_206158__ans271036
