import Mathlib.Tactic.NormNum
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.Ring
import Mathlib.Tactic.FieldSimp
import Mathlib.Tactic.FinCases
import Mathlib.Tactic.Tauto
import Mathlib.Tactic.IntervalCases

/- Human-guided audit: x=1 is natural even if naturals exclude0; the inequality is3<0. Uses ℤ arithmetic for the signed expression.
   Original witness action: KEPT. -/
namespace Audit_reddit_mathematics_14r91pk
theorem certificate : 0 < (1 : ℕ) ∧ ¬ ((1 : ℤ)+2 < -(1 : ℤ)^2+1^3) := by norm_num
end Audit_reddit_mathematics_14r91pk
