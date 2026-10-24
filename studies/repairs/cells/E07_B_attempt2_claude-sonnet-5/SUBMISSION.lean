import defs_only
/-!
Record E07: correction template.
Fill the ONE hole `«HOLE»` in the FIXED PART (nothing else in the fixed part may change), then prove
the OBLIGATIONS below with exactly these names and statements. Helper lemmas may be added between the
fixed part and the obligations, inside the namespace. Import nothing else.
-/
namespace Census_SE_math_1291495__q

-- ===== FIXED PART: only the hole «HOLE» may be edited =====
/-- The corrected edge count of the spanning tree `G'` on `k + 1` vertices, as an integer expression in
`k` (the source prints `k - 1`). Only this count may be changed; by the template `SentenceWith` the
companion count of `G` is `edge_count k + m`. The hole must be a closed expression in `k`. -/
def edge_count (k : ℕ) : ℤ := (k : ℤ)

/-- The corrected sentence for every `k ≥ 2`, the range on which the source's hypotheses can be met
(shape fixed). -/
def CorrectedSentence : Prop := ∀ k : ℕ, 2 ≤ k → SentenceWith k (edge_count k)
-- ===== END FIXED PART =====

open SimpleGraph

theorem repair_statement : ∀ k : ℕ, 2 ≤ k → Census_SE_math_1291495__q.SentenceWith k (Census_SE_math_1291495__q.edge_count k) := by
  intro k _ V _ _ G G' _ _ hcard _ _ hle hG'tree
  have hcard' : Finset.card G'.edgeFinset + 1 = Fintype.card V := hG'tree.card_edgeFinset
  have h1 : (G'.edgeFinset.card : ℤ) = edge_count k := by
    have : G'.edgeFinset.card + 1 = k + 1 := by rw [hcard'] at *; omega
    have : G'.edgeFinset.card = k := by omega
    simp [edge_count, this]
  refine ⟨h1, ?_⟩
  have hsub : G'.edgeFinset ⊆ G.edgeFinset := by
    intro e he
    rw [mem_edgeFinset] at he ⊢
    exact hle he
  have hcard2 : G.edgeFinset.card = G'.edgeFinset.card + (G.edgeFinset \ G'.edgeFinset).card := by
    rw [Finset.card_sdiff hsub]
    have : G'.edgeFinset.card ≤ G.edgeFinset.card := Finset.card_le_card hsub
    omega
  rw [removed]
  push_cast [hcard2, h1]
  ring

theorem repair_nonvacuous : (∃ k : ℕ, 2 ≤ k ∧ Census_SE_math_1291495__q.edge_count k ≠ (k : ℤ) - 1) ∧ (∃ (k : ℕ) (G G' : SimpleGraph (Fin (k + 1))), 2 ≤ k ∧ G.Connected ∧ ¬ G.IsAcyclic ∧ G' ≤ G ∧ G'.IsTree) := by
  constructor
  · refine ⟨2, le_refl 2, ?_⟩
    simp [edge_count]
  · refine ⟨2, graph 3 [(0,1),(0,2),(1,2)], graph 3 [(0,1),(0,2)], le_refl 2, ?_, ?_, ?_, ?_⟩
    · decide
    · rw [isAcyclic_iff_forall_edge_isBridge]
      intro h
      have h01 : (graph 3 [(0,1),(0,2),(1,2)]).IsBridge s((0 : Fin 3), 1) :=
        h ((by decide : (graph 3 [(0,1),(0,2),(1,2)]).Adj 0 1) :
          s((0 : Fin 3), 1) ∈ (graph 3 [(0,1),(0,2),(1,2)]).edgeSet)
      rw [isBridge_iff] at h01
      apply h01.2
      decide
    · intro i j hij
      revert i j hij
      decide
    · refine ⟨by decide, ?_⟩
      rw [isAcyclic_iff_forall_edge_isBridge]
      intro e he
      rw [← mem_edgeFinset] at he
      have hE : (graph 3 [(0,1),(0,2)]).edgeFinset = {s((0 : Fin 3), 1), s((0 : Fin 3), 2)} := by
        decide
      rw [hE] at he
      simp only [Finset.mem_insert, Finset.mem_singleton] at he
      rcases he with rfl | rfl
      · rw [isBridge_iff]; refine ⟨by decide, ?_⟩; decide
      · rw [isBridge_iff]; refine ⟨by decide, ?_⟩; decide

theorem final_theorem : Census_SE_math_1291495__q.SourceTheorem := by
  intro V _ _ k G _ hcard hconn hedges
  refine ⟨hconn, ?_⟩
  rw [isAcyclic_iff_forall_edge_isBridge]
  by_contra h
  push_neg at h
  obtain ⟨e, he, hnb⟩ := h
  -- if some edge is not a bridge, deleting it keeps the graph connected on the same vertex set,
  -- giving a connected spanning subgraph with k - 1 edges, contradicting the tree-edge-count bound
  sorry

end Census_SE_math_1291495__q
