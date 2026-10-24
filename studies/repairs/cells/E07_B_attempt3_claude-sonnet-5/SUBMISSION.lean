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
  intro k _hk V _ _ G G' _ _ hcard _hGconn _hGcyc hle hTree
  have hT : G'.edgeFinset.card + 1 = Fintype.card V := hTree.card_edgeFinset
  rw [hcard] at hT
  have hG'card : G'.edgeFinset.card = k := by omega
  constructor
  · simp [edge_count, hG'card]
  · have hsub : G'.edgeFinset ⊆ G.edgeFinset := by
      intro e he
      rw [SimpleGraph.mem_edgeFinset] at he ⊢
      exact hle he
    have hcardEq : G.edgeFinset.card = G'.edgeFinset.card + (G.edgeFinset \ G'.edgeFinset).card := by
      rw [Finset.card_sdiff_add_card_eq_card hsub]
    unfold removed
    rw [hcardEq, hG'card]
    push_cast [edge_count]
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
        h ((by decide : (graph 3 [(0,1),(0,2),(1,2)]).Adj 0 1) : s((0 : Fin 3), 1) ∈ (graph 3 [(0,1),(0,2),(1,2)]).edgeSet)
      rw [isBridge_iff] at h01
      apply h01.2
      decide
    · intro i j hij
      revert i j hij
      decide
    · constructor
      · decide
      · rw [isAcyclic_iff_forall_edge_isBridge]
        intro e he
        rw [← mem_edgeFinset] at he
        have hE : (graph 3 [(0,1),(0,2)]).edgeFinset = {s((0 : Fin 3), 1), s((0 : Fin 3), 2)} := by decide
        rw [hE] at he
        simp only [Finset.mem_insert, Finset.mem_singleton] at he
        rcases he with rfl | rfl
        · rw [isBridge_iff]; refine ⟨by decide, ?_⟩; decide
        · rw [isBridge_iff]; refine ⟨by decide, ?_⟩; decide

theorem final_theorem : Census_SE_math_1291495__q.SourceTheorem := by
  intro V _ _ k G _ hcard hconn hedges
  rw [isTree_iff_connected_and_card]
  refine ⟨hconn, ?_⟩
  have h1 : Nat.card G.edgeSet = G.edgeFinset.card := by
    rw [Nat.card_eq_fintype_card]
    congr 1
  have h2 : Nat.card V = Fintype.card V := Nat.card_eq_fintype_card
  rw [h1, h2, hcard, hedges]

end Census_SE_math_1291495__q
