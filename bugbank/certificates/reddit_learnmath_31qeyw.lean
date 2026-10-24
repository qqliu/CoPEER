import Mathlib.Data.Rat.Defs
import Mathlib.Tactic.NormNum
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.Ring
import Mathlib.Tactic.FieldSimp
import Mathlib.Tactic.FinCases
import Mathlib.Tactic.Tauto
import Mathlib.Tactic.IntervalCases

/- Human-guided audit: n=2 meets the positive-integer domain; 1/3=560/1680 exceeds the right side 533/1680. Uses actual rational division.
   Original witness action: KEPT. -/
namespace Audit_reddit_learnmath_31qeyw
theorem certificate : 0 < (2 : ℕ) ∧
    ¬ ((1 : ℚ)/(2*2-1) < 1/(8*2-6)+1/(8*2-4)+1/(8*2-2)+1/(8*2)) := by norm_num
end Audit_reddit_learnmath_31qeyw
