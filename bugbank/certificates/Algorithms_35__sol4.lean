import Mathlib
namespace QEDReview35sol4
abbrev V := Fin 4
def graph : SimpleGraph V := SimpleGraph.fromEdgeSet {s(0,1),s(0,2),s(0,3),s(1,2)}
instance : DecidableRel graph.Adj := by unfold graph; infer_instance
def px : graph.Walk 3 1 := .cons (by decide : graph.Adj 3 0) (.cons (by decide : graph.Adj 0 1) .nil)
def py : graph.Walk 3 2 := .cons (by decide : graph.Adj 3 0) (.cons (by decide : graph.Adj 0 2) .nil)
def conflictEdge : graph.Walk 1 2 := .cons (by decide : graph.Adj 1 2) .nil
def closedWalk := (px.append conflictEdge).append py.reverse
def embed (v : Fin 3) : V := ⟨v.val, by omega⟩
lemma clique : ∀ a b : Fin 3, a ≠ b → graph.Adj (embed a) (embed b) := by decide
lemma non_bipartite : ¬ graph.Colorable 2 := by
  rintro ⟨C⟩
  have hi := C.injective_comp_of_pairwise_adj embed (by
    intro a b hab
    exact clique a b hab)
  have := Fintype.card_le_of_injective (C ∘ embed) hi
  norm_num at this
/-- The frozen BFS paths share vertex0; the resulting closed walk is not a cycle. -/
theorem refuted : graph.Connected ∧ ¬ graph.Colorable 2 ∧
    px.IsPath ∧ py.IsPath ∧ px.length = 2 ∧ py.length = 2 ∧
    ¬ graph.Adj 3 1 ∧ ¬ graph.Adj 3 2 ∧
    closedWalk.support = [3,0,1,2,0,3] ∧ ¬ closedWalk.IsCycle := by
  refine ⟨by decide, non_bipartite, ?_⟩
  simp [px, py, closedWalk, conflictEdge, SimpleGraph.Walk.isPath_def,
    SimpleGraph.Walk.isCycle_def, SimpleGraph.Walk.isTrail_def]
  decide
end QEDReview35sol4
