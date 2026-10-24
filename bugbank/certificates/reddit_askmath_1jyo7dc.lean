import Mathlib.Data.Rat.Defs
import Mathlib.Algebra.BigOperators.Group.List.Basic
import Mathlib.Tactic.NormNum
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.Ring
import Mathlib.Tactic.FinCases
import Mathlib.Tactic.Tauto

/- Human-review repair, 2026-09-15.
500 ratings all equal to 1 meet the 1-to-5 scale and average 500/500=9/9. This refutes the denominator-based fraction-equality claim only; decimal strings also have the usual 0.999... ambiguity.
Historical source and human verdicts are preserved in the review packet. -/
namespace RedditAskmath1jyo7dc

def ratings : List ℚ := List.replicate 500 1

theorem audited_counterexample :
    ratings.length = 500 ∧ (∀ x ∈ ratings, (1 : ℚ) ≤ x ∧ x ≤ 5) ∧
    ratings.sum = 500 ∧ ratings.sum / 500 = (9/9 : ℚ) := by
  norm_num [ratings]

end RedditAskmath1jyo7dc
