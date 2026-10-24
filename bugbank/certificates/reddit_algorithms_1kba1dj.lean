import Mathlib.Order.Bounds.Defs
import Mathlib.Data.Real.Basic
import Mathlib.Tactic.NormNum
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.Ring
import Mathlib.Tactic.FinCases
import Mathlib.Tactic.Tauto

/- Human-review repair, 2026-09-15.
One-period counterexample with demand 1, initial stock 0, capacity 1, final stock 1, price 1. Real nonnegative production is allowed. The actual balance requires production/cost 2; the reversed recurrence admits production/cost 0.
Historical source and human verdicts are preserved in the review packet. -/
namespace RedditAlgorithms1kba1dj

theorem audited_counterexample :
    (0 : ℝ) - 1 + 2 = 1 ∧ (0 : ℝ) - 1 + 0 ≠ 1 ∧
    (1 : ℝ) + 0 - 1 = 0 ∧
    IsLeast {cost : ℝ | ∃ x : ℝ, 0 ≤ x ∧ 0 - 1 + x = 1 ∧ cost = 1*x} 2 ∧
    IsLeast {cost : ℝ | ∃ x : ℝ, 0 ≤ x ∧ 1 + x - 1 = 0 ∧ cost = 1*x} 0 := by
  refine ⟨by norm_num, by norm_num, by norm_num, ?_, ?_⟩
  · constructor
    · exact ⟨2, by norm_num, by norm_num, by norm_num⟩
    · rintro cost ⟨x, hx, hb, rfl⟩
      linarith
  · constructor
    · exact ⟨0, by norm_num, by norm_num, by norm_num⟩
    · rintro cost ⟨x, hx, hb, rfl⟩
      linarith

end RedditAlgorithms1kba1dj
