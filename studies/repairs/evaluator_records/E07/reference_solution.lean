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

theorem card_eq_card_add_removed {V : Type} [Fintype V] [DecidableEq V] (G G' : SimpleGraph V)
    [DecidableRel G.Adj] [DecidableRel G'.Adj] (hle : G' ≤ G) :
    G.edgeFinset.card = G'.edgeFinset.card + removed G G' := by
  have hsub : G'.edgeFinset ⊆ G.edgeFinset := SimpleGraph.edgeFinset_subset_edgeFinset.mpr hle
  unfold removed
  rw [Finset.card_sdiff_of_subset hsub]
  have := Finset.card_le_card hsub
  omega

abbrev G3 := graph 3 [(0,1),(0,2),(1,2)]
abbrev H3 := graph 3 [(0,1),(0,2)]

theorem G3_connected : G3.Connected := by decide

theorem G3_has_cycle : ¬ G3.IsAcyclic := by
  rw [SimpleGraph.isAcyclic_iff_forall_edge_isBridge]
  intro h
  have h01 : G3.IsBridge s((0 : Fin 3), 1) :=
    h ((by decide : G3.Adj 0 1) : s((0 : Fin 3), 1) ∈ G3.edgeSet)
  rw [SimpleGraph.isBridge_iff] at h01
  apply h01.2
  decide

theorem H3_le_G3 : H3 ≤ G3 := by
  intro i j hij
  revert i j hij
  decide

theorem H3_tree : H3.IsTree := by
  rw [SimpleGraph.isTree_iff_connected_and_card]
  constructor
  · decide
  · rw [Nat.card_eq_fintype_card, Nat.card_eq_fintype_card]
    decide

-- ===== OBLIGATIONS: keep the names and statements; replace each `sorry` by a proof =====
/-- Universal: the corrected sentence holds for every `k ≥ 2`, every finite vertex type with `k + 1`
elements, every connected `G` with a cycle and every spanning tree `G'` of `G`. -/
theorem repair_statement : ∀ k : ℕ, 2 ≤ k → Census_SE_math_1291495__q.SentenceWith k (Census_SE_math_1291495__q.edge_count k) := by
  intro k _ V _ _ G G' _ _ hV _ _ hle hT
  have h1 : G'.edgeFinset.card = k := by
    have := hT.card_edgeFinset
    omega
  have h2 := card_eq_card_add_removed G G' hle
  unfold edge_count
  constructor <;> omega

/-- Non-vacuity: the corrected count differs from the printed `k - 1` for some admissible `k`, and the
hypotheses of the sentence are satisfiable for some `k ≥ 2`. -/
theorem repair_nonvacuous : (∃ k : ℕ, 2 ≤ k ∧ Census_SE_math_1291495__q.edge_count k ≠ (k : ℤ) - 1) ∧ (∃ (k : ℕ) (G G' : SimpleGraph (Fin (k + 1))), 2 ≤ k ∧ G.Connected ∧ ¬ G.IsAcyclic ∧ G' ≤ G ∧ G'.IsTree) := ⟨⟨2, by norm_num, by unfold edge_count; norm_num⟩, ⟨2, G3, H3, by norm_num, G3_connected, G3_has_cycle, H3_le_G3, H3_tree⟩⟩

/-- The theorem the source sets out to prove, unchanged (`SourceTheorem` from defs_only: a connected
graph on `k + 1` vertices with `k` edges is a tree). If you cannot prove it, replace this declaration
(this doc comment included) by the single line `-- CANNOT: <reason>`. -/
theorem final_theorem : Census_SE_math_1291495__q.SourceTheorem := by
  intro V _ _ k G _ hV hc hE
  obtain ⟨T, hle, hT⟩ := hc.exists_isTree_le
  classical
  have h1 : T.edgeFinset.card = k := by
    have := hT.card_edgeFinset
    omega
  have h2 := card_eq_card_add_removed G T hle
  have hm : removed G T = 0 := by omega
  have hTG : T = G := by
    unfold removed at hm
    rw [Finset.card_eq_zero, Finset.sdiff_eq_empty_iff_subset, SimpleGraph.edgeFinset_subset_edgeFinset] at hm
    exact le_antisymm hle hm
  exact hTG ▸ hT
-- ===== END OBLIGATIONS =====
end Census_SE_math_1291495__q
