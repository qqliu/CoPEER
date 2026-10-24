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
    Matrix V V ℕ := ∑ k ∈ Finset.range (Fintype.card V), (G.adjMatrix ℕ) ^ k

/-- The corrected entrywise claim for every finite simple graph (shape fixed). -/
def CorrectedEntrywise : Prop :=
  ∀ (V : Type) [Fintype V] [DecidableEq V] (G : SimpleGraph V) [DecidableRel G.Adj],
    ∀ i j : V, criterion G i j = 0 → ¬ G.Reachable i j
-- ===== END FIXED PART =====

theorem repair_statement :
    ∀ (V : Type) [Fintype V] [DecidableEq V] (G : SimpleGraph V) [DecidableRel G.Adj],
      ∀ i j : V, SE_math_994847_q.criterion G i j = 0 → ¬ G.Reachable i j := by
  intro V _ _ G _ i j hzero hreach
  obtain ⟨p, hp⟩ := hreach.exists_isPath
  have hlt : p.length < Fintype.card V := hp.length_lt
  have hne : (G.adjMatrix ℕ ^ p.length) i j ≠ 0 := by
    rw [G.adjMatrix_pow_apply_eq_card_walk]
    have : Nonempty { q : G.Walk i j | q.length = p.length } := ⟨⟨p, rfl⟩⟩
    exact (Fintype.card_pos_iff.mpr this).ne'
  have hmem : p.length ∈ Finset.range (Fintype.card V) := Finset.mem_range.mpr hlt
  rw [SE_math_994847_q.criterion, Matrix.sum_apply] at hzero
  have := (Finset.sum_eq_zero_iff.mp hzero) p.length hmem
  exact hne this

theorem repair_nonvacuous :
    SE_math_994847_q.criterion (⊥ : SimpleGraph (Fin 2)) 0 0 ≠ 0 ∧
      SE_math_994847_q.criterion (⊥ : SimpleGraph (Fin 2)) 0 1 = 0 := by
  constructor <;> simp [SE_math_994847_q.criterion, SimpleGraph.adjMatrix_bot, Fintype.card_fin,
    Finset.sum_range_succ]

theorem final_theorem :
    ∀ (V : Type) [Fintype V] [DecidableEq V] [Nonempty V] (G : SimpleGraph V) [DecidableRel G.Adj],
      G.Connected ↔ ∀ i j : V, SE_math_994847_q.criterion G i j ≠ 0 := by
  intro V _ _ _ G _
  constructor
  · intro hconn i j
    have hreach : G.Reachable i j := hconn.preconnected i j
    obtain ⟨p, hp⟩ := hreach.exists_isPath
    have hlt : p.length < Fintype.card V := hp.length_lt
    have hne : (G.adjMatrix ℕ ^ p.length) i j ≠ 0 := by
      rw [G.adjMatrix_pow_apply_eq_card_walk]
      have : Nonempty { q : G.Walk i j | q.length = p.length } := ⟨⟨p, rfl⟩⟩
      exact (Fintype.card_pos_iff.mpr this).ne'
    have hpos : 0 < (G.adjMatrix ℕ ^ p.length) i j := Nat.pos_of_ne_zero hne
    have hmem : p.length ∈ Finset.range (Fintype.card V) := Finset.mem_range.mpr hlt
    rw [SE_math_994847_q.criterion, Matrix.sum_apply]
    exact (Finset.sum_pos' (fun k _ => Nat.zero_le _) ⟨p.length, hmem, hpos⟩).ne'
  · intro hcrit
    refine ⟨fun i j => ?_⟩
    have hne : SE_math_994847_q.criterion G i j ≠ 0 := hcrit i j
    rw [SE_math_994847_q.criterion, Matrix.sum_apply] at hne
    obtain ⟨k, hkmem, hk⟩ := Finset.exists_ne_zero_of_sum_ne_zero hne
    rw [G.adjMatrix_pow_apply_eq_card_walk] at hk
    have : Nonempty { q : G.Walk i j | q.length = k } := Fintype.card_pos_iff.mp (Nat.pos_of_ne_zero hk)
    obtain ⟨⟨q, _⟩⟩ := this
    exact ⟨q⟩

end SE_math_994847_q
