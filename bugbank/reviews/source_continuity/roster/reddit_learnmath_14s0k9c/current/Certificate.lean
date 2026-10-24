import Mathlib.GroupTheory.Perm.Cycle.Type
import Mathlib.Tactic.NormNum
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.Ring
import Mathlib.Tactic.FinCases
import Mathlib.Tactic.Tauto

/- Human-review repair, 2026-09-15.
Strengthened source-context witness in S4: x=(01)(23), y=(12) both have order 2 and do not commute, so their generated subgroup is nonabelian. Its inclusion in S4 is the required embedding, but x is not a single transposition. This replaces the old abelian C2 example.
Historical source and human verdicts are preserved in the review packet. -/
namespace RedditLearnmath14s0k9c

open Equiv

def x : Perm (Fin 4) := swap 0 1 * swap 2 3
def y : Perm (Fin 4) := swap 1 2

theorem audited_counterexample :
    orderOf x = 2 ∧ orderOf y = 2 ∧ x*y ≠ y*x ∧ ¬ x.IsSwap := by
  have hx : x^2 = 1 := by decide
  have hy : y^2 = 1 := by decide
  refine ⟨orderOf_eq_prime hx (by decide), orderOf_eq_prime hy (by decide), ?_, ?_⟩
  · decide
  · unfold Equiv.Perm.IsSwap
    decide

def generated : Subgroup (Perm (Fin 4)) := Subgroup.closure {x,y}

theorem generated_nonabelian :
    x ∈ generated ∧ y ∈ generated ∧ ¬ ∀ a b : generated, a*b=b*a := by
  have hx : x ∈ generated := Subgroup.subset_closure (by simp)
  have hy : y ∈ generated := Subgroup.subset_closure (by simp)
  refine ⟨hx,hy,?_⟩
  intro h
  have hb := congrArg Subtype.val (h ⟨x,hx⟩ ⟨y,hy⟩)
  exact audited_counterexample.2.2.1 hb
end RedditLearnmath14s0k9c
