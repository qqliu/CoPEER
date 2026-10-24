import Mathlib.Tactic.NormNum.Parity
import Mathlib.Algebra.Group.Nat.Even
import Mathlib.Tactic.NormNum
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.Ring
import Mathlib.Tactic.FieldSimp
import Mathlib.Tactic.FinCases
import Mathlib.Tactic.Tauto
import Mathlib.Tactic.IntervalCases

/- Human-guided audit: n=5 is odd and floor(n/2)=2 is even; the recursive expression is6, not7. Uses natural Euclidean division and standard parity.
   Original witness action: KEPT. -/
namespace Audit_reddit_learnmath_8yjpp7
theorem certificate : Odd (5 : ℕ) ∧ Even (5 / 2 : ℕ) ∧
    ((5 / 2 : ℕ)+1)*2 = 6 ∧ ((5 / 2 : ℕ)+1)*2 ≠ 5+2 := by norm_num
end Audit_reddit_learnmath_8yjpp7
