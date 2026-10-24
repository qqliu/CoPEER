import Mathlib.Tactic.NormNum.NatFactorial
import Mathlib.Data.Nat.Factorial.Basic
import Mathlib.Data.Rat.Defs
import Mathlib.Tactic.NormNum
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.Ring
import Mathlib.Tactic.FieldSimp
import Mathlib.Tactic.FinCases
import Mathlib.Tactic.Tauto
import Mathlib.Tactic.IntervalCases

/- Human-guided audit: k=1 is allowed (take n=1), all denominators nonzero, and the alleged rearrangement reads5=7. Uses Nat.factorial and rational division.
   Original witness action: KEPT. -/
namespace Audit_reddit_learnmath_azugr0
theorem certificate : 1 ≤ (1 : ℕ) ∧
    ((1 : ℚ)^2+4*1+1+4)/(1+1) ≠ (Nat.factorial (1+2) : ℚ)/2+((1 : ℚ)^2+3*1)/1 := by norm_num
end Audit_reddit_learnmath_azugr0
