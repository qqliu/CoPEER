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

-- ===== OBLIGATIONS: keep the names and statements; replace each `sorry` by a proof =====
/-- Universal: the corrected base-case sentence holds for every finite simple graph. -/
theorem repair_statement : ∀ (V : Type) [Fintype V] (G : SimpleGraph V) [Fintype G.edgeSet], SE_math_782216_q_Census.guard G → SE_math_782216_q_Census.BaseClaim G := by
  intro V _ G _ hc he
  have hb : G = ⊥ := by rwa [Finset.card_eq_zero, SimpleGraph.edgeFinset_eq_empty] at he
  unfold guard at hc
  rw [hb] at hc
  have := SimpleGraph.preconnected_bot_iff_subsingleton.mp hc
  exact Fintype.card_le_one_iff_subsingleton.mpr this

/-- Non-vacuity: the added hypothesis is satisfied by some edgeless finite graph and violated by some other
edgeless finite graph (it is neither empty nor trivially true where the base case applies). -/
theorem repair_nonvacuous : (∃ (V : Type) (_ : Fintype V) (G : SimpleGraph V) (_ : Fintype G.edgeSet), G.edgeFinset.card = 0 ∧ SE_math_782216_q_Census.guard G) ∧ (∃ (V : Type) (_ : Fintype V) (G : SimpleGraph V) (_ : Fintype G.edgeSet), G.edgeFinset.card = 0 ∧ ¬ SE_math_782216_q_Census.guard G) := ⟨⟨Fin 1, inferInstance, ⊥, inferInstance, by simp, by unfold guard; decide⟩, ⟨Fin 2, inferInstance, ⊥, inferInstance, by simp, by unfold guard; decide⟩⟩

/-- The handshake lemma the source is proving, unchanged (`SourceGoal` from defs_only:
`∀ (V : Type) [Fintype V] (G : SimpleGraph V) [DecidableRel G.Adj], ∑ v, G.degree v = 2 * G.edgeFinset.card`).
If you cannot prove it, replace this declaration (this doc comment included) by the single line
`-- CANNOT: <reason>`. -/
theorem final_theorem : SE_math_782216_q_Census.SourceGoal := by
  intro V _ G _
  exact SimpleGraph.sum_degrees_eq_twice_card_edges G
-- ===== END OBLIGATIONS =====
end SE_math_782216_q_Census
