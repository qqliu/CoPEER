import Mathlib.Data.Rat.Defs
import Mathlib.Tactic.NormNum
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.Ring
import Mathlib.Tactic.FinCases
import Mathlib.Tactic.Tauto

/- Audit 2026-09-15. Historical source packets and human judgments remain unchanged. -/
namespace RedditAskmath185kx7d

theorem audited_counterexample :
    ((1 : ℚ)*(1+1))/2 + (1+1) = 3 ∧
    ((1 : ℚ)*(1+1)+(1+1))/2 = 2 ∧
    ((1 : ℚ)*(1+1))/2 + (1+1) ≠ ((1 : ℚ)*(1+1)+(1+1))/2 := by
  norm_num

end RedditAskmath185kx7d
