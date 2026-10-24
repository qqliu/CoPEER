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

theorem repair_statement :
    ∀ k : ℕ, 2 ≤ k → Census_SE_math_1291495__q.SentenceWith k (Census_SE_math_1291495__q.edge_count k) := by
  intro k _hk V _ _ G G' _ _ hcard hGconn hGcyc hGle hG'tree
  have hsub : G'.edgeFinset ⊆ G.edgeFinset := (edgeFinset_subset_edgeFinset).mpr hGle
  have hcardG' : G'.edgeFinset.card + 1 = Fintype.card V := hG'tree.card_edgeFinset
  have hcardG'k : G'.edgeFinset.card = k := by
    have := hcardG'
    rw [hcard] at this
    omega
  have hremoved : removed G G' = G.edgeFinset.card - G'.edgeFinset.card := by
    unfold removed
    rw [Finset.card_sdiff_of_subset hsub]
  have hle : G'.edgeFinset.card ≤ G.edgeFinset.card := Finset.card_le_card hsub
  have hremovedZ : (removed G G' : ℤ) = (G.edgeFinset.card : ℤ) - (G'.edgeFinset.card : ℤ) := by
    rw [hremoved]
    omega
  constructor
  · show (G'.edgeFinset.card : ℤ) = edge_count k
    unfold edge_count
    rw [hcardG'k]
  · show (G.edgeFinset.card : ℤ) = edge_count k + (removed G G' : ℤ)
    unfold edge_count
    rw [hremovedZ, hcardG'k]
    ring

theorem repair_nonvacuous :
    (∃ k : ℕ, 2 ≤ k ∧ Census_SE_math_1291495__q.edge_count k ≠ (k : ℤ) - 1) ∧
      (∃ (k : ℕ) (G G' : SimpleGraph (Fin (k + 1))),
        2 ≤ k ∧ G.Connected ∧ ¬ G.IsAcyclic ∧ G' ≤ G ∧ G'.IsTree) := by
  constructor
  · refine ⟨2, le_refl 2, ?_⟩
    simp [edge_count]
  · have hGconn : (⊤ : SimpleGraph (Fin 3)).Connected := SimpleGraph.connected_top
    have hGcyc : ¬ (⊤ : SimpleGraph (Fin 3)).IsAcyclic := by
      rw [← SimpleGraph.cycleGraph_three_eq_top]
      intro h
      exact h (SimpleGraph.cycleGraph.cycle 0) SimpleGraph.cycleGraph.isCycle_cycle
    obtain ⟨G', hG'le, hG'tree⟩ := hGconn.exists_isTree_le
    exact ⟨2, (⊤ : SimpleGraph (Fin 3)), G', le_refl 2, hGconn, hGcyc, hG'le, hG'tree⟩

theorem final_theorem : Census_SE_math_1291495__q.SourceTheorem := by
  intro V _ _ k G _ hcard hGconn hGedges
  refine ⟨hGconn, ?_⟩
  by_contra hnot
  obtain ⟨T, hTle, hTtree⟩ := hGconn.exists_isTree_le
  have hTcard : T.edgeFinset.card + 1 = Fintype.card V := hTtree.card_edgeFinset
  have hTcardk : T.edgeFinset.card = k := by
    rw [hcard] at hTcard
    omega
  have hsub : T.edgeFinset ⊆ G.edgeFinset := (edgeFinset_subset_edgeFinset).mpr hTle
  have hEqCard : T.edgeFinset.card = G.edgeFinset.card := by
    rw [hTcardk, hGedges]
  have hEqSet : T.edgeFinset = G.edgeFinset := Finset.eq_of_subset_of_card_le hsub (le_of_eq hEqCard.symm)
  have hEqSet' : T.edgeSet = G.edgeSet := by
    have := congrArg (fun s : Finset (Sym2 V) => (s : Set (Sym2 V))) hEqSet
    simpa [SimpleGraph.coe_edgeFinset] using this
  have hEq : T = G := edgeSet_inj.mp hEqSet'
  exact hnot (hEq ▸ hTtree.isAcyclic)

end Census_SE_math_1291495__q
