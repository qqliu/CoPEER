import Mathlib.Data.Int.Basic
import Mathlib.Tactic.NormNum
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.Ring
import Mathlib.Tactic.FieldSimp
import Mathlib.Tactic.FinCases
import Mathlib.Tactic.Tauto
import Mathlib.Tactic.IntervalCases

/- Human-guided audit: a=−1,b=1 satisfies both source sign assumptions but ab=−1; multiplying an inequality by a negative number reverses it.
   Original witness action: KEPT. -/
namespace Audit_reddit_learnmath_20itsx
theorem certificate : (-1 : ℤ) < 0 ∧ (0 : ℤ) < 1 ∧ ¬ (0 < (-1 : ℤ)*1) := by norm_num
end Audit_reddit_learnmath_20itsx
