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
def guard {V : Type} [Fintype V] (G : SimpleGraph V) : Prop := G.Preconnected

/-- The corrected base-case sentence: under the added hypothesis, a finite simple graph without edges has
at most one vertex (shape fixed). -/
def CorrectedBaseClaim : Prop :=
  ∀ (V : Type) [Fintype V] (G : SimpleGraph V) [Fintype G.edgeSet], guard G → BaseClaim G
-- ===== END FIXED PART =====

theorem repair_statement : ∀ (V : Type) [Fintype V] (G : SimpleGraph V) [Fintype G.edgeSet], SE_math_782216_q_Census.guard G → SE_math_782216_q_Census.BaseClaim G := by
  intro V _ G _ hguard hcard
  have hbot : G = ⊥ := SimpleGraph.edgeFinset_eq_empty.mp (Finset.card_eq_zero.mp hcard)
  have hpre : (⊥ : SimpleGraph V).Preconnected := hbot ▸ hguard
  have hsub : Subsingleton V := (SimpleGraph.preconnected_bot_iff_subsingleton).mp hpre
  exact Fintype.card_le_one_iff_subsingleton.mpr hsub

theorem repair_nonvacuous : (∃ (V : Type) (_ : Fintype V) (G : SimpleGraph V) (_ : Fintype G.edgeSet), G.edgeFinset.card = 0 ∧ SE_math_782216_q_Census.guard G) ∧ (∃ (V : Type) (_ : Fintype V) (G : SimpleGraph V) (_ : Fintype G.edgeSet), G.edgeFinset.card = 0 ∧ ¬ SE_math_782216_q_Census.guard G) := by
  constructor
  · refine ⟨PUnit, inferInstance, ⊥, inferInstance, ?_, ?_⟩
    · simp
    · show (⊥ : SimpleGraph PUnit).Preconnected
      exact SimpleGraph.preconnected_bot
  · refine ⟨Fin 2, inferInstance, ⊥, inferInstance, ?_, ?_⟩
    · simp
    · show ¬ (⊥ : SimpleGraph (Fin 2)).Preconnected
      exact SimpleGraph.not_preconnected_bot

theorem final_theorem : SE_math_782216_q_Census.SourceGoal := by
  intro V _ G _
  exact SimpleGraph.sum_degrees_eq_twice_card_edges G

end SE_math_782216_q_Census
