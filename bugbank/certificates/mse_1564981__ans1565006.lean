import Mathlib.Tactic.NormNum

/-!
Source: https://math.stackexchange.com/a/1565006, lines 0011–0015.
The source multiplies only one side by 17^4 and then changes exponent 4m+4
into 4m+1. The same integer a=8352, m=1 refutes both literal steps.
Mathlib integer powers replace a fuel-bounded custom exponentiation program.
-/
namespace mse_1564981__ans1565006

theorem induction_step_refuted :
    (17 : ℤ) ^ (4 * 1) - 1 = 10 * 8352 ∧
    (17 : ℤ) ^ 4 * (17 ^ (4 * 1) - 1) ≠ 10 * 8352 ∧
    (17 : ℤ) ^ (4 * 1 + 1) - 83521 ≠ 10 * 8352 ∧
    (17 : ℤ) ^ (4 * 1 + 1) - 1 ≠ 10 * (8352 + 8352) := by norm_num

theorem corrected_multiplication :
    (17 : ℤ) ^ 4 * (17 ^ 4 - 1) = 10 * (83521 * 8352) := by norm_num

end mse_1564981__ans1565006
