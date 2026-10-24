import Mathlib
namespace QEDReview40sol5
/-- Internal vertices0,1,2,3 carry the original labels4,5,6,7. -/
abbrev V := Fin 4
def originalLabel (v : V) : ℕ := v.val + 4
def graph : SimpleGraph V := SimpleGraph.fromEdgeSet {s(0,1),s(1,2),s(2,3)}
instance : DecidableRel graph.Adj := by unfold graph; infer_instance
def M1 : graph.Subgraph where
  verts := Set.univ
  Adj u v := (u=0 ∧ v=1) ∨ (u=1 ∧ v=0) ∨ (u=2 ∧ v=3) ∨ (u=3 ∧ v=2)
  adj_sub := by intro u v h; rcases h with ⟨rfl,rfl⟩ | ⟨rfl,rfl⟩ | ⟨rfl,rfl⟩ | ⟨rfl,rfl⟩ <;> decide
  edge_vert := by simp
  symm := by intros u v h; tauto
def M2 : graph.Subgraph where
  verts := {1,2}
  Adj u v := (u=1 ∧ v=2) ∨ (u=2 ∧ v=1)
  adj_sub := by intro u v h; rcases h with ⟨rfl,rfl⟩ | ⟨rfl,rfl⟩ <;> decide
  edge_vert := by intro u v h; rcases h with ⟨rfl,rfl⟩ | ⟨rfl,rfl⟩ <;> simp
  symm := by intros u v h; tauto
instance : DecidableRel M1.Adj := fun _ _ => inferInstanceAs (Decidable (_ ∨ _ ∨ _ ∨ _))
instance : DecidableRel M2.Adj := fun _ _ => inferInstanceAs (Decidable (_ ∨ _))
instance : DecidablePred (fun v => v ∈ M1.verts) := fun _ => inferInstanceAs (Decidable True)
instance : DecidablePred (fun v => v ∈ M2.verts) := fun v => inferInstanceAs (Decidable (v = 1 ∨ v = 2))
instance : DecidableRel M1.spanningCoe.Adj := inferInstanceAs (DecidableRel M1.Adj)
instance : DecidableRel M2.spanningCoe.Adj := inferInstanceAs (DecidableRel M2.Adj)
def path : graph.Walk 0 3 := .cons (by decide : graph.Adj 0 1) (.cons (by decide : graph.Adj 1 2) (.cons (by decide : graph.Adj 2 3) .nil))
/-- A maximal matching cannot add an edge: every ambient edge touches a matched vertex. -/
def NoAddableEdge (M : graph.Subgraph) := ∀ u v, graph.Adj u v → u ∈ M.verts ∨ v ∈ M.verts
lemma matching1 : M1.IsMatching := by
  change ∀ v : V, v ∈ M1.verts → ∃! w, M1.Adj v w
  unfold ExistsUnique
  decide
lemma matching2 : M2.IsMatching := by
  change ∀ v : V, v ∈ M2.verts → ∃! w, M2.Adj v w
  unfold ExistsUnique
  decide
/-- The frozen P₄ has a single alternating path carrying two M₁ edges but only one M₂ edge. -/
theorem refuted : M1.IsMatching ∧ M2.IsMatching ∧
    NoAddableEdge M1 ∧ NoAddableEdge M2 ∧
    M1.spanningCoe.edgeFinset = {s(0,1),s(2,3)} ∧
    M2.spanningCoe.edgeFinset = {s(1,2)} ∧
    Disjoint M1.spanningCoe.edgeFinset M2.spanningCoe.edgeFinset ∧
    path.IsPath ∧ path.edges = [s(0,1),s(1,2),s(2,3)] ∧
    (M1.spanningCoe.edgeFinset \ M2.spanningCoe.edgeFinset).card >
      M2.spanningCoe.edgeFinset.card := by
  refine ⟨matching1, matching2, ?_, ?_, ?_, ?_, ?_, ?_, ?_, ?_⟩
  · unfold NoAddableEdge; decide
  · unfold NoAddableEdge; decide
  · decide
  · decide
  · decide
  · simp [path, SimpleGraph.Walk.isPath_def]
  · rfl
  · decide
end QEDReview40sol5
