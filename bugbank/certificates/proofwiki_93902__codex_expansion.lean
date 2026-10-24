import Mathlib
/-! On the one-point space, cl(univ)=univ while int(univ^c)=empty.
All topology and closure operations are Mathlib definitions. -/
namespace ProofWiki93902CodexExpansion

def H : Set Unit := Set.univ

theorem refutes_published_closure_interior_step :
    closure H = H ∧ interior Hᶜ = ∅ ∧
    closure H ≠ interior Hᶜ ∧ closure H = (interior Hᶜ)ᶜ := by
  simp [H]

theorem negative_control_empty_space_equality_holds :
    closure (Set.univ : Set Empty) = interior (Set.univ : Set Empty)ᶜ := by
  ext x
  exact nomatch x
end ProofWiki93902CodexExpansion
