import Mathlib.Data.ZMod.Basic
import Mathlib.Algebra.Polynomial.Degree.Operations
import Mathlib.Algebra.Polynomial.Eval.Defs
import Mathlib.Tactic.NormNum
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.Ring
import Mathlib.Tactic.FinCases
import Mathlib.Tactic.Tauto

/- Human-review repair, 2026-09-15.
Typographical constant-coefficient error: f=X²+1 and g=X²+2 over the original field ZMod 3 have leading coefficient 1, but the remainder is -1, not the displayed a0-a0=0.
Historical source and human verdicts are preserved in the review packet. -/
namespace RedditAskmath12t7sri

open Polynomial
noncomputable def f : Polynomial (ZMod 3) := X^2 + C 1
noncomputable def g : Polynomial (ZMod 3) := X^2 + C 2

theorem audited_counterexample :
    f.natDegree = 2 ∧ g.natDegree = 2 ∧
    f.leadingCoeff = 1 ∧ g.leadingCoeff = 1 ∧
    f - g = C (-1) ∧ f ≠ g + 0 := by
  refine ⟨natDegree_X_pow_add_C, natDegree_X_pow_add_C, ?_, ?_, ?_, ?_⟩
  · exact leadingCoeff_X_pow_add_C (by decide : 0 < 2)
  · exact leadingCoeff_X_pow_add_C (by decide : 0 < 2)
  · simp only [f,g,add_sub_add_left_eq_sub,← map_sub]
    norm_num
  · intro h
    have := congrArg (eval 0) h
    norm_num [f,g] at this
    exact (by decide : (1 : ZMod 3) ≠ 2) this
end RedditAskmath12t7sri
