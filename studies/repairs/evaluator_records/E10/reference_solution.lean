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

theorem one_add_pow_entry_ne_zero_iff {V : Type} [Fintype V] [DecidableEq V] (G : SimpleGraph V)
    [DecidableRel G.Adj] (k : ℕ) (i j : V) :
    ((1 + G.adjMatrix ℕ) ^ k) i j ≠ 0 ↔ ∃ p : G.Walk i j, p.length ≤ k := by
  induction k generalizing i j with
  | zero =>
    rw [pow_zero]
    constructor
    · intro h
      by_cases hij : i = j
      · subst hij; exact ⟨SimpleGraph.Walk.nil, Nat.le_refl _⟩
      · exact absurd (Matrix.one_apply_ne hij) h
    · rintro ⟨p, hp⟩
      have hij : i = j := SimpleGraph.Walk.eq_of_length_eq_zero (Nat.le_zero.mp hp)
      subst hij
      rw [Matrix.one_apply_eq]
      exact one_ne_zero
  | succ k ih =>
    rw [pow_succ', Matrix.mul_apply]
    constructor
    · intro h
      have hex : ∃ l, (1 + G.adjMatrix ℕ) i l * ((1 + G.adjMatrix ℕ) ^ k) l j ≠ 0 := by
        by_contra hcon
        exact h (Finset.sum_eq_zero (fun l _ => by
          by_contra hne
          exact hcon ⟨l, hne⟩))
      obtain ⟨l, hl⟩ := hex
      have h1 : (1 + G.adjMatrix ℕ) i l ≠ 0 := left_ne_zero_of_mul hl
      have h2 : ((1 + G.adjMatrix ℕ) ^ k) l j ≠ 0 := right_ne_zero_of_mul hl
      obtain ⟨p, hp⟩ := (ih l j).mp h2
      by_cases hil : i = l
      · subst hil; exact ⟨p, Nat.le_succ_of_le hp⟩
      · have hadj : G.Adj i l := by
          by_contra hna
          apply h1
          rw [Matrix.add_apply, Matrix.one_apply_ne hil, SimpleGraph.adjMatrix_apply, if_neg hna]
          omega
        exact ⟨SimpleGraph.Walk.cons hadj p, by rw [SimpleGraph.Walk.length_cons]; omega⟩
    · rintro ⟨p, hp⟩
      have hex : ∃ l, (1 + G.adjMatrix ℕ) i l ≠ 0 ∧ ∃ q : G.Walk l j, q.length ≤ k := by
        cases p with
        | nil =>
          refine ⟨_, ?_, SimpleGraph.Walk.nil, Nat.zero_le _⟩
          rw [Matrix.add_apply, Matrix.one_apply_eq]; omega
        | cons h q =>
          refine ⟨_, ?_, q, ?_⟩
          · rw [Matrix.add_apply, SimpleGraph.adjMatrix_apply, if_pos h]; omega
          · rw [SimpleGraph.Walk.length_cons] at hp; omega
      obtain ⟨l, hl1, q, hq⟩ := hex
      have hl2 : ((1 + G.adjMatrix ℕ) ^ k) l j ≠ 0 := (ih l j).mpr ⟨q, hq⟩
      intro hsum
      exact (mul_ne_zero hl1 hl2) ((Finset.sum_eq_zero_iff.mp hsum) l (Finset.mem_univ l))

theorem criterion_ne_zero_iff {V : Type} [Fintype V] [DecidableEq V] (G : SimpleGraph V)
    [DecidableRel G.Adj] (i j : V) : criterion G i j ≠ 0 ↔ G.Reachable i j := by
  unfold criterion
  rw [one_add_pow_entry_ne_zero_iff]
  constructor
  · rintro ⟨p, _⟩; exact ⟨p⟩
  · intro hr
    obtain ⟨p, hp⟩ := hr.exists_isPath
    exact ⟨p, Nat.le_sub_one_of_lt hp.length_lt⟩

-- ===== OBLIGATIONS: keep the names and statements; replace each `sorry` by a proof =====
/-- Universal: a zero entry of the corrected criterion certifies that the two vertices are not joined by
a walk, for every finite simple graph. -/
theorem repair_statement : ∀ (V : Type) [Fintype V] [DecidableEq V] (G : SimpleGraph V) [DecidableRel G.Adj], ∀ i j : V, SE_math_994847_q.criterion G i j = 0 → ¬ G.Reachable i j := by
  intro V _ _ G _ i j h hr
  exact (criterion_ne_zero_iff G i j).mpr hr h

/-- Non-vacuity: the criterion is not a constant matrix (on the edgeless graph with two vertices the
diagonal entry is nonzero and the off-diagonal entry is zero). -/
theorem repair_nonvacuous : SE_math_994847_q.criterion (⊥ : SimpleGraph (Fin 2)) 0 0 ≠ 0 ∧ SE_math_994847_q.criterion (⊥ : SimpleGraph (Fin 2)) 0 1 = 0 := ⟨by unfold criterion; decide +kernel, by unfold criterion; decide +kernel⟩

/-- The source's theorem (stored source line 0001) with the corrected criterion: on a nonempty vertex
set, `G` is connected iff the criterion has no zero entry. If you cannot prove it, replace this declaration
(this doc comment included) by the single line `-- CANNOT: <reason>`. -/
theorem final_theorem : ∀ (V : Type) [Fintype V] [DecidableEq V] [Nonempty V] (G : SimpleGraph V) [DecidableRel G.Adj], G.Connected ↔ ∀ i j : V, SE_math_994847_q.criterion G i j ≠ 0 := by
  intro V _ _ _ G _
  rw [SimpleGraph.connected_iff]
  constructor
  · intro h i j
    exact (criterion_ne_zero_iff G i j).mpr (h.1 i j)
  · intro h
    exact ⟨fun i j => (criterion_ne_zero_iff G i j).mp (h i j), inferInstance⟩
-- ===== END OBLIGATIONS =====
end SE_math_994847_q
