import Mathlib.Tactic.NormNum.Parity
import Mathlib.Algebra.Ring.Int.Parity
import Mathlib.Tactic.NormNum
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.Ring
import Mathlib.Tactic.FieldSimp
import Mathlib.Tactic.FinCases
import Mathlib.Tactic.Tauto
import Mathlib.Tactic.IntervalCases

/- Human-guided audit: The middle expression repeats k in place of j; k=0,j=1 gives 4≠2. The final even-sum theorem remains true; human reviewer explicitly identifies a typo. Uses Mathlib Odd.
   Original witness action: KEPT. -/
namespace Audit_reddit_learnmath_18emvdx
theorem certificate : Odd (1 : ℤ) ∧ Odd (3 : ℤ) ∧
    (1 : ℤ) = 2 * 0 + 1 ∧ (3 : ℤ) = 2 * 1 + 1 ∧
    (1 : ℤ) + 3 ≠ 2 * 0 + 2 * 0 + 2 := by norm_num
end Audit_reddit_learnmath_18emvdx
