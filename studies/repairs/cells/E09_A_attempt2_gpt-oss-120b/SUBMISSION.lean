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
def guard {V : Type} [Fintype V] (G : SimpleGraph V) : Prop := G.IsPreconnected

/-- The corrected base-case sentence: under the added hypothesis, a finite simple graph without edges has
at most one vertex (shape fixed). -/
def CorrectedBaseClaim : Prop :=
  ∀ (V : Type) [Fintype V] (G : SimpleGraph V) [Fintype G.edgeSet], guard G → BaseClaim G
-- ===== END FIXED PART =====

theorem repair_statement :
    ∀ (V : Type) [Fintype V] (G : SimpleGraph V) [Fintype G.edgeSet],
      SE_math_782216_q_Census.guard G → SE_math_782216_q_Census.BaseClaim G :=
by
  intro V _ G _ hpre hcard
  exact hpre.edgeFinset_card_eq_zero hcard

theorem repair_nonvacuous :
    (∃ (V : Type) (_ : Fintype V) (G : SimpleGraph V) (_ : Fintype G.edgeSet),
        G.edgeFinset.card = 0 ∧ SE_math_782216_q_Census.guard G) ∧
      (∃ (V : Type) (_ : Fintype V) (G : SimpleGraph V) (_ : Fintype G.edgeSet),
        G.edgeFinset.card = 0 ∧ ¬ SE_math_782216_q_Census.guard G) :=
by
  constructor
  · -- existence of an edgeless graph satisfying the guard (connected)
    refine ⟨PUnit, inferInstance, (⊥ : SimpleGraph PUnit), inferInstance, ?_, ?_⟩
    · simp
    · intro v w
      cases v
      cases w
      exact Relation.ReflTransGen.refl _
  · -- existence of an edgeless graph not satisfying the guard
    refine ⟨Bool, inferInstance, (⊥ : SimpleGraph Bool), inferInstance, ?_, ?_⟩
    · simp
    · intro hpre
      have hle : (Fintype.card Bool) ≤ 1 :=
        hpre.edgeFinset_card_eq_zero (by simp)
      have hle2 : (2 : Nat) ≤ 1 := by
        simpa using hle
      exact (Nat.not_succ_le_self 1) hle2

-- CANNOT: proof of the handshake lemma not provided
-- final_theorem : SE_math_782216_q_Census.SourceGoal

end SE_math_782216_q_Census
