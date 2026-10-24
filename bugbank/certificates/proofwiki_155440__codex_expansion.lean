import Mathlib
/-! The identity FrameHom on the complete Boolean algebra Set Unit preserves
arbitrary joins. It does not interchange joins and meets. -/
namespace ProofWiki155440CodexExpansion
abbrev A := Set Unit

def phi : FrameHom A A := FrameHom.id A
def witnessA : Set A := {∅, Set.univ}

theorem refutes_published_meet_for_arbitrary_join :
    Set.range phi = Set.univ ∧
    phi (sSup witnessA) = Set.univ ∧ sInf (phi '' witnessA) = ∅ ∧
    phi (sSup witnessA) ≠ sInf (phi '' witnessA) := by
  simp [phi, witnessA]

theorem correctedJoinLaw (s : Set A) : phi (sSup s) = sSup (phi '' s) := by
  simp [phi]

theorem negative_control_singleton_top :
    phi (sSup {Set.univ}) = sInf (phi '' {Set.univ}) := by
  simp [phi]
end ProofWiki155440CodexExpansion
