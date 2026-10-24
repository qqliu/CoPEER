import Mathlib.Algebra.Polynomial.Basic
import Mathlib.Algebra.Polynomial.Eval.Defs
import Mathlib.Tactic.Ring

/-!
Source: https://math.stackexchange.com/a/5127254 (line 0005).
The lemma claims pointwise divisibility over all naturals implies a constant
integer polynomial quotient, without a degree hypothesis. We use its stored
primary witness f = X^2 - 1, g = X + 1, and prove the premise for every n,
not a finite sweep. Mathlib Polynomial replaces coefficient-list arithmetic.
This refutes the lemma as stated; its equal-degree use site is a separate claim.
-/
namespace mse_1892923__ans5127254
open Polynomial

noncomputable def f : Polynomial ℤ := X ^ 2 - 1
noncomputable def g : Polynomial ℤ := X + 1

theorem pointwise_divisibility (n : ℕ) : g.eval (n : ℤ) ∣ f.eval (n : ℤ) := by
  refine ⟨(n : ℤ) - 1, ?_⟩
  simp only [f, g, eval_sub, eval_pow, eval_X, eval_one, eval_add]
  ring

theorem no_constant_quotient : ¬ ∃ r : ℤ, f = C r * g := by
  rintro ⟨r, h⟩
  have h0 := congrArg (fun p : Polynomial ℤ => p.eval 0) h
  have h1 := congrArg (fun p : Polynomial ℤ => p.eval 1) h
  simp [f, g] at h0 h1
  omega

theorem lemma_is_false :
    (∀ n : ℕ, g.eval (n : ℤ) ∣ f.eval (n : ℤ)) ∧
    ¬ ∃ r : ℤ, f = C r * g :=
  ⟨pointwise_divisibility, no_constant_quotient⟩

end mse_1892923__ans5127254
