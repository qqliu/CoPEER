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
  intro k _ V _ _ G G' _ _ hcard hGconn hGacyc hGle hGtree
  classical
  have hcardV : Nat.card V = k + 1 := by
    rw [Nat.card_eq_fintype_card, hcard]
  have hTree : (G'.edgeFinset.card : ℤ) = edge_count k := by
    have h := (isTree_iff_connected_and_card (G := G')).mp hGtree
    have h2 : Fintype.card G'.edgeSet + 1 = Fintype.card V := by
      rw [← Nat.card_eq_fintype_card, ← Nat.card_eq_fintype_card]; exact h.2
    rw [← edgeFinset_card] at h2
    rw [hcard] at h2
    have hk : G'.edgeFinset.card = k := by omega
    simp [edge_count, hk]
  refine ⟨hTree, ?_⟩
  have hsub : G'.edgeFinset ⊆ G.edgeFinset := by
    intro e he
    rw [mem_edgeFinset] at *
    exact edgeSet_mono hGle he
  have hremoved : (removed G G' : ℤ) = (G.edgeFinset.card : ℤ) - (G'.edgeFinset.card : ℤ) := by
    unfold removed
    exact Finset.cast_card_sdiff hsub
  rw [hremoved, hTree]
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
  intro V _ _ k G _ hcard hGconn hGedges
  rw [isTree_iff_connected_and_card]
  refine ⟨hGconn, ?_⟩
  rw [Nat.card_eq_fintype_card, Nat.card_eq_fintype_card, ← edgeFinset_card, hGedges, hcard]

end Census_SE_math_1291495__q
