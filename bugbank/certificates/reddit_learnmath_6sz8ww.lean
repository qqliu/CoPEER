import Mathlib.Tactic.NormNum.Parity
import Mathlib.Algebra.Polynomial.Degree.Definitions
import Mathlib.Algebra.Polynomial.Degree.Operations
import Mathlib.Algebra.Polynomial.Eval.Defs
import Mathlib.Algebra.Ring.Int.Parity
import Mathlib.Tactic.NormNum
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.Ring
import Mathlib.Tactic.FieldSimp
import Mathlib.Tactic.FinCases
import Mathlib.Tactic.Tauto
import Mathlib.Tactic.IntervalCases

/- Human-guided audit: p=2x+1 satisfies BOTH odd-value assumptions p(0)=1,p(1)=3. Its leading coefficient2 is even; its root−1/2 lacks integer parity. Uses Polynomial and Odd.
   Original witness action: KEPT. -/
namespace Audit_reddit_learnmath_6sz8ww
open Polynomial
noncomputable def p : Polynomial ℤ := C 2*X + C 1
theorem certificate : Odd (p.eval 0) ∧ Odd (p.eval 1) ∧
    p.natDegree = 1 ∧ p.leadingCoeff = 2 ∧ ¬ Odd p.leadingCoeff ∧
    (2 : ℚ)*(-1/2)+1 = 0 := by
  have hd : p.natDegree = 1 := by
    rw [p, Polynomial.natDegree_add_C, Polynomial.natDegree_C_mul_X 2 (by norm_num)]
  have hl : p.leadingCoeff = 2 := by
    rw [Polynomial.leadingCoeff, hd, p, Polynomial.coeff_add, Polynomial.coeff_C_mul_X, Polynomial.coeff_C]
    norm_num
  rw [hd, hl]
  norm_num [p]
end Audit_reddit_learnmath_6sz8ww
