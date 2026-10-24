import defs_only
/- EVALUATOR-ONLY reference correction for E07 (original package: repair, line 104; repair_sentence, line 114). -/
namespace Census_SE_math_1291495__q.Ref

/-- Reference corrected count: a spanning tree on `k + 1` vertices has `k` edges. -/
def edge_count (k : ℕ) : ℤ := (k : ℤ)

theorem card_eq_card_add_removed {V : Type} [Fintype V] [DecidableEq V] (G G' : SimpleGraph V)
    [DecidableRel G.Adj] [DecidableRel G'.Adj] (hle : G' ≤ G) :
    G.edgeFinset.card = G'.edgeFinset.card + removed G G' := by
  have hsub : G'.edgeFinset ⊆ G.edgeFinset := SimpleGraph.edgeFinset_subset_edgeFinset.mpr hle
  unfold removed
  rw [Finset.card_sdiff_of_subset hsub]
  have := Finset.card_le_card hsub
  omega

theorem universal : ∀ k : ℕ, 2 ≤ k → SentenceWith k (edge_count k) := by
  intro k _ V _ _ G G' _ _ hV _ _ hle hT
  have h1 : G'.edgeFinset.card = k := by
    have := hT.card_edgeFinset
    omega
  have h2 := card_eq_card_add_removed G G' hle
  unfold edge_count
  constructor <;> omega

end Census_SE_math_1291495__q.Ref
