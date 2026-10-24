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
  intro k _hk
  intro V _ _ G G' _ _ hcard _hconn _hcyc hle htree
  have h1 : G'.edgeFinset.card + 1 = Fintype.card V := htree.card_edgeFinset
  rw [hcard] at h1
  have hcardG' : G'.edgeFinset.card = k := by omega
  refine ⟨?_, ?_⟩
  · simp [edge_count, hcardG']
  · have hsub : G'.edgeFinset ⊆ G.edgeFinset := edgeFinset_mono hle
    have hnat : G.edgeFinset.card = G'.edgeFinset.card + (G.edgeFinset \ G'.edgeFinset).card := by
      rw [Finset.card_sdiff_of_subset hsub]
      have : G'.edgeFinset.card ≤ G.edgeFinset.card := Finset.card_le_card hsub
      omega
    unfold removed
    rw [hnat, hcardG']
    simp only [edge_count]
    push_cast
    ring

theorem repair_nonvacuous :
    (∃ k : ℕ, 2 ≤ k ∧ Census_SE_math_1291495__q.edge_count k ≠ (k : ℤ) - 1) ∧
    (∃ (k : ℕ) (G G' : SimpleGraph (Fin (k + 1))), 2 ≤ k ∧ G.Connected ∧ ¬ G.IsAcyclic ∧ G' ≤ G ∧ G'.IsTree) := by
  constructor
  · refine ⟨2, le_refl 2, ?_⟩
    simp [edge_count]
  · refine ⟨2, graph 3 [(0,1),(1,2),(0,2)], graph 3 [(0,1),(1,2)], le_refl 2, ?_, ?_, ?_, ?_⟩
    · decide
    · intro hacyc
      have hconn : (graph 3 [(0,1),(1,2),(0,2)] : SimpleGraph (Fin 3)).Connected := by decide
      have htree : (graph 3 [(0,1),(1,2),(0,2)] : SimpleGraph (Fin 3)).IsTree := ⟨hconn, hacyc⟩
      have h1 := htree.card_edgeFinset
      have h2 : (graph 3 [(0,1),(1,2),(0,2)] : SimpleGraph (Fin 3)).edgeFinset.card = 3 := by decide
      simp [h2] at h1
    · intro v w hadj
      fin_cases v <;> fin_cases w <;> simp_all [graph]
    · have hconn : (graph 3 [(0,1),(1,2)] : SimpleGraph (Fin 3)).Connected := by decide
      have hcard : (graph 3 [(0,1),(1,2)] : SimpleGraph (Fin 3)).edgeFinset.card = 2 := by decide
      have hcardV : Nat.card (Fin 3) = 3 := by
        rw [Nat.card_eq_fintype_card, Fintype.card_fin]
      have : Nat.card (graph 3 [(0,1),(1,2)] : SimpleGraph (Fin 3)).edgeSet + 1 = Nat.card (Fin 3) := by
        rw [Nat.card_eq_fintype_card, ← edgeFinset_card, hcard, hcardV]
      exact isTree_iff_connected_and_card.mpr ⟨hconn, this⟩

theorem final_theorem : Census_SE_math_1291495__q.SourceTheorem := by
  intro V _ _ k G _ hcard hconn hedges
  obtain ⟨T, hTG, hTT⟩ := hconn.exists_isTree_le
  have hTcard : T.edgeFinset.card + 1 = Fintype.card V := hTT.card_edgeFinset
  rw [hcard] at hTcard
  have hTk : T.edgeFinset.card = k := by omega
  have hsub : T.edgeFinset ⊆ G.edgeFinset := edgeFinset_mono hTG
  have heq : T.edgeFinset = G.edgeFinset :=
    Finset.eq_of_subset_of_card_le hsub (by rw [hTk, hedges])
  have hTG_eq : T = G := edgeFinset_inj.mp heq
  rw [← hTG_eq]
  exact hTT

end Census_SE_math_1291495__q
