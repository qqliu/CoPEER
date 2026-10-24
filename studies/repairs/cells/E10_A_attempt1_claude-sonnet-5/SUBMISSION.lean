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

/-- Helper: entries of `criterion` are given by summing walk counts. -/
theorem criterion_apply {V : Type} [Fintype V] [DecidableEq V] (G : SimpleGraph V)
    [DecidableRel G.Adj] (i j : V) :
    criterion G i j = ∑ k ∈ Finset.range (Fintype.card V),
      Fintype.card { p : G.Walk i j | p.length = k } := by
  unfold criterion
  simp [Finset.sum_apply, SimpleGraph.adjMatrix_pow_apply_eq_card_walk]

theorem criterion_eq_zero_iff {V : Type} [Fintype V] [DecidableEq V] (G : SimpleGraph V)
    [DecidableRel G.Adj] (i j : V) :
    criterion G i j = 0 ↔
      ∀ k ∈ Finset.range (Fintype.card V), (G.adjMatrix ℕ ^ k) i j = 0 := by
  unfold criterion
  rw [Finset.sum_apply]
  exact Finset.sum_eq_zero_iff_of_nonneg (fun _ _ => Nat.zero_le _)

theorem exists_path_of_reachable {V : Type} [Fintype V] [DecidableEq V] (G : SimpleGraph V)
    [DecidableRel G.Adj] {i j : V} (h : G.Reachable i j) :
    ∃ p : G.Walk i j, p.IsPath ∧ p.length < Fintype.card V := by
  obtain ⟨w⟩ := h
  refine ⟨w.toPath.1, w.toPath.2, ?_⟩
  exact w.toPath.2.length_lt

-- ===== OBLIGATIONS =====

theorem repair_statement : ∀ (V : Type) [Fintype V] [DecidableEq V] (G : SimpleGraph V) [DecidableRel G.Adj], ∀ i j : V, SE_math_994847_q.criterion G i j = 0 → ¬ G.Reachable i j := by
  intro V _ _ G _ i j hz hreach
  obtain ⟨p, hp, hlt⟩ := exists_path_of_reachable G hreach
  rw [criterion_eq_zero_iff] at hz
  have h0 := hz p.length (Finset.mem_range.mpr hlt)
  rw [SimpleGraph.adjMatrix_pow_apply_eq_card_walk] at h0
  have : Nonempty { q : G.Walk i j | q.length = p.length } := ⟨⟨p, rfl⟩⟩
  rw [Fintype.card_eq_zero_iff] at h0
  exact h0.false ⟨p, rfl⟩

theorem repair_nonvacuous : SE_math_994847_q.criterion (⊥ : SimpleGraph (Fin 2)) 0 0 ≠ 0 ∧ SE_math_994847_q.criterion (⊥ : SimpleGraph (Fin 2)) 0 1 = 0 := by
  constructor
  · decide
  · decide

theorem final_theorem : ∀ (V : Type) [Fintype V] [DecidableEq V] [Nonempty V] (G : SimpleGraph V) [DecidableRel G.Adj], G.Connected ↔ ∀ i j : V, SE_math_994847_q.criterion G i j ≠ 0 := by
  intro V _ _ _ G _
  constructor
  · intro hconn i j
    have hreach : G.Reachable i j := hconn.preconnected i j
    obtain ⟨p, hp, hlt⟩ := exists_path_of_reachable G hreach
    rw [criterion_apply]
    intro hsum
    rw [Finset.sum_eq_zero_iff_of_nonneg (fun _ _ => Nat.zero_le _)] at hsum
    have h0 := hsum p.length (Finset.mem_range.mpr hlt)
    rw [Fintype.card_eq_zero_iff] at h0
    exact h0.false ⟨p, rfl⟩
  · intro hall
    constructor
    · intro i j
      have hz := hall i j
      rw [criterion_eq_zero_iff] at hz
      push_neg at hz
      obtain ⟨k, hk, hne⟩ := hz
      rw [SimpleGraph.adjMatrix_pow_apply_eq_card_walk] at hne
      rw [Fintype.card_ne_zero_iff] at hne
      obtain ⟨q, hq⟩ := hne
      exact ⟨q.1⟩
    · infer_instance

end SE_math_994847_q
