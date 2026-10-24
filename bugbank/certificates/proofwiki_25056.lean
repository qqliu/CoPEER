import Mathlib
/-! Keep the original polynomial witness: a=-1,b=n=2,q=-1/2,f=X+1.
Here g=n*f is the integral polynomial 2X+2; b*n*q*f=-g.
Mathlib's normalized polynomial content evaluates to +2, not -2. -/
namespace ProofWiki25056
open Polynomial
noncomputable def f : ℤ[X] := X + 1
noncomputable def g : ℤ[X] := C 2 * f

theorem f_content : f.content = 1 := by
  apply IsPrimitive.content_eq_one
  exact (monic_X_add_C (1 : ℤ)).isPrimitive

theorem g_content : g.content = 2 := by
  rw [g, content_C_mul, f_content]
  norm_num [← Int.abs_eq_normalize]

theorem refutes_unsigned_scalar_pull_out :
    (-1 : ℚ) / 2 = -1/2 ∧ (2:ℚ)*2*(-1/2) = -2 ∧
    g.content = 2 ∧ (-g).content = 2 ∧
    (-g).content ≠ (-1:ℤ) * g.content := by
  have hn : (-g).content = 2 := by
    have hneg : -g = C (-1 : ℤ) * g := by simp
    rw [hneg, content_C_mul, g_content]
    norm_num [← Int.abs_eq_normalize]
  norm_num [g_content, hn]
end ProofWiki25056
