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

lemma M_pos {V : Type} [Fintype V] [DecidableEq V] (G : SimpleGraph V) [DecidableRel G.Adj]
    (i l : V) (h : i = l ∨ G.Adj i l) : 0 < (1 + G.adjMatrix ℕ) i l := by
  rcases h with rfl | h
  · simp [Matrix.one_apply]
  · simp [Matrix.one_apply, SimpleGraph.adjMatrix_apply, h]

lemma M_ne {V : Type} [Fintype V] [DecidableEq V] (G : SimpleGraph V) [DecidableRel G.Adj]
    (i l : V) (h : (1 + G.adjMatrix ℕ) i l ≠ 0) : i = l ∨ G.Adj i l := by
  by_contra hc
  push_neg at hc
  apply h
  simp [Matrix.one_apply, SimpleGraph.adjMatrix_apply, hc.1, hc.2]

lemma step_pos {V : Type} [Fintype V] [DecidableEq V] (G : SimpleGraph V) [DecidableRel G.Adj]
    (k : ℕ) (i l j : V) (h1 : i = l ∨ G.Adj i l) (h2 : 0 < ((1 + G.adjMatrix ℕ) ^ k) l j) :
    0 < ((1 + G.adjMatrix ℕ) ^ (k + 1)) i j := by
  rw [pow_succ', Matrix.mul_apply]
  have h3 := M_pos G i l h1
  have : (1 + G.adjMatrix ℕ) i l * ((1 + G.adjMatrix ℕ) ^ k) l j ≤
      ∑ x, (1 + G.adjMatrix ℕ) i x * ((1 + G.adjMatrix ℕ) ^ k) x j :=
    Finset.single_le_sum (f := fun x => (1 + G.adjMatrix ℕ) i x * ((1 + G.adjMatrix ℕ) ^ k) x j)
      (fun _ _ => Nat.zero_le _) (Finset.mem_univ l)
  exact lt_of_lt_of_le (Nat.mul_pos h3 h2) this

lemma diag_pos {V : Type} [Fintype V] [DecidableEq V] (G : SimpleGraph V) [DecidableRel G.Adj]
    (i : V) : ∀ k : ℕ, 0 < ((1 + G.adjMatrix ℕ : Matrix V V ℕ) ^ k) i i := by
  intro k
  induction k with
  | zero => simp
  | succ k ih => exact step_pos G k i i i (Or.inl rfl) ih

lemma walk_pos {V : Type} [Fintype V] [DecidableEq V] (G : SimpleGraph V) [DecidableRel G.Adj]
    {i j : V} (p : G.Walk i j) : ∀ k, p.length ≤ k → 0 < ((1 + G.adjMatrix ℕ) ^ k) i j := by
  induction p with
  | nil => intro k _; exact diag_pos G _ k
  | cons h p ih =>
    intro k hk
    simp only [SimpleGraph.Walk.length_cons] at hk
    obtain ⟨k', rfl⟩ : ∃ k', k = k' + 1 := ⟨k - 1, by omega⟩
    exact step_pos G k' _ _ _ (Or.inr h) (ih k' (by omega))

lemma ne_reach {V : Type} [Fintype V] [DecidableEq V] (G : SimpleGraph V) [DecidableRel G.Adj] :
    ∀ (k : ℕ) (i j : V), ((1 + G.adjMatrix ℕ : Matrix V V ℕ) ^ k) i j ≠ 0 → G.Reachable i j := by
  intro k
  induction k with
  | zero =>
    intro i j h
    by_cases hij : i = j
    · subst hij; rfl
    · simp [Matrix.one_apply, hij] at h
  | succ k ih =>
    intro i j h
    rw [pow_succ', Matrix.mul_apply] at h
    obtain ⟨l, _, hl⟩ := Finset.exists_ne_zero_of_sum_ne_zero h
    rw [mul_ne_zero_iff] at hl
    have h1 : G.Reachable i l := by
      rcases M_ne G i l hl.1 with rfl | ha
      · rfl
      · exact ha.reachable
    exact h1.trans (ih l j hl.2)

lemma reach_pos {V : Type} [Fintype V] [DecidableEq V] (G : SimpleGraph V) [DecidableRel G.Adj]
    (i j : V) (h : G.Reachable i j) : criterion G i j ≠ 0 := by
  obtain ⟨p⟩ := h
  have hp := (p.bypass_isPath).length_lt
  exact Nat.pos_iff_ne_zero.mp (walk_pos G p.bypass _ (by omega))

theorem repair_statement : ∀ (V : Type) [Fintype V] [DecidableEq V] (G : SimpleGraph V) [DecidableRel G.Adj], ∀ i j : V, SE_math_994847_q.criterion G i j = 0 → ¬ G.Reachable i j := by
  intro V _ _ G _ i j h hr
  exact reach_pos G i j hr h

theorem repair_nonvacuous : SE_math_994847_q.criterion (⊥ : SimpleGraph (Fin 2)) 0 0 ≠ 0 ∧ SE_math_994847_q.criterion (⊥ : SimpleGraph (Fin 2)) 0 1 = 0 := by
  simp [criterion, Matrix.one_apply, SimpleGraph.adjMatrix_apply]

theorem final_theorem : ∀ (V : Type) [Fintype V] [DecidableEq V] [Nonempty V] (G : SimpleGraph V) [DecidableRel G.Adj], G.Connected ↔ ∀ i j : V, SE_math_994847_q.criterion G i j ≠ 0 := by
  intro V _ _ _ G _
  constructor
  · intro hc i j
    exact reach_pos G i j (hc.preconnected i j)
  · intro h
    rw [SimpleGraph.connected_iff]
    exact ⟨fun i j => ne_reach G (Fintype.card V - 1) i j (h i j), inferInstance⟩

end SE_math_994847_q
