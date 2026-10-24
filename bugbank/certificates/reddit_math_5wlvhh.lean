import Mathlib.Tactic.NormNum
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.Ring
import Mathlib.Tactic.FieldSimp
import Mathlib.Tactic.FinCases
import Mathlib.Tactic.Tauto
import Mathlib.Tactic.IntervalCases

/- Human-guided audit: P={1,2},k=2 satisfies both stated premises, while P(3) fails. Source omits the induction-step premise; logical witness is unchanged.
   Original witness action: KEPT. -/
namespace Audit_reddit_math_5wlvhh
def P (n : ℕ) : Prop := n = 1 ∨ n = 2
theorem certificate : P 1 ∧ P 2 ∧ ¬ P (2+1) := by norm_num [P]
end Audit_reddit_math_5wlvhh
