import Mathlib.Data.Real.Basic
import Mathlib.Tactic.NormNum
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.Ring
import Mathlib.Tactic.FinCases
import Mathlib.Tactic.Tauto

/- Human-review repair, 2026-09-15.
The theorem concerns the quoted local assertion; it does not refute the surrounding theorem.
Historical source and human verdicts are preserved in the review packet. -/
namespace RedditAskmath18tciae

theorem audited_counterexample :
    (0 : ℝ) < 1 ∧ (0 : ℝ) < 1 ∧ ¬ ∃ a : ℝ, 1 ≤ a ∧ a < 1 := by
  refine ⟨by norm_num, by norm_num, ?_⟩
  rintro ⟨a, ha, hb⟩
  linarith

end RedditAskmath18tciae
