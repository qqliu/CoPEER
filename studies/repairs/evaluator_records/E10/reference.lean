import defs_only
/- EVALUATOR-ONLY reference correction for E10 (original package: repair_entry_exact, line 202; repair, line 213). -/
namespace SE_math_994847_q.Ref

/-- Reference corrected criterion: `(I + A)^(n - 1)`. -/
def criterion {V : Type} [Fintype V] [DecidableEq V] (G : SimpleGraph V) [DecidableRel G.Adj] :
    Matrix V V ℕ := (1 + G.adjMatrix ℕ) ^ (Fintype.card V - 1)

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

theorem universal : ∀ (V : Type) [Fintype V] [DecidableEq V] (G : SimpleGraph V) [DecidableRel G.Adj], ∀ i j : V, criterion G i j = 0 → ¬ G.Reachable i j := by
  intro V _ _ G _ i j h hr
  exact (criterion_ne_zero_iff G i j).mpr hr h

end SE_math_994847_q.Ref
