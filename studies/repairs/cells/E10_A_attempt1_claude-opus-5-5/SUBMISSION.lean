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

lemma oneA_ne_zero_iff {V : Type} [Fintype V] [DecidableEq V] (G : SimpleGraph V)
    [DecidableRel G.Adj] (i j : V) :
    (1 + G.adjMatrix ℕ) i j ≠ 0 ↔ (i = j ∨ G.Adj i j) := by
  rw [Matrix.add_apply, Matrix.one_apply, SimpleGraph.adjMatrix_apply]
  by_cases h1 : i = j <;> by_cases h2 : G.Adj i j <;> simp [h1, h2]

lemma pow_succ_ne_zero_iff {V : Type} [Fintype V] [DecidableEq V] (M : Matrix V V ℕ)
    (k : ℕ) (i j : V) :
    (M ^ (k+1)) i j ≠ 0 ↔ ∃ l, M i l ≠ 0 ∧ (M ^ k) l j ≠ 0 := by
  rw [pow_succ', Matrix.mul_apply]
  constructor
  · intro h
    obtain ⟨l, _, hl⟩ := Finset.exists_ne_zero_of_sum_ne_zero h
    exact ⟨l, mul_ne_zero_iff.mp hl⟩
  · rintro ⟨l, h1, h2⟩ h
    rw [Finset.sum_eq_zero_iff] at h
    exact mul_ne_zero h1 h2 (h l (Finset.mem_univ _))

lemma reach_of_ne_zero {V : Type} [Fintype V] [DecidableEq V] (G : SimpleGraph V)
    [DecidableRel G.Adj] (k : ℕ) : ∀ i j : V, ((1 + G.adjMatrix ℕ) ^ k) i j ≠ 0 → G.Reachable i j := by
  induction k with
  | zero =>
    intro i j h
    rw [pow_zero, Matrix.one_apply] at h
    by_cases hij : i = j
    · subst hij; exact SimpleGraph.Reachable.refl _
    · simp [hij] at h
  | succ k ih =>
    intro i j h
    obtain ⟨l, h1, h2⟩ := (pow_succ_ne_zero_iff _ k i j).mp h
    have r2 := ih l j h2
    rcases (oneA_ne_zero_iff G i l).mp h1 with h | h
    · subst h; exact r2
    · exact h.reachable.trans r2

lemma ne_zero_of_walk {V : Type} [Fintype V] [DecidableEq V] (G : SimpleGraph V)
    [DecidableRel G.Adj] (k : ℕ) : ∀ i j : V, ∀ p : G.Walk i j, p.length ≤ k →
      ((1 + G.adjMatrix ℕ) ^ k) i j ≠ 0 := by
  induction k with
  | zero =>
    intro i j p hp
    have := SimpleGraph.Walk.eq_of_length_eq_zero (by omega : p.length = 0)
    subst this
    simp
  | succ k ih =>
    intro i j p hp
    rw [pow_succ_ne_zero_iff]
    cases p with
    | nil =>
      exact ⟨i, (oneA_ne_zero_iff G i i).mpr (Or.inl rfl),
        ih i i SimpleGraph.Walk.nil (by simp)⟩
    | cons h q =>
      rename_i l
      refine ⟨l, (oneA_ne_zero_iff G _ _).mpr (Or.inr h), ih _ _ q ?_⟩
      simp at hp; omega

theorem repair_statement : ∀ (V : Type) [Fintype V] [DecidableEq V] (G : SimpleGraph V) [DecidableRel G.Adj], ∀ i j : V, SE_math_994847_q.criterion G i j = 0 → ¬ G.Reachable i j := by
  intro V _ _ G _ i j h r
  obtain ⟨p⟩ := r
  have hl := (p.toPath).2.length_lt
  exact ne_zero_of_walk G _ i j p.toPath.1 (by omega) h

theorem repair_nonvacuous : SE_math_994847_q.criterion (⊥ : SimpleGraph (Fin 2)) 0 0 ≠ 0 ∧ SE_math_994847_q.criterion (⊥ : SimpleGraph (Fin 2)) 0 1 = 0 := by
  have h : SE_math_994847_q.criterion (⊥ : SimpleGraph (Fin 2)) = 1 := by
    unfold criterion
    rw [Fintype.card_fin]
    ext a b
    simp [Matrix.add_apply, SimpleGraph.adjMatrix_apply]
  rw [h]
  simp

theorem final_theorem : ∀ (V : Type) [Fintype V] [DecidableEq V] [Nonempty V] (G : SimpleGraph V) [DecidableRel G.Adj], G.Connected ↔ ∀ i j : V, SE_math_994847_q.criterion G i j ≠ 0 := by
  intro V _ _ _ G _
  constructor
  · intro hc i j h
    exact repair_statement V G i j h (hc.preconnected i j)
  · intro h
    rw [SimpleGraph.connected_iff]
    exact ⟨fun i j => reach_of_ne_zero G _ i j (h i j), inferInstance⟩

end SE_math_994847_q
