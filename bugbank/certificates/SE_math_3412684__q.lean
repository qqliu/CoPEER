import Mathlib

/- Human review: original witness, actual Mathlib graph semantics.
Historical custom graph enumerators remain in the frozen source packet. -/
set_option maxRecDepth 10000
set_option maxHeartbeats 4000000

namespace HumanReview_SE_math_3412684__q
def graph (n : ℕ) (es : List (ℕ × ℕ)) : SimpleGraph (Fin n) where
 Adj i j := i ≠ j ∧ ((i.val,j.val) ∈ es ∨ (j.val,i.val) ∈ es)
 symm := by intro i j h; exact ⟨h.1.symm,h.2.symm⟩
 loopless := ⟨fun _ h => h.1 rfl⟩
instance (n : ℕ) (es : List (ℕ × ℕ)) : DecidableRel (graph n es).Adj := fun _ _ => inferInstanceAs (Decidable (_ ∧ _))
namespace CommonNeighbor
def G := graph 6 [(0,3),(0,4),(1,3),(1,5),(2,4),(2,5),(3,4),(3,5),(4,5)]
instance : DecidableRel G.Adj := inferInstanceAs (DecidableRel (graph _ _).Adj)
theorem witness : (∀ v : Fin 6, G.degree v ≤ 4) ∧ G.degree 5 = 4 ∧
    (∀ u v : Fin 6, u ≠ v → ¬G.Adj u v → ∃ w, G.Adj u w ∧ G.Adj v w) ∧
    ¬G.Adj 0 5 ∧ (∀ v : Fin 6, v ≠ 0 → v ≠ 5 → G.Adj 5 v) ∧
    ¬(∃ w : Fin 6, G.Adj 0 w ∧ ∀ i : Fin 6,
      i ≠ 0 → i ≠ 5 → ¬G.Adj 0 i → G.Adj w i) := by decide
end CommonNeighbor
end HumanReview_SE_math_3412684__q
