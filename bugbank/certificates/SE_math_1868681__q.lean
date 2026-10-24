import Mathlib

/- Human review: original witness, actual Mathlib graph semantics.
Historical custom graph enumerators remain in the frozen source packet. -/
set_option maxRecDepth 10000
set_option maxHeartbeats 4000000

namespace HumanReview_SE_math_1868681__q
def graph (n : ℕ) (es : List (ℕ × ℕ)) : SimpleGraph (Fin n) where
 Adj i j := i ≠ j ∧ ((i.val,j.val) ∈ es ∨ (j.val,i.val) ∈ es)
 symm := by intro i j h; exact ⟨h.1.symm,h.2.symm⟩
 loopless := ⟨fun _ h => h.1 rfl⟩
instance (n : ℕ) (es : List (ℕ × ℕ)) : DecidableRel (graph n es).Adj := fun _ _ => inferInstanceAs (Decidable (_ ∧ _))
namespace TreeCount
def G := graph 3 [(0,1),(0,2),(1,2)]
def H := graph 3 [(0,1),(0,2)]
instance : DecidableRel G.Adj := inferInstanceAs (DecidableRel (graph _ _).Adj)
instance : DecidableRel H.Adj := inferInstanceAs (DecidableRel (graph _ _).Adj)
theorem htree : H.IsTree := by
 rw [SimpleGraph.isTree_iff_connected_and_card]
 constructor
 · decide
 · rw [Nat.card_eq_fintype_card, Nat.card_eq_fintype_card]
   decide
theorem witness : G.Connected ∧ H.IsTree ∧ H ≤ G ∧
    H.edgeFinset.card = 2 ∧ G.edgeFinset.card = 3 ∧
    ¬ H.edgeFinset.card = 1 := ⟨by decide, htree, (by exact (by decide : ∀ i j : Fin 3, H.Adj i j → G.Adj i j)), by decide, by decide, by decide⟩
end TreeCount
namespace OddBipartite
abbrev G := TreeCount.H
instance : DecidableRel G.Adj := inferInstanceAs (DecidableRel (graph _ _).Adj)
theorem witness : G.edgeFinset.card = 2 ∧
    (∀ i j : Fin 3, G.Adj i j → (i = 0) ≠ (j = 0)) ∧
    (G.edgeFinset.card : ℚ) ≠ (3:ℚ)^2/4 ∧
    (∀ m : ℕ, (m : ℚ) ≠ (3:ℚ)^2/4) := by
 refine ⟨by decide, by decide, ?_, ?_⟩
 · have hc : G.edgeFinset.card = 2 := by decide
   norm_num [hc]
 · intro m hm
   have h : (m : ℚ) * 4 = 9 := by linarith
   have hnat : m * 4 = 9 := by exact_mod_cast h
   omega
end OddBipartite
end HumanReview_SE_math_1868681__q
