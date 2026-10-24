import Mathlib
namespace QEDReview36sol5
abbrev V := Fin 4
def firstTree : SimpleGraph V := SimpleGraph.fromEdgeSet {s(0,1),s(0,2),s(0,3)}
instance : DecidableRel firstTree.Adj := by unfold firstTree; infer_instance
def secondTree : SimpleGraph V := SimpleGraph.fromEdgeSet {s(0,1),s(1,2),s(2,3)}
instance : DecidableRel secondTree.Adj := by unfold secondTree; infer_instance
def e : Sym2 V := s(0,2)
def f : Sym2 V := s(2,3)
def firstSwap : SimpleGraph V := firstTree.deleteEdges {e} ⊔ SimpleGraph.fromEdgeSet {f}
def secondSwap : SimpleGraph V := secondTree.deleteEdges {f} ⊔ SimpleGraph.fromEdgeSet {e}
instance : DecidableRel firstSwap.Adj := by unfold firstSwap; infer_instance
instance : DecidableRel secondSwap.Adj := by unfold secondSwap; infer_instance
lemma tree1 : firstTree.IsTree := by
  apply SimpleGraph.isTree_iff_connected_and_card.mpr
  refine ⟨by decide, ?_⟩
  rw [Nat.card_eq_fintype_card, ← SimpleGraph.edgeFinset_card, Nat.card_eq_fintype_card]
  decide
lemma tree2 : secondTree.IsTree := by
  apply SimpleGraph.isTree_iff_connected_and_card.mpr
  refine ⟨by decide, ?_⟩
  rw [Nat.card_eq_fintype_card, ← SimpleGraph.edgeFinset_card, Nat.card_eq_fintype_card]
  decide
/-- The proposed f crosses the e-cut of T₁, but replacing it in T₂ disconnects T₂. -/
theorem refuted : firstTree.IsTree ∧ secondTree.IsTree ∧
    e ∈ firstTree.edgeFinset ∧ f ∈ secondTree.edgeFinset ∧
    (∀ v : V, (firstTree.deleteEdges {e}).Reachable 0 v ↔ v ≠ 2) ∧
    firstSwap.Connected ∧ ¬ secondSwap.Connected ∧ ¬ secondSwap.IsTree := by
  have hc : ¬ secondSwap.Connected := by decide
  exact ⟨tree1, tree2, by decide, by decide, by decide, by decide, hc,
    fun h => hc h.connected⟩
end QEDReview36sol5
