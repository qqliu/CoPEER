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

theorem repair_statement : ∀ (V : Type) [Fintype V] (G : SimpleGraph V) [Fintype G.edgeSet], SE_math_782216_q_Census.guard G → SE_math_782216_q_Census.BaseClaim G := by
  intro V _ G _ hconn hcard
  classical
  by_contra hcard'
  push_neg at hcard'
  -- card V ≥ 2, so there are two distinct vertices
  obtain ⟨a, b, hab⟩ := Fintype.exists_pair_of_one_lt_card hcard'
  -- connected graph gives a walk between a and b
  have hreach : G.Reachable a b := hconn.preconnected a b
  -- edgeFinset empty means no edges at all, i.e. G = ⊥
  have hbot : G = ⊥ := by
    rw [← SimpleGraph.edgeFinset_eq_empty, ← Finset.card_eq_zero]; exact hcard
  rw [hbot, SimpleGraph.reachable_bot] at hreach
  exact hab hreach

theorem repair_nonvacuous : (∃ (V : Type) (_ : Fintype V) (G : SimpleGraph V) (_ : Fintype G.edgeSet), G.edgeFinset.card = 0 ∧ SE_math_782216_q_Census.guard G) ∧ (∃ (V : Type) (_ : Fintype V) (G : SimpleGraph V) (_ : Fintype G.edgeSet), G.edgeFinset.card = 0 ∧ ¬ SE_math_782216_q_Census.guard G) := by
  constructor
  · refine ⟨Unit, inferInstance, ⊥, inferInstance, ?_, ?_⟩
    · simp
    · show (⊥ : SimpleGraph Unit).Connected
      refine ⟨fun x y => ?_⟩
      have : x = y := Subsingleton.elim x y
      rw [this]
  · refine ⟨Fin 2, inferInstance, ⊥, inferInstance, ?_, ?_⟩
    · simp
    · show ¬ (⊥ : SimpleGraph (Fin 2)).Connected
      intro hconn
      have hreach : (⊥ : SimpleGraph (Fin 2)).Reachable 0 1 := hconn.preconnected 0 1
      rw [SimpleGraph.reachable_bot] at hreach
      exact absurd hreach (by decide)

theorem final_theorem : SE_math_782216_q_Census.SourceGoal := by
  intro V _ G _
  exact G.sum_degrees_eq_twice_card_edges

end SE_math_782216_q_Census
