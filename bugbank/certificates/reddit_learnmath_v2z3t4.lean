import Mathlib.Tactic.NormNum
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.Ring
import Mathlib.Tactic.FieldSimp
import Mathlib.Tactic.FinCases
import Mathlib.Tactic.Tauto
import Mathlib.Tactic.IntervalCases

/- Human-guided audit: Keeps n=4,d=2 and the stated subtract-one recursion. It returns3, violating qd≤n. The algorithm itself is source-specific and retained; arithmetic uses Nat.
   Original witness action: KEPT. -/
namespace Audit_reddit_learnmath_v2z3t4
def alg : ℕ → ℕ → ℕ
  | 0, _ => 0
  | n+1, d => if n+1 < d then 0 else 1+alg n d
theorem certificate : (0 : ℕ) < 2 ∧ alg 4 2 = 3 ∧ ¬ (alg 4 2*2 ≤ 4 ∧ 4 < (alg 4 2+1)*2) := by decide
end Audit_reddit_learnmath_v2z3t4
