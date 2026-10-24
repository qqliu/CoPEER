import Mathlib
/-! Mathlib irreducibility on a singleton. No two proper subsets can cover
this closed irreducible set, irrespective of their closedness. -/
namespace ProofWiki131075CodexExpansion

def F : Set Unit := {()}

theorem refutes_irreducible_proper_closed_cover_step :
    IsClosed F ∧ IsIrreducible F ∧
    ¬ (∃ A B : Set Unit, IsClosed A ∧ IsClosed B ∧ A ⊂ F ∧ B ⊂ F ∧ F = A ∪ B) := by
  refine ⟨isClosed_singleton, isIrreducible_singleton, ?_⟩
  rintro ⟨A,B,_,_,ha,hb,heq⟩
  have hA : () ∉ A := by
    intro hx
    exact ha.2 (fun x _ => by cases x; exact hx)
  have hB : () ∉ B := by
    intro hx
    exact hb.2 (fun x _ => by cases x; exact hx)
  have hmem : () ∈ A ∪ B := by rw [← heq]; simp [F]
  exact hmem.elim hA hB
end ProofWiki131075CodexExpansion
