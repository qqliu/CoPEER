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
  have hsub : G'.edgeFinset ⊆ G.edgeFinset := edgeFinset_mono hle
  have h2 := Finset.card_sdiff_add_card_eq_card hsub
  unfold removed edge_count
  constructor
  · omega
  · omega

abbrev triG : SimpleGraph (Fin 3) := graph 3 [(0,1),(0,2),(1,2)]
abbrev pathH : SimpleGraph (Fin 3) := graph 3 [(0,1),(0,2)]

theorem triG_has_cycle : ¬ triG.IsAcyclic := by
  rw [isAcyclic_iff_forall_edge_isBridge]
  intro h
  have h01 : triG.IsBridge s((0 : Fin 3), 1) :=
    h ((by decide : triG.Adj 0 1) : s((0 : Fin 3), 1) ∈ triG.edgeSet)
  rw [isBridge_iff] at h01
  apply h01.2
  decide

theorem pathH_tree : pathH.IsTree := by
  rw [isTree_iff_connected_and_card]
  refine ⟨by decide, ?_⟩
  rw [Nat.card_eq_fintype_card, ← edgeFinset_card, Nat.card_eq_fintype_card]
  decide

theorem repair_nonvacuous : (∃ k : ℕ, 2 ≤ k ∧ Census_SE_math_1291495__q.edge_count k ≠ (k : ℤ) - 1) ∧ (∃ (k : ℕ) (G G' : SimpleGraph (Fin (k + 1))), 2 ≤ k ∧ G.Connected ∧ ¬ G.IsAcyclic ∧ G' ≤ G ∧ G'.IsTree) := by
  refine ⟨⟨2, le_refl _, by unfold edge_count; norm_num⟩, ⟨2, triG, pathH, le_refl _, by decide,
    triG_has_cycle, ?_, pathH_tree⟩⟩
  intro i j hij
  revert i j hij
  decide

theorem final_theorem : Census_SE_math_1291495__q.SourceTheorem := by
  intro V _ _ k G _ hV hc hE
  rw [isTree_iff_connected_and_card]
  refine ⟨hc, ?_⟩
  rw [Nat.card_eq_fintype_card, ← edgeFinset_card, Nat.card_eq_fintype_card, hV]
  convert congrArg (· + 1) hE using 3

end Census_SE_math_1291495__q
