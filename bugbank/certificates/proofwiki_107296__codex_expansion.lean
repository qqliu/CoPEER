import Mathlib
/-! Actual ordinals: the supremum (union) of the singleton index {0} is 0.
The claimed embedding does not land there; the successor union repairs it. -/
namespace ProofWiki107296CodexExpansion

noncomputable def idx (_ : Unit) : Ordinal := 0
noncomputable def beta : Ordinal := ⨆ x : Unit, idx x
noncomputable def betaPlus : Ordinal := ⨆ x : Unit, Order.succ (idx x)

theorem refutes_source_embedding_into_union_of_indices :
    Function.Injective idx ∧ beta = 0 ∧
    ¬ (∀ x : Unit, idx x < beta) := by
  refine ⟨fun x y _ => Subsingleton.elim x y, ?_, ?_⟩
  · simp [beta, idx]
  · intro h
    simpa [idx, beta] using h ()

theorem negative_control_successor_union_repairs_embedding :
    ∀ x : Unit, idx x < betaPlus := by
  intro x
  simp [idx, betaPlus]
end ProofWiki107296CodexExpansion
