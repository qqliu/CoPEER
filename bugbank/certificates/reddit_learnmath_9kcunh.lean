import Mathlib.Tactic.NormNum.RealSqrt
import Mathlib.Data.Real.Sqrt
import Mathlib.Tactic.NormNum
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.Ring
import Mathlib.Tactic.FieldSimp
import Mathlib.Tactic.FinCases
import Mathlib.Tactic.Tauto
import Mathlib.Tactic.IntervalCases

/- Human-guided audit: Unchanged n=4 satisfies the surrounding choice ε=2/5,N=3, including N least integer≥1/ε and1/N<ε. Thus conditional and isolated readings both fail. Uses actual Real.sqrt and ℝ division; resolves reviewer concern about omitted epsilon context.
   Original witness action: KEPT. -/
namespace Audit_reddit_learnmath_9kcunh
theorem certificate : (0 : ℝ) < 2/5 ∧ (1/3 : ℝ) < 2/5 ∧
    (1/(2/5) : ℝ) ≤ 3 ∧ (∀ m : ℕ, m < 3 → (m : ℝ) < 1/(2/5)) ∧
    3 ≤ (4 : ℕ) ∧ ¬ ((4 : ℝ)/(Real.sqrt 4+2) < 1/4) := by
  norm_num
  intro m hm; interval_cases m <;> norm_num
end Audit_reddit_learnmath_9kcunh
