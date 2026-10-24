import Mathlib.Tactic.NormNum.BigOperators
import Mathlib.Order.Interval.Finset.Nat
import Mathlib.Algebra.BigOperators.Group.Finset.Basic
import Mathlib.Data.Rat.Defs
import Mathlib.Tactic.NormNum
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.Ring
import Mathlib.Tactic.FieldSimp
import Mathlib.Tactic.FinCases
import Mathlib.Tactic.Tauto
import Mathlib.Tactic.IntervalCases

/- Human-guided audit: n=2 satisfies n≥1, but the actual sum5 differs from proposed4. Uses Finset sums with actual rational division.
   Original witness action: KEPT. -/
namespace Audit_reddit_learnmath_fnlluu
open scoped BigOperators
theorem certificate : 1 ≤ (2 : ℕ) ∧
    (∑ k ∈ Finset.Icc (1 : ℕ) 2, (k : ℚ)^2) = 5 ∧
    (∑ k ∈ Finset.Icc (1 : ℕ) 2, (k : ℚ)^2) ≠ (2 : ℚ)*(2+1)*(2+2)/6 := by norm_num [show Finset.Icc (1 : ℕ) 2 = {1,2} by decide]
end Audit_reddit_learnmath_fnlluu
