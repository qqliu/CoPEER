-- P15: kernel check of exactly the witness supplied by the critic's response:
--   "For n=2, x=1, and y=1, the left-hand side is 2 but the right-hand side evaluates to 3."
-- Line 25 reads: x + y = sum over i = 0 to 1 of (n choose i) * x^i * y^(n-i).
import Mathlib

namespace P15

-- right-hand side of line 25 at n = 2, x = 1, y = 1 (sum over i = 0,1)
theorem rhs_at_witness :
    (∑ i ∈ Finset.range 2, (Nat.choose 2 i : ℤ) * (1 : ℤ) ^ i * (1 : ℤ) ^ (2 - i)) = 3 := by
  decide

theorem line25_fails_at_witness :
    ((1 : ℤ) + 1) ≠ ∑ i ∈ Finset.range 2, (Nat.choose 2 i : ℤ) * (1 : ℤ) ^ i * (1 : ℤ) ^ (2 - i) := by
  decide

-- the induction hypothesis A(2) the source has in force at line 25 does hold at x = y = 1,
-- so the witness is not excluded by the assumption of line 19.
theorem A2_holds_at_witness :
    ((1 : ℤ) + 1) ^ 2 = ∑ i ∈ Finset.range 3, (Nat.choose 2 i : ℤ) * (1 : ℤ) ^ i * (1 : ℤ) ^ (2 - i) := by
  decide

end P15
