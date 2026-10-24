import Mathlib
namespace QEDReview32sol5
abbrev V := Fin 6
def graph : SimpleGraph V := SimpleGraph.fromEdgeSet {s(0,1),s(0,2),s(0,3),s(0,4),s(1,5)}
instance : DecidableRel graph.Adj := by unfold graph; infer_instance
lemma tree : graph.IsTree := by
  apply SimpleGraph.isTree_iff_connected_and_card.mpr
  refine ⟨by decide, ?_⟩
  rw [Nat.card_eq_fintype_card, ← SimpleGraph.edgeFinset_card, Nat.card_eq_fintype_card]
  decide
/-- The genuine connected component after deletion of r, represented by its reachable vertices.
Removing all incident edges leaves r isolated; requiring v≠r exactly removes that vertex. -/
def component (r s : V) : Finset V :=
  Finset.univ.filter (fun v => v ≠ r ∧ (graph.deleteIncidenceSet r).Reachable s v)
theorem refuted : graph.IsTree ∧
    component 1 0 = {0,2,3,4} ∧ component 0 1 = {1,5} ∧
    graph.Adj 1 0 ∧ 2 * (component 1 0).card > 6 ∧
    (component 0 1).card ≠ 6 - (component 1 0).card - 1 ∧
    ¬ (2 * (component 0 1).card < 6 - 2) := by
  refine ⟨tree, ?_⟩
  decide
end QEDReview32sol5
