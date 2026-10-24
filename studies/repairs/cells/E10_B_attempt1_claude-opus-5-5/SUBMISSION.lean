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

theorem one_add_adj_ne_zero {V : Type} [Fintype V] [DecidableEq V] (G : SimpleGraph V)
    [DecidableRel G.Adj] (i l : V) :
    (1 + G.adjMatrix ℕ) i l ≠ 0 ↔ (i = l ∨ G.Adj i l) := by
  rw [Matrix.add_apply, Matrix.one_apply, SimpleGraph.adjMatrix_apply]
  by_cases h1 : i = l <;> by_cases h2 : G.Adj i l <;> simp [h1, h2]

theorem pow_entry_ne_zero {V : Type} [Fintype V] [DecidableEq V] (G : SimpleGraph V)
    [DecidableRel G.Adj] (k : ℕ) : ∀ i j : V,
    ((1 + G.adjMatrix ℕ) ^ k) i j ≠ 0 ↔ ∃ p : G.Walk i j, p.length ≤ k := by
  induction k with
  | zero =>
    intro i j
    rw [pow_zero, Matrix.one_apply]
    constructor
    · intro h
      by_cases hij : i = j
      · subst hij; exact ⟨SimpleGraph.Walk.nil, le_refl _⟩
      · simp [hij] at h
    · rintro ⟨p, hp⟩
      have := p.eq_of_length_eq_zero (Nat.le_zero.mp hp)
      simp [this]
  | succ k ih =>
    intro i j
    rw [pow_succ', Matrix.mul_apply]
    constructor
    · intro h
      obtain ⟨l, -, hl⟩ : ∃ l ∈ Finset.univ, (1 + G.adjMatrix ℕ) i l *
          ((1 + G.adjMatrix ℕ) ^ k) l j ≠ 0 := by
        by_contra hc
        push_neg at hc
        exact h (Finset.sum_eq_zero hc)
      rcases mul_ne_zero_iff.mp hl with ⟨h1, h2⟩
      obtain ⟨q, hq⟩ := (ih l j).mp h2
      rcases (one_add_adj_ne_zero G i l).mp h1 with rfl | hadj
      · exact ⟨q, by omega⟩
      · exact ⟨SimpleGraph.Walk.cons hadj q, by simp; omega⟩
    · rintro ⟨p, hp⟩
      intro hs
      rw [Finset.sum_eq_zero_iff] at hs
      cases p with
      | nil =>
        have := hs i (Finset.mem_univ _)
        rcases Nat.mul_eq_zero.mp this with h | h
        · exact (one_add_adj_ne_zero G i i).mpr (Or.inl rfl) h
        · exact (ih i i).mpr ⟨SimpleGraph.Walk.nil, Nat.zero_le _⟩ h
      | @cons _ l _ hadj q =>
        have := hs l (Finset.mem_univ _)
        rcases Nat.mul_eq_zero.mp this with h | h
        · exact (one_add_adj_ne_zero G i l).mpr (Or.inr hadj) h
        · simp at hp
          exact (ih l j).mpr ⟨q, by omega⟩ h

theorem criterion_ne_zero_iff {V : Type} [Fintype V] [DecidableEq V] (G : SimpleGraph V)
    [DecidableRel G.Adj] (i j : V) : criterion G i j ≠ 0 ↔ G.Reachable i j := by
  unfold criterion
  rw [pow_entry_ne_zero]
  constructor
  · rintro ⟨p, -⟩; exact ⟨p⟩
  · rintro ⟨p⟩
    refine ⟨p.bypass, ?_⟩
    have := (p.bypass_isPath).length_lt
    omega

theorem repair_statement : ∀ (V : Type) [Fintype V] [DecidableEq V] (G : SimpleGraph V) [DecidableRel G.Adj], ∀ i j : V, SE_math_994847_q.criterion G i j = 0 → ¬ G.Reachable i j := by
  intro V _ _ G _ i j h hr
  exact (criterion_ne_zero_iff G i j).mpr hr h

theorem repair_nonvacuous : SE_math_994847_q.criterion (⊥ : SimpleGraph (Fin 2)) 0 0 ≠ 0 ∧ SE_math_994847_q.criterion (⊥ : SimpleGraph (Fin 2)) 0 1 = 0 := by
  refine ⟨(criterion_ne_zero_iff _ 0 0).mpr (SimpleGraph.Reachable.refl _), ?_⟩
  by_contra h
  have := (criterion_ne_zero_iff _ 0 1).mp h
  rw [SimpleGraph.reachable_bot] at this
  exact absurd this (by decide)

theorem final_theorem : ∀ (V : Type) [Fintype V] [DecidableEq V] [Nonempty V] (G : SimpleGraph V) [DecidableRel G.Adj], G.Connected ↔ ∀ i j : V, SE_math_994847_q.criterion G i j ≠ 0 := by
  intro V _ _ hne G _
  simp only [criterion_ne_zero_iff]
  rw [SimpleGraph.connected_iff]
  exact ⟨fun h => h.1, fun h => ⟨h, hne⟩⟩

end SE_math_994847_q
