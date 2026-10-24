import Mathlib
/-! Actual Mathlib order ideals and filters in the two-element Boolean lattice.
The scope is the standalone lemma's printed hypotheses; omitted parent-page
assumptions are not asserted to hold. -/
namespace ProofWiki105639
open Order

def F : PFilter Bool := PFilter.principal true
def M : Order.Ideal Bool := Order.Ideal.principal false

theorem disjoint_M_F : Disjoint (M : Set Bool) (F : Set Bool) := by
  rw [Set.disjoint_left]
  intro x hx hF
  cases x
  · exact (by decide : ¬ ((true : Bool) ≤ false)) hF
  · exact (by decide : ¬ ((true : Bool) ≤ false)) hx

theorem maximal_disjoint :
    ∀ I : Order.Ideal Bool, Disjoint (I : Set Bool) (F : Set Bool) → M ≤ I → I ≤ M := by
  intro I hd _ x hx
  cases x
  · simp [M]
  · exact False.elim (Set.disjoint_left.mp hd hx (by simp [F]))

def N (a : Bool) : Set Bool := {x | ∃ m ∈ M, x ≤ m ⊔ a}

theorem N_false : N false = (M : Set Bool) := by
  ext x
  cases x <;> simp [N, M]

theorem refutes_unqualified_a_and_strictness_claims :
    Disjoint (M : Set Bool) (F : Set Bool) ∧
    (∀ I : Order.Ideal Bool, Disjoint (I : Set Bool) (F : Set Bool) → M ≤ I → I ≤ M) ∧
    false ∈ M ∧ N false = (M : Set Bool) ∧ ¬ ((M : Set Bool) ⊂ N false) := by
  refine ⟨disjoint_M_F, maximal_disjoint, by simp [M], N_false, ?_⟩
  rw [N_false]
  exact lt_irrefl _

theorem negative_control_a_not_in_M : true ∉ M ∧ (M : Set Bool) ⊂ N true := by
  constructor
  · simp [M]
  · refine ⟨?_, ?_⟩
    · intro x hx
      exact ⟨x, hx, by simp⟩
    · intro h
      have := h (show true ∈ N true from ⟨false, by simp [M], by simp⟩)
      exact (by decide : ¬ ((true : Bool) ≤ false)) this

end ProofWiki105639
