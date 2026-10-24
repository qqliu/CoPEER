import Mathlib
/-! The original free one-element matroid rank witness. On its finite
powerset the rank is cardinality, using Mathlib's Finset operations. -/
namespace ProofWiki132447
abbrev S := Fin 1
def rho (A : Finset S) : ℤ := A.card

theorem rank_axioms :
    (∀ A : Finset S, 0 ≤ rho A ∧ rho A ≤ (A.card : ℤ)) ∧
    (∀ A B : Finset S, A ⊆ B → rho A ≤ rho B) ∧
    (∀ A B : Finset S, rho (A ∪ B) + rho (A ∩ B) ≤ rho A + rho B) := by
  decide

theorem refutes_printed_rank_submodularity_step :
    (0 : S) ∉ (∅ : Finset S) ∧
    rho (∅ ∪ {0}) = 1 ∧ rho ∅ = 0 ∧ rho {0} = 1 ∧
    ¬ (rho (∅ ∪ {0}) ≤ rho ∅ + rho {0} - rho (∅ ∪ {0})) := by
  decide
end ProofWiki132447
