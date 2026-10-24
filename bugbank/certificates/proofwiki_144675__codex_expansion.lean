import Mathlib
/-! Standard complete lattice Set Unit and bundled identity homomorphism. -/
namespace ProofWiki144675CodexExpansion
abbrev A := Set Unit

def idA : CompleteLatticeHom A A := CompleteLatticeHom.id A

def witnessX : Set A := {∅}

theorem refutes_literal_source_claim :
    idA (sSup (Set.univ : Set A)) = Set.univ ∧
    sSup (idA '' witnessX) = ∅ ∧
    idA (sSup (Set.univ : Set A)) ≠ sSup (idA '' witnessX) := by
  simp [idA, witnessX]

theorem identity_preserves_every_arbitrary_join (X : Set A) :
    idA (sSup X) = sSup (idA '' X) := by
  simp [idA]

theorem negative_control_top_singleton_satisfies_source_equality :
    idA (sSup (Set.univ : Set A)) = sSup (idA '' {Set.univ}) := by
  simp [idA]
end ProofWiki144675CodexExpansion
