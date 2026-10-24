import defs_only
/-!
Record E09: correction template.
Fill the ONE hole `«HOLE»` in the FIXED PART (nothing else in the fixed part may change), then prove
the OBLIGATIONS below with exactly these names and statements. Helper lemmas may be added between the
fixed part and the obligations, inside the namespace. Import nothing else.
-/
namespace SE_math_782216_q_Census

-- ===== FIXED PART: only the hole «HOLE» may be edited =====
/-- The hypothesis to add to the source's base-case sentence: a condition on the graph `G` drawn from
the source's context (connectivity). The hole must be a proposition about `G` in Mathlib vocabulary; it
may not mention the number of vertices (`Fintype.card`, `Subsingleton`, ...), edge counts or `BaseClaim`. -/
def guard {V : Type} [Fintype V] (G : SimpleGraph V) : Prop := G.Connected

/-- The corrected base-case sentence: under the added hypothesis, a finite simple graph without edges has
at most one vertex (shape fixed). -/
def CorrectedBaseClaim : Prop :=
  ∀ (V : Type) [Fintype V] (G : SimpleGraph V) [Fintype G.edgeSet], guard G → BaseClaim G
-- ===== END FIXED PART =====

theorem repair_statement :
    ∀ (V : Type) [Fintype V] (G : SimpleGraph V) [Fintype G.edgeSet],
      SE_math_782216_q_Census.guard G → SE_math_782216_q_Census.BaseClaim G := by
  intro V _ G _ hconn hcard
  by_contra hcard1
  push Not at hcard1
  -- hcard1 : 1 < Fintype.card V, so there exist two distinct vertices
  obtain ⟨v, w, hvw⟩ := Fintype.exists_pair_of_one_lt_card hcard1
  -- connectivity gives a path (reachability) between v and w
  have hreach : G.Reachable v w := hconn.preconnected v w
  obtain ⟨p⟩ := hreach
  -- since G has no edges, the only possible walk between distinct vertices doesn't exist
  have hne : v ≠ w := hvw
  have : p.length ≠ 0 := by
    intro h0
    exact hne (SimpleGraph.Walk.eq_of_length_eq_zero h0)
  obtain ⟨u, huv, huw, hp'⟩ := p.exists_eq_cons_of_ne hne
  have hedge : G.Adj v u := huv
  have hmemSet : s(v, u) ∈ G.edgeSet := by rw [SimpleGraph.mem_edgeSet]; exact hedge
  have hmem : s(v, u) ∈ G.edgeFinset := by
    rw [SimpleGraph.mem_edgeFinset]; exact hmemSet
  have hne' : G.edgeFinset.Nonempty := ⟨_, hmem⟩
  rw [← Finset.card_pos] at hne'
  omega

theorem repair_nonvacuous :
    (∃ (V : Type) (_ : Fintype V) (G : SimpleGraph V) (_ : Fintype G.edgeSet),
      G.edgeFinset.card = 0 ∧ SE_math_782216_q_Census.guard G) ∧
    (∃ (V : Type) (_ : Fintype V) (G : SimpleGraph V) (_ : Fintype G.edgeSet),
      G.edgeFinset.card = 0 ∧ ¬ SE_math_782216_q_Census.guard G) := by
  constructor
  · -- single-vertex edgeless graph: connected, edgeless
    refine ⟨PUnit, inferInstance, ⊥, inferInstance, ?_, ?_⟩
    · simp
    · constructor
      intro a b
      have : a = b := Subsingleton.elim a b
      rw [this]
  · -- two-vertex edgeless graph: edgeless, not connected
    refine ⟨Bool, inferInstance, ⊥, inferInstance, ?_, ?_⟩
    · simp
    · intro hconn
      have hreach : (⊥ : SimpleGraph Bool).Reachable true false := hconn.preconnected true false
      obtain ⟨p⟩ := hreach
      have hne : (true : Bool) ≠ false := by decide
      have hlen : p.length ≠ 0 := by
        intro h0
        exact hne (SimpleGraph.Walk.eq_of_length_eq_zero h0)
      obtain ⟨u, huv, _huw, _hp'⟩ := p.exists_eq_cons_of_ne hne
      exact huv

theorem final_theorem : SE_math_782216_q_Census.SourceGoal := by
  intro V _ G _
  exact G.sum_degrees_eq_twice_card_edges

end SE_math_782216_q_Census
