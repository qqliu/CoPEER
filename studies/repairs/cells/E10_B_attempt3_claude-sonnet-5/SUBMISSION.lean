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

open Matrix SimpleGraph

/-- Helper: entries of the criterion via `Matrix.sum_apply`. -/
theorem criterion_apply {V : Type} [Fintype V] [DecidableEq V] (G : SimpleGraph V)
    [DecidableRel G.Adj] (i j : V) :
    criterion G i j = ∑ k ∈ Finset.range (Fintype.card V), (G.adjMatrix ℕ ^ k) i j := by
  unfold criterion
  rw [Matrix.sum_apply]

/-- Helper: a walk of length `k` from `i` to `j` shows the `k`-th power entry is nonzero. -/
theorem pow_apply_ne_zero_of_walk {V : Type} [Fintype V] [DecidableEq V] (G : SimpleGraph V)
    [DecidableRel G.Adj] {i j : V} (p : G.Walk i j) :
    (G.adjMatrix ℕ ^ p.length) i j ≠ 0 := by
  rw [G.adjMatrix_pow_apply_eq_card_walk]
  simp only [ne_eq, Nat.cast_eq_zero, Fintype.card_eq_zero_iff]
  intro h
  exact h.false ⟨p, rfl⟩

/-- Helper: reachability gives a witness index in range making the criterion nonzero. -/
theorem exists_index_of_reachable {V : Type} [Fintype V] [DecidableEq V] (G : SimpleGraph V)
    [DecidableRel G.Adj] {i j : V} (h : G.Reachable i j) :
    ∃ k ∈ Finset.range (Fintype.card V), (G.adjMatrix ℕ ^ k) i j ≠ 0 := by
  obtain ⟨p⟩ := h
  refine ⟨p.bypass.length, Finset.mem_range.mpr p.bypass_isPath.length_lt, ?_⟩
  exact pow_apply_ne_zero_of_walk G p.bypass

/-- Helper: a nonzero entry of the criterion produces a walk, hence reachability. -/
theorem reachable_of_criterion_ne_zero {V : Type} [Fintype V] [DecidableEq V] (G : SimpleGraph V)
    [DecidableRel G.Adj] {i j : V} (h : criterion G i j ≠ 0) : G.Reachable i j := by
  rw [criterion_apply] at h
  have hex : ∃ k ∈ Finset.range (Fintype.card V), (G.adjMatrix ℕ ^ k) i j ≠ 0 := by
    by_contra hc
    push_neg at hc
    exact h (Finset.sum_eq_zero hc)
  obtain ⟨k, -, hne⟩ := hex
  rw [G.adjMatrix_pow_apply_eq_card_walk] at hne
  simp only [ne_eq, Nat.cast_eq_zero, Fintype.card_eq_zero_iff, not_isEmpty_iff] at hne
  obtain ⟨p, -⟩ := hne.some
  exact ⟨p⟩

theorem repair_statement : ∀ (V : Type) [Fintype V] [DecidableEq V] (G : SimpleGraph V)
    [DecidableRel G.Adj], ∀ i j : V, SE_math_994847_q.criterion G i j = 0 → ¬ G.Reachable i j := by
  intro V _ _ G _ i j hz hr
  obtain ⟨k, hk, hne⟩ := exists_index_of_reachable G hr
  apply hne
  rw [criterion_apply] at hz
  exact (Finset.sum_eq_zero_iff.mp hz) k hk

theorem repair_nonvacuous : SE_math_994847_q.criterion (⊥ : SimpleGraph (Fin 2)) 0 0 ≠ 0 ∧
    SE_math_994847_q.criterion (⊥ : SimpleGraph (Fin 2)) 0 1 = 0 := by
  constructor
  · rw [criterion_apply]
    decide
  · rw [criterion_apply]
    decide

theorem final_theorem : ∀ (V : Type) [Fintype V] [DecidableEq V] [Nonempty V] (G : SimpleGraph V)
    [DecidableRel G.Adj], G.Connected ↔ ∀ i j : V, SE_math_994847_q.criterion G i j ≠ 0 := by
  intro V _ _ _ G _
  constructor
  · intro hconn i j hz
    exact (repair_statement V G i j hz) (hconn.preconnected i j)
  · intro hall
    exact { preconnected := fun i j => reachable_of_criterion_ne_zero G (hall i j)
            nonempty := ‹Nonempty V› }

end SE_math_994847_q
