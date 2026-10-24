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

-- The following obligations are required.

theorem repair_statement :
    ∀ (V : Type) [Fintype V] [DecidableEq V] (G : SimpleGraph V) [DecidableRel G.Adj],
      ∀ i j : V, SE_math_994847_q.criterion G i j = 0 → ¬ G.Reachable i j :=
by
  intro V _ _ G _ i j hzero hreach
  -- We obtain a walk from the reachability hypothesis.
  rcases (SimpleGraph.reachable_iff_exists_walk).1 hreach with ⟨p⟩
  -- Erase cycles to get a simple walk whose length is bounded by the number of vertices.
  let p' := p.eraseCycles
  have hlen_le : p'.length ≤ Fintype.card V - 1 := by
    have : p'.length ≤ Fintype.card V := p'.length_le_card
    have hpos : 0 < Fintype.card V := by
      haveI : Nonempty V := Classical.choice (inferInstance : Inhabited V)
      exact Nat.succ_le_iff.mpr (Nat.succ_pos _)
    exact Nat.le_of_lt_succ (Nat.sub_lt (Nat.succ_le_of_lt hpos) (Nat.succ_pos _))
  -- Count walks of the exact length `p'.length`.
  have hcount :
      (G.adjMatrix ℕ) ^ p'.length i j =
        Fintype.card (G.Walk.ofLength p'.length i j) := by
    simpa using G.adjMatrix_pow_eq_card_walk (n := p'.length) i j
  have hposA : 0 < (G.adjMatrix ℕ) ^ p'.length i j := by
    have : (p' : G.Walk i j) ∈ (G.Walk.ofLength p'.length i j) := by
      exact p'.mem_ofLength
    have : 0 < Fintype.card (G.Walk.ofLength p'.length i j) := by
      apply Nat.pos_of_ne_zero
      intro hzero'
      have : (G.Walk.ofLength p'.length i j).Nonempty := ⟨⟨p'⟩⟩
      exact this.elim (by simpa [hzero'] using this)
    simpa [hcount] using this
  -- The entry of the criterion matrix dominates this positive term.
  have hpos : 0 < (1 + G.adjMatrix ℕ) ^ (Fintype.card V - 1) i j := by
    have hcoeff : (Nat.choose (Fintype.card V - 1) p'.length) ≠ 0 := by
      apply Nat.choose_pos
      exact hlen_le
    have hterm : 0 < (Nat.choose (Fintype.card V - 1) p'.length) * ((G.adjMatrix ℕ) ^ p'.length i j) := by
      have : 0 < (G.adjMatrix ℕ) ^ p'.length i j := hposA
      exact Nat.mul_pos (Nat.pos_of_ne_zero (by
        intro h; have := Nat.eq_zero_of_choose_eq_zero h; exact False.elim (by decide))) this
    have hsum :
        (1 + G.adjMatrix ℕ) ^ (Fintype.card V - 1) i j =
          ∑ k in Finset.range (Fintype.card V), Nat.choose (Fintype.card V - 1) k *
            ((G.adjMatrix ℕ) ^ k) i j := by
      simpa [Matrix.one_add_pow] using rfl
    have : (∑ k in Finset.range (Fintype.card V),
        Nat.choose (Fintype.card V - 1) k *
          ((G.adjMatrix ℕ) ^ k) i j) ≥
        (Nat.choose (Fintype.card V - 1) p'.length) *
          ((G.adjMatrix ℕ) ^ p'.length i j) := by
      apply Finset.le_sum_of_subset_of_nonneg
      · intro x hx; exact Finset.mem_range.mpr (Nat.lt_of_lt_of_le (Nat.lt_succ_self _) (Nat.le_of_lt_succ (Nat.sub_lt (Nat.succ_le_of_lt (by decide)) (Nat.succ_pos _))))
      · intro x hx; exact Nat.zero_le _
    have : 0 < (∑ k in Finset.range (Fintype.card V),
        Nat.choose (Fintype.card V - 1) k *
          ((G.adjMatrix ℕ) ^ k) i j) := lt_of_lt_of_le hterm this
    simpa [hsum] using this
  have : (SE_math_994847_q.criterion G i j) ≠ 0 := by
    intro hzero'
    have : 0 < (SE_math_994847_q.criterion G i j) := hpos
    simpa [hzero'] using this
  exact this hzero

theorem repair_nonvacuous :
    SE_math_994847_q.criterion (⊥ : SimpleGraph (Fin 2)) 0 0 ≠ 0 ∧
      SE_math_994847_q.criterion (⊥ : SimpleGraph (Fin 2)) 0 1 = 0 :=
by
  have hcard : Fintype.card (Fin 2) = 2 := by decide
  simp [criterion, hcard] 

-- CANNOT: proof of final theorem requires extensive combinatorial matrix lemmas beyond current scope
