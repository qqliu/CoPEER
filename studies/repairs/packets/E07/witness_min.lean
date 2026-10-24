import defs_only
/- Record SE_math_1291495__q (E07): the source sentence fails at k = 2, on the triangle G
(3 vertices, 3 edges) with the path H = G minus one cycle edge (2 edges, m = 1):
the printed counts would be 1 and 1 + 1. -/
set_option maxRecDepth 10000
set_option maxHeartbeats 4000000

namespace Census_SE_math_1291495__q
open SimpleGraph

namespace TreeCount
def G := graph 3 [(0,1),(0,2),(1,2)]
def H := graph 3 [(0,1),(0,2)]
instance : DecidableRel G.Adj := inferInstanceAs (DecidableRel (graph _ _).Adj)
instance : DecidableRel H.Adj := inferInstanceAs (DecidableRel (graph _ _).Adj)

theorem G_connected : G.Connected := by decide

/-- The triangle contains a cycle: its edge 0-1 is not a bridge (0 and 1 stay joined via 2). -/
theorem G_has_cycle : ¬ G.IsAcyclic := by
  rw [isAcyclic_iff_forall_edge_isBridge]
  intro h
  have h01 : G.IsBridge s((0 : Fin 3), 1) :=
    h ((by decide : G.Adj 0 1) : s((0 : Fin 3), 1) ∈ G.edgeSet)
  rw [isBridge_iff] at h01
  apply h01.2
  decide

theorem H_le_G : H ≤ G := by
  intro i j hij
  revert i j hij
  decide

theorem H_connected : H.Connected := by decide

/-- The path is acyclic: each of its two edges is a bridge. -/
theorem H_acyclic : H.IsAcyclic := by
  rw [isAcyclic_iff_forall_edge_isBridge]
  intro e he
  rw [← mem_edgeFinset] at he
  have hE : H.edgeFinset = {s((0 : Fin 3), 1), s((0 : Fin 3), 2)} := by decide
  rw [hE] at he
  simp only [Finset.mem_insert, Finset.mem_singleton] at he
  rcases he with rfl | rfl
  · rw [isBridge_iff]; refine ⟨by decide, ?_⟩; decide
  · rw [isBridge_iff]; refine ⟨by decide, ?_⟩; decide

theorem H_tree : H.IsTree := ⟨H_connected, H_acyclic⟩

theorem H_edges : H.edgeFinset.card = 2 := by decide
theorem G_edges : G.edgeFinset.card = 3 := by decide
theorem removed_one : removed G H = 1 := by decide
end TreeCount

theorem source_sentence_false_at_two : ¬ SourceSentence 2 := by
  intro h
  have h2 := h (Fin 3) TreeCount.G TreeCount.H (by simp) TreeCount.G_connected
    TreeCount.G_has_cycle TreeCount.H_le_G TreeCount.H_tree
  have h3 := h2.1
  rw [TreeCount.H_edges] at h3
  norm_num at h3

theorem universal_source_sentence_false : ¬ UniversalSourceSentence :=
  fun h => source_sentence_false_at_two (h 2)

end Census_SE_math_1291495__q

#print axioms Census_SE_math_1291495__q.TreeCount.H_tree
#print axioms Census_SE_math_1291495__q.source_sentence_false_at_two
#print axioms Census_SE_math_1291495__q.universal_source_sentence_false
