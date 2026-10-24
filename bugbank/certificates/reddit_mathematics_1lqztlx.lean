import Mathlib.Order.Interval.Finset.Nat
import Mathlib.Data.Nat.Prime.Defs
import Mathlib.Data.Finset.Interval
import Mathlib.Tactic.NormNum
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.Ring
import Mathlib.Tactic.FieldSimp
import Mathlib.Tactic.FinCases
import Mathlib.Tactic.Tauto
import Mathlib.Tactic.IntervalCases

/- Human-guided audit: Same initial prime segment{2,3,5,7,11}: initial covered run2..12 has length11;114..126 has length13 and uncovered neighbors. Both runs lie below next prime13 squared. Uses Nat.Prime, divisibility and Finset intervals.
   Original witness action: KEPT. -/
namespace Audit_reddit_mathematics_1lqztlx
def S : Finset ℕ := {2,3,5,7,11}
def covered (n : ℕ) := ∃ p ∈ S, p ∣ n
instance (n : ℕ) : Decidable (covered n) := inferInstanceAs (Decidable (∃ p ∈ S, p ∣ n))
theorem certificate :
    (∀ p ∈ S, Nat.Prime p) ∧ (∀ p ∈ Finset.range 12, Nat.Prime p → p ∈ S) ∧
    (∀ n ∈ Finset.Icc 2 12, covered n) ∧ ¬ covered 13 ∧
    (∀ n ∈ Finset.Icc 114 126, covered n) ∧ ¬ covered 113 ∧ ¬ covered 127 ∧
    (Finset.Icc 2 12).card < (Finset.Icc 114 126).card := by decide
end Audit_reddit_mathematics_1lqztlx
