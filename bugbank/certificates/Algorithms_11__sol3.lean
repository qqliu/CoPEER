import Mathlib

open scoped BigOperators

set_option linter.style.nameCheck false

namespace QEDReview11sol3



def conflict : SimpleGraph (Fin 6) where
  Adj u v := u ≠ v ∧ u.val / 3 = v.val / 3
  symm := by
    intro u v h
    exact ⟨Ne.symm h.1, h.2.symm⟩
  loopless := ⟨by intro u h; exact h.1 rfl⟩

instance : DecidableRel conflict.Adj := fun _ _ => inferInstanceAs
  (Decidable (_ ≠ _ ∧ _ = _))

def sourceGraph : SimpleGraph (Fin 2) := ⊥

/-- The source's k=3 total seats leave at most two seats for passengers. -/
theorem Algorithms_11__sol3_refuted :
    sourceGraph.Colorable 3 ∧
    ∀ load : Finset (Fin 6), load.card ≤ 3 - 1 →
      ¬ conflict.IsIndepSet (↑(Finset.univ \ load)) := by
  constructor
  · exact ⟨SimpleGraph.Coloring.mk (fun _ => (0 : Fin 3)) (by
      intro u v h
      exact False.elim h)⟩
  · decide


end QEDReview11sol3
