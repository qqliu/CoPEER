import Mathlib.Data.Real.Sqrt
import Mathlib.Analysis.SpecialFunctions.Pow.Real
import Mathlib.Tactic.NormNum
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.Ring
import Mathlib.Tactic.FinCases
import Mathlib.Tactic.Tauto

/- Human-review repair, 2026-09-15.
The source explicitly presents a false proof. This is the real-power/square-root step, not a newly discovered false theorem.
Historical source and human verdicts are preserved in the review packet. -/
namespace RedditLearnmathFuwmpf

theorem audited_counterexample :
    (-1 : ℝ) ^ ((2 : ℝ)/2) = -1 ∧
    Real.sqrt ((-1 : ℝ)^2) = 1 ∧
    (-1 : ℝ) ^ ((2 : ℝ)/2) ≠ Real.sqrt ((-1 : ℝ)^2) := by
  norm_num

end RedditLearnmathFuwmpf
