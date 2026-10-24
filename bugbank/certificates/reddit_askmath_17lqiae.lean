import Mathlib.Algebra.MvPolynomial.CommRing
import Mathlib.Tactic.NormNum
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.Ring
import Mathlib.Tactic.FinCases
import Mathlib.Tactic.Tauto

/- Human-review repair, 2026-09-15.
Literal typographical claim that odd powers contain (xy)^n: at n=1 the coefficient of xy in x+y is zero. This does not challenge the symmetric-polynomial theorem.
Historical source and human verdicts are preserved in the review packet. -/
namespace RedditAskmath17lqiae

open MvPolynomial
noncomputable def exponent : Fin 2 →₀ ℕ := Finsupp.single 0 1 + Finsupp.single 1 1

theorem audited_counterexample :
    Odd (1 : ℕ) ∧
    coeff exponent (((X (0 : Fin 2) + X 1) : MvPolynomial (Fin 2) ℤ)^1) = 0 := by
  have h0 : exponent ≠ Finsupp.single 0 1 := by
    intro h
    have := congrArg (fun f : Fin 2 →₀ ℕ => f 1) h
    norm_num [exponent] at this
  have h1 : exponent ≠ Finsupp.single 1 1 := by
    intro h
    have := congrArg (fun f : Fin 2 →₀ ℕ => f 0) h
    norm_num [exponent] at this
  refine ⟨⟨0, by norm_num⟩, ?_⟩
  simp [coeff_X',h0,h1,h0.symm,h1.symm]
end RedditAskmath17lqiae
