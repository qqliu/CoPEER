import Mathlib

/- Human review: original witness, actual Mathlib graph semantics.
Historical custom graph enumerators remain in the frozen source packet. -/
set_option maxRecDepth 10000
set_option maxHeartbeats 4000000

namespace HumanReview_SE_math_1968421__q
def graph (n : ℕ) (es : List (ℕ × ℕ)) : SimpleGraph (Fin n) where
 Adj i j := i ≠ j ∧ ((i.val,j.val) ∈ es ∨ (j.val,i.val) ∈ es)
 symm := by intro i j h; exact ⟨h.1.symm,h.2.symm⟩
 loopless := ⟨fun _ h => h.1 rfl⟩
instance (n : ℕ) (es : List (ℕ × ℕ)) : DecidableRel (graph n es).Adj := fun _ _ => inferInstanceAs (Decidable (_ ∧ _))
namespace DegreeDelete
def G := graph 7 [(0,1),(0,2),(1,4),(1,5),(2,3),(2,6),(3,6),(4,5)]
instance : DecidableRel G.Adj := inferInstanceAs (DecidableRel (graph _ _).Adj)
theorem witness : G.Connected ∧ G.degree 0 = 2 ∧
    (∀ v : Fin 7, 2 ≤ G.degree v) ∧
    ¬(G.induce {v | v ≠ 0}).Connected := by decide
end DegreeDelete
end HumanReview_SE_math_1968421__q
