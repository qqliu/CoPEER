import Mathlib.Data.Real.Basic
import Mathlib.Tactic.NormNum
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.Ring
import Mathlib.Tactic.FinCases
import Mathlib.Tactic.Tauto

/- Human-review repair, 2026-09-15.
Dependency-consistent witness: c=0, δ=1, K=1, ε=2. K is evaluated from the exact source formula and the defining minimum is checked simultaneously.
Historical source and human verdicts are preserved in the review packet. -/
namespace RedditLearnmath1h7q3ju

theorem audited_counterexample :
    ∃ c δ K ε x : ℝ,
      c = 0 ∧ δ = 1 ∧ K = (δ + |c|)^2 + |c| *(δ + |c|) + |c|^2 ∧
      0 < δ ∧ 0 < K ∧ 0 < ε ∧ δ = min 1 (ε / K) ∧
      |x-c| < δ ∧ δ*K ≠ ε := by
  refine ⟨0, 1, 1, 2, 1/2, ?_⟩
  norm_num

end RedditLearnmath1h7q3ju
