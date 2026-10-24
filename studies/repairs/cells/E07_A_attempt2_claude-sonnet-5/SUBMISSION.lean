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
  intro k _hk V _ _ G G' _ _ hcard hGconn hGcyc hle hTree
  classical
  -- G'.edgeFinset.card + 1 = Fintype.card V = k + 1, hence G'.edgeFinset.card = k
  have h1 : G'.edgeFinset.card + 1 = Fintype.card V := hTree.card_edgeFinset
  rw [hcard] at h1
  have hG'card : G'.edgeFinset.card = k := by omega
  -- G'.edgeFinset ⊆ G.edgeFinset
  have hsub : G'.edgeFinset ⊆ G.edgeFinset := edgeFinset_mono hle
  have huniv : G.edgeFinset ∪ G'.edgeFinset = G.edgeFinset := Finset.union_eq_left.mpr hsub
  have h2 : (G.edgeFinset \ G'.edgeFinset).card + G'.edgeFinset.card = G.edgeFinset.card := by
    have := Finset.card_sdiff_add_card G.edgeFinset G'.edgeFinset
    rwa [huniv] at this
  constructor
  · simp [edge_count, hG'card]
  · have : (removed G G' : ℤ) = ((G.edgeFinset \ G'.edgeFinset).card : ℤ) := by
      unfold removed
    have hGcard : G.edgeFinset.card = k + (G.edgeFinset \ G'.edgeFinset).card := by omega
    simp only [edge_count, this]
    push_cast [hGcard]
    ring

theorem repair_nonvacuous :
    (∃ k : ℕ, 2 ≤ k ∧ Census_SE_math_1291495__q.edge_count k ≠ (k : ℤ) - 1) ∧
      (∃ (k : ℕ) (G G' : SimpleGraph (Fin (k + 1))), 2 ≤ k ∧ G.Connected ∧ ¬ G.IsAcyclic ∧ G' ≤ G ∧ G'.IsTree) := by
  constructor
  · refine ⟨2, le_refl 2, ?_⟩
    simp [edge_count]
  · -- k = 2: G is the triangle graph on Fin 3 (a 3-cycle), G' is a path spanning tree.
    refine ⟨2, graph 3 [(0,1),(1,2),(2,0)], graph 3 [(0,1),(1,2)], le_refl 2, ?_, ?_, ?_, ?_⟩
    · -- Connected
      rw [SimpleGraph.connected_iff]
      constructor
      · rw [SimpleGraph.preconnected_iff_forall_reachable]
        intro u v
        fin_cases u <;> fin_cases v <;>
          first
          | exact SimpleGraph.Reachable.refl _
          | (apply SimpleGraph.Adj.reachable
             refine ⟨by decide, ?_⟩
             decide)
          | (apply SimpleGraph.Reachable.trans (y := (1 : Fin 3))
             · apply SimpleGraph.Adj.reachable
               refine ⟨by decide, ?_⟩
               decide
             · apply SimpleGraph.Adj.reachable
               refine ⟨by decide, ?_⟩
               decide)
      · exact ⟨0⟩
    · -- not acyclic: has a 3-cycle
      intro hac
      have hadj01 : (graph 3 [(0,1),(1,2),(2,0)] : SimpleGraph (Fin 3)).Adj 0 1 := by
        refine ⟨by decide, ?_⟩; decide
      have hadj12 : (graph 3 [(0,1),(1,2),(2,0)] : SimpleGraph (Fin 3)).Adj 1 2 := by
        refine ⟨by decide, ?_⟩; decide
      have hadj20 : (graph 3 [(0,1),(1,2),(2,0)] : SimpleGraph (Fin 3)).Adj 2 0 := by
        refine ⟨by decide, ?_⟩; decide
      let w : (graph 3 [(0,1),(1,2),(2,0)] : SimpleGraph (Fin 3)).Walk 0 0 :=
        SimpleGraph.Walk.cons hadj01 (SimpleGraph.Walk.cons hadj12 (SimpleGraph.Walk.cons hadj20 SimpleGraph.Walk.nil))
      have hcyc : w.IsCycle := by
        constructor
        · constructor
          · decide
          · decide
        · decide
      exact (hac w) hcyc
    · -- G' ≤ G
      intro a b hab
      exact ⟨hab.1, by rcases hab.2 with h | h; · left; simp_all; · right; simp_all⟩
    · -- G' is a tree
      rw [SimpleGraph.isTree_iff_connected_and_card]
      constructor
      · rw [SimpleGraph.connected_iff]
        constructor
        · rw [SimpleGraph.preconnected_iff_forall_reachable]
          intro u v
          fin_cases u <;> fin_cases v <;>
            first
            | exact SimpleGraph.Reachable.refl _
            | (apply SimpleGraph.Adj.reachable
               refine ⟨by decide, ?_⟩
               decide)
            | (apply SimpleGraph.Reachable.trans (y := (1 : Fin 3))
               · apply SimpleGraph.Adj.reachable
                 refine ⟨by decide, ?_⟩
                 decide
               · apply SimpleGraph.Adj.reachable
                 refine ⟨by decide, ?_⟩
                 decide)
        · exact ⟨0⟩
      · decide

theorem final_theorem : Census_SE_math_1291495__q.SourceTheorem := by
  intro V _ _ k G _ hcard hconn hedges
  rw [SimpleGraph.isTree_iff_connected_and_card]
  refine ⟨hconn, ?_⟩
  rw [Nat.card_eq_fintype_card, ← SimpleGraph.edgeFinset_card, hedges, Nat.card_eq_fintype_card, hcard]

end Census_SE_math_1291495__q
