import Mathlib.Order.Bounds.Defs
import Mathlib.Tactic.NormNum
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.Ring
import Mathlib.Tactic.FinCases
import Mathlib.Tactic.Tauto

/- Source-scope clarification, 2026-09-23.
The supplied source asks why its proof is wrong and concludes that 1 is the
largest natural number. The natural number 2 refutes that final conclusion.
This certificate proves that 1 is not greatest in the natural numbers; it
does not claim that 2 satisfies the inconsistent premise that a greatest
natural number exists, and it makes no claim about the author's intent. -/
namespace RedditLearnmathYa047e

theorem audited_counterexample :
    (2 : ℕ) ∈ Set.univ ∧ ¬ IsGreatest (Set.univ : Set ℕ) 1 := by
  refine ⟨Set.mem_univ _, ?_⟩
  intro h
  have := h.2 (Set.mem_univ 2)
  norm_num at this

end RedditLearnmathYa047e
