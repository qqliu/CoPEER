import Mathlib

/- Human review: original witness, actual Mathlib graph semantics.
Historical custom graph enumerators remain in the frozen source packet. -/
set_option maxRecDepth 10000
set_option maxHeartbeats 4000000

namespace HumanReview_SE_math_2559073__q
def graph (n : ℕ) (es : List (ℕ × ℕ)) : SimpleGraph (Fin n) where
 Adj i j := i ≠ j ∧ ((i.val,j.val) ∈ es ∨ (j.val,i.val) ∈ es)
 symm := by intro i j h; exact ⟨h.1.symm,h.2.symm⟩
 loopless := ⟨fun _ h => h.1 rfl⟩
instance (n : ℕ) (es : List (ℕ × ℕ)) : DecidableRel (graph n es).Adj := fun _ _ => inferInstanceAs (Decidable (_ ∧ _))
namespace ArbitraryPath
def G := graph 4 [(0,2),(0,3),(1,2),(1,3)]
instance : DecidableRel G.Adj := inferInstanceAs (DecidableRel (graph _ _).Adj)
def p : G.Walk 0 1 := .cons (by decide : G.Adj 0 2) (.cons (by decide : G.Adj 2 1) .nil)
theorem witness : (∀ v : Fin 4, G.degree v = 2) ∧ p.IsPath ∧
    p.support = [0,2,1] ∧ (G.neighborFinset 0 ∩ {2,1}).card = 1 ∧
    ¬ 2 ≤ (G.neighborFinset 0 ∩ {2,1}).card := by
 refine ⟨by decide, ?_, by decide, by decide, by decide⟩
 rw [SimpleGraph.Walk.isPath_def]
 decide
end ArbitraryPath
end HumanReview_SE_math_2559073__q
