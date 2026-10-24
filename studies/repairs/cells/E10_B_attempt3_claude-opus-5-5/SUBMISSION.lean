import defs_only
/-!
Record E10: correction template.
Fill the ONE hole `«HOLE»` in the FIXED PART (nothing else in the fixed part may change), then prove
the OBLIGATIONS below with exactly these names and statements. Helper lemmas may be added between the
fixed part and the obligations, inside the namespace. Import nothing else.
-/
namespace SE_math_994847_q

-- ===== FIXED PART: only the hole «HOLE» may be edited =====
/-- The corrected matrix criterion: a matrix over ℕ computed from the adjacency matrix `G.adjMatrix ℕ` and
the vertex count `Fintype.card V`, whose zero entries certify unreachability (the source uses
`G.adjMatrix ℕ ^ (Fintype.card V - 1)`). The hole must be a matrix expression in `G.adjMatrix ℕ` and
`Fintype.card V` (powers, sums, `1`); it may not mention `Reachable`, `Connected`, `Walk`, `if`/`match`. -/
def criterion {V : Type} [Fintype V] [DecidableEq V] (G : SimpleGraph V) [DecidableRel G.Adj] :
    Matrix V V ℕ := (1 + G.adjMatrix ℕ) ^ (Fintype.card V - 1)

/-- The corrected entrywise claim for every finite simple graph (shape fixed). -/
def CorrectedEntrywise : Prop :=
  ∀ (V : Type) [Fintype V] [DecidableEq V] (G : SimpleGraph V) [DecidableRel G.Adj],
    ∀ i j : V, criterion G i j = 0 → ¬ G.Reachable i j
-- ===== END FIXED PART =====

theorem walk_pos {V : Type} [Fintype V] [DecidableEq V] (G : SimpleGraph V) [DecidableRel G.Adj] :
    ∀ (k : ℕ) (i j : V) (p : G.Walk i j), p.length ≤ k → ((1 + G.adjMatrix ℕ) ^ k) i j ≠ 0 := by
  intro k
  induction k with
  | zero =>
    intro i j p hp
    cases p with
    | nil => simp
    | cons h q => simp at hp
  | succ k ih =>
    intro i j p hp
    rw [pow_succ', Matrix.mul_apply]
    intro hs
    have hz := Finset.sum_eq_zero_iff.mp hs
    cases p with
    | nil =>
      have := hz i (Finset.mem_univ _)
      rcases mul_eq_zero.mp this with h | h
      · simp [Matrix.add_apply, SimpleGraph.adjMatrix_apply] at h
      · exact ih i i SimpleGraph.Walk.nil (by simp) h
    | @cons _ i' _ hadj q =>
      have := hz i' (Finset.mem_univ _)
      rcases mul_eq_zero.mp this with h | h
      · simp [Matrix.add_apply, SimpleGraph.adjMatrix_apply, hadj] at h
      · simp at hp
        exact ih i' j q (by omega) h

theorem pos_reach {V : Type} [Fintype V] [DecidableEq V] (G : SimpleGraph V) [DecidableRel G.Adj] :
    ∀ (k : ℕ) (i j : V), ((1 + G.adjMatrix ℕ) ^ k) i j ≠ 0 → G.Reachable i j := by
  intro k
  induction k with
  | zero =>
    intro i j h
    by_contra hr
    have hij : i ≠ j := fun e => hr (e ▸ SimpleGraph.Reachable.refl i)
    simp [Matrix.one_apply, hij] at h
  | succ k ih =>
    intro i j h
    rw [pow_succ', Matrix.mul_apply] at h
    obtain ⟨l, -, hl⟩ := Finset.exists_ne_zero_of_sum_ne_zero h
    have h1 := left_ne_zero_of_mul hl
    have h2 := right_ne_zero_of_mul hl
    refine SimpleGraph.Reachable.trans ?_ (ih l j h2)
    by_cases e : i = l
    · subst e; rfl
    · have : G.Adj i l := by
        by_contra hn
        simp [Matrix.add_apply, SimpleGraph.adjMatrix_apply, Matrix.one_apply, e, hn] at h1
      exact this.reachable

theorem reach_pos {V : Type} [Fintype V] [DecidableEq V] (G : SimpleGraph V) [DecidableRel G.Adj]
    (i j : V) (h : G.Reachable i j) : criterion G i j ≠ 0 := by
  obtain ⟨p⟩ := h
  have hl := (p.bypass_isPath).length_lt
  exact walk_pos G _ i j p.bypass (by omega)

theorem repair_statement : ∀ (V : Type) [Fintype V] [DecidableEq V] (G : SimpleGraph V) [DecidableRel G.Adj], ∀ i j : V, SE_math_994847_q.criterion G i j = 0 → ¬ G.Reachable i j := by
  intro V _ _ G _ i j h hr
  exact reach_pos G i j hr h

theorem repair_nonvacuous : SE_math_994847_q.criterion (⊥ : SimpleGraph (Fin 2)) 0 0 ≠ 0 ∧ SE_math_994847_q.criterion (⊥ : SimpleGraph (Fin 2)) 0 1 = 0 := by
  simp [criterion, Matrix.add_apply, SimpleGraph.adjMatrix_apply, Matrix.one_apply]

theorem final_theorem : ∀ (V : Type) [Fintype V] [DecidableEq V] [Nonempty V] (G : SimpleGraph V) [DecidableRel G.Adj], G.Connected ↔ ∀ i j : V, SE_math_994847_q.criterion G i j ≠ 0 := by
  intro V _ _ _ G _
  constructor
  · intro hc i j
    exact reach_pos G i j (hc.preconnected i j)
  · intro h
    exact { preconnected := fun i j => pos_reach G _ i j (h i j), nonempty := inferInstance }

end SE_math_994847_q
