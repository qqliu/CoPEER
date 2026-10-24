import Mathlib.Data.Real.Archimedean
import Mathlib.Tactic.NormNum
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.Ring
import Mathlib.Tactic.FieldSimp
import Mathlib.Tactic.FinCases
import Mathlib.Tactic.Tauto
import Mathlib.Tactic.IntervalCases

/- Human-guided audit: m=2,z=1,x=3/2 meets the floor decomposition, while floor(m+x)=3 rather than m. Uses actual Int.floor over ℝ.
   Original witness action: KEPT. -/
namespace Audit_reddit_learnmath_3jd8ci
theorem certificate : Int.floor (3/2 : ℝ) = 1 ∧
    ((2 + 1 : ℝ) ≤ 2+3/2 ∧ (2+3/2 : ℝ) < 2+1+1) ∧
    Int.floor (2+3/2 : ℝ) ≠ 2 := by norm_num
end Audit_reddit_learnmath_3jd8ci
