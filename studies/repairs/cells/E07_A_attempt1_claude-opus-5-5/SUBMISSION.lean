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
  intro k _ V _ _ G G' _ _ hV _ _ hle hT
  have h1 := hT.card_edgeFinset
  have hsub : G'.edgeFinset ⊆ G.edgeFinset := edgeFinset_subset_edgeFinset.mpr hle
  have h2 := Finset.card_sdiff_add_card_eq_card hsub
  unfold removed edge_count
  refine ⟨by omega, ?_⟩
  omega

theorem final_theorem : Census_SE_math_1291495__q.SourceTheorem := by
  intro V _ _ k G _ hV hG hE
  rw [isTree_iff_connected_and_card]
  refine ⟨hG, ?_⟩
  rw [Nat.card_eq_fintype_card, Nat.card_eq_fintype_card, ← edgeFinset_card, hE, hV]

theorem repair_nonvacuous : (∃ k : ℕ, 2 ≤ k ∧ Census_SE_math_1291495__q.edge_count k ≠ (k : ℤ) - 1) ∧ (∃ (k : ℕ) (G G' : SimpleGraph (Fin (k + 1))), 2 ≤ k ∧ G.Connected ∧ ¬ G.IsAcyclic ∧ G' ≤ G ∧ G'.IsTree) := by
  refine ⟨⟨2, le_refl _, by unfold edge_count; omega⟩, ?_⟩
  obtain ⟨T, hT, hTt⟩ := (connected_top : (⊤ : SimpleGraph (Fin 3)).Connected).exists_isTree_le
  refine ⟨2, ⊤, T, le_refl _, connected_top, ?_, hT, hTt⟩
  intro hac
  have ht : (⊤ : SimpleGraph (Fin 3)).IsTree := ⟨connected_top, hac⟩
  have h1 := ht.card_edgeFinset
  rw [card_edgeFinset_top_eq_card_choose_two] at h1
  simp at h1

end Census_SE_math_1291495__q
