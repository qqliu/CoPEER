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

theorem key_walk {V : Type} [Fintype V] [DecidableEq V] (G : SimpleGraph V) [DecidableRel G.Adj]
    (k : ℕ) : ∀ i j : V, ((1 + G.adjMatrix ℕ) ^ k) i j ≠ 0 ↔ ∃ p : G.Walk i j, p.length ≤ k := by
  induction k with
  | zero =>
    intro i j
    rw [pow_zero, Matrix.one_apply]
    constructor
    · intro h
      by_cases hij : i = j
      · subst hij; exact ⟨.nil, by simp⟩
      · simp [hij] at h
    · rintro ⟨p, hp⟩
      have h0 : p.length = 0 := by omega
      have := SimpleGraph.Walk.eq_of_length_eq_zero h0
      simp [this]
  | succ k ih =>
    intro i j
    rw [pow_succ', Matrix.add_mul, Matrix.one_mul, Matrix.add_apply, Matrix.mul_apply]
    have hs : (∑ l, G.adjMatrix ℕ i l * ((1 + G.adjMatrix ℕ) ^ k) l j ≠ 0) ↔
        ∃ l, G.Adj i l ∧ ((1 + G.adjMatrix ℕ) ^ k) l j ≠ 0 := by
      rw [Ne, Finset.sum_eq_zero_iff]
      push_neg
      simp [SimpleGraph.adjMatrix_apply]
    constructor
    · intro h
      by_cases h1 : ((1 + G.adjMatrix ℕ) ^ k) i j = 0
      · rw [h1, zero_add] at h
        obtain ⟨l, hadj, hM⟩ := hs.1 h
        obtain ⟨q, hq⟩ := (ih l j).1 hM
        exact ⟨.cons hadj q, by simp; omega⟩
      · obtain ⟨p, hp⟩ := (ih i j).1 h1
        exact ⟨p, by omega⟩
    · rintro ⟨p, hp⟩
      cases p with
      | nil =>
        have := (ih i i).2 ⟨.nil, by simp⟩
        omega
      | cons h q =>
        have h2 := (ih _ j).2 ⟨q, by simp at hp; omega⟩
        have h3 := hs.2 ⟨_, h, h2⟩
        omega

theorem reach_crit {V : Type} [Fintype V] [DecidableEq V] (G : SimpleGraph V) [DecidableRel G.Adj]
    (i j : V) (h : G.Reachable i j) : criterion G i j ≠ 0 := by
  obtain ⟨p⟩ := h
  have := p.bypass_isPath.length_lt
  exact (key_walk G _ i j).2 ⟨p.bypass, by omega⟩

theorem repair_statement : ∀ (V : Type) [Fintype V] [DecidableEq V] (G : SimpleGraph V) [DecidableRel G.Adj], ∀ i j : V, SE_math_994847_q.criterion G i j = 0 → ¬ G.Reachable i j := by
  intro V _ _ G _ i j h hr
  exact reach_crit G i j hr h

theorem repair_nonvacuous : SE_math_994847_q.criterion (⊥ : SimpleGraph (Fin 2)) 0 0 ≠ 0 ∧ SE_math_994847_q.criterion (⊥ : SimpleGraph (Fin 2)) 0 1 = 0 := by
  simp [criterion, SimpleGraph.adjMatrix_apply, Matrix.one_apply]

theorem final_theorem : ∀ (V : Type) [Fintype V] [DecidableEq V] [Nonempty V] (G : SimpleGraph V) [DecidableRel G.Adj], G.Connected ↔ ∀ i j : V, SE_math_994847_q.criterion G i j ≠ 0 := by
  intro V _ _ _ G _
  constructor
  · intro hc i j
    exact reach_crit G i j (hc.preconnected i j)
  · intro h
    rw [SimpleGraph.connected_iff]
    refine ⟨fun i j => ?_, inferInstance⟩
    obtain ⟨p, _⟩ := (key_walk G _ i j).1 (h i j)
    exact ⟨p⟩

end SE_math_994847_q
