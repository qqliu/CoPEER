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

/-- The criterion, entrywise, is the sum of walk-count-matrix entries over lengths `0, …, n-1`. -/
theorem criterion_apply {V : Type} [Fintype V] [DecidableEq V] (G : SimpleGraph V)
    [DecidableRel G.Adj] (i j : V) :
    criterion G i j = ∑ k ∈ Finset.range (Fintype.card V), (G.adjMatrix ℕ ^ k) i j := by
  simp [criterion, Matrix.sum_apply]

/-- If `i` and `j` are joined by a walk, the criterion entry at `(i, j)` is nonzero: the shortest
walk (a path) has length `< Fintype.card V`, and that length contributes a positive term to the
criterion sum. -/
theorem criterion_ne_zero_of_reachable {V : Type} [Fintype V] [DecidableEq V] (G : SimpleGraph V)
    [DecidableRel G.Adj] {i j : V} (h : G.Reachable i j) : criterion G i j ≠ 0 := by
  obtain ⟨p⟩ := h
  set q : G.Walk i j := (p.toPath : G.Walk i j) with hq
  have hpath : q.IsPath := p.toPath.2
  have hlt : q.length < Fintype.card V := hpath.length_lt
  have hcardpos : 0 < Fintype.card {w : G.Walk i j | w.length = q.length} := by
    rw [Fintype.card_pos_iff]
    exact ⟨⟨q, rfl⟩⟩
  have hterm : (G.adjMatrix ℕ ^ q.length) i j ≠ 0 := by
    rw [SimpleGraph.adjMatrix_pow_apply_eq_card_walk]
    simp only [ne_eq, Nat.cast_eq_zero]
    exact hcardpos.ne'
  rw [criterion_apply]
  intro hz
  exact hterm (Finset.sum_eq_zero_iff.mp hz q.length (Finset.mem_range.mpr hlt))

/-- If the criterion entry at `(i, j)` is nonzero, some length `k < Fintype.card V` gives a
nonzero walk-count entry, i.e. a walk of length `k` from `i` to `j`, so `i` and `j` are reachable. -/
theorem reachable_of_criterion_ne_zero {V : Type} [Fintype V] [DecidableEq V] (G : SimpleGraph V)
    [DecidableRel G.Adj] {i j : V} (h : criterion G i j ≠ 0) : G.Reachable i j := by
  rw [criterion_apply] at h
  obtain ⟨k, -, hk⟩ := Finset.exists_ne_zero_of_sum_ne_zero h
  have : (G.adjMatrix ℕ ^ k) i j = Fintype.card {w : G.Walk i j | w.length = k} := by
    rw [SimpleGraph.adjMatrix_pow_apply_eq_card_walk]; simp
  rw [this] at hk
  have : Nonempty {w : G.Walk i j | w.length = k} := by
    rw [← Fintype.card_pos_iff]
    exact Nat.pos_of_ne_zero hk
  exact ⟨this.some.1⟩

theorem repair_statement : ∀ (V : Type) [Fintype V] [DecidableEq V] (G : SimpleGraph V) [DecidableRel G.Adj], ∀ i j : V, SE_math_994847_q.criterion G i j = 0 → ¬ G.Reachable i j := by
  intro V _ _ G _ i j hz hreach
  exact criterion_ne_zero_of_reachable G hreach hz

theorem repair_nonvacuous : SE_math_994847_q.criterion (⊥ : SimpleGraph (Fin 2)) 0 0 ≠ 0 ∧ SE_math_994847_q.criterion (⊥ : SimpleGraph (Fin 2)) 0 1 = 0 := by
  constructor
  · decide
  · decide

theorem final_theorem : ∀ (V : Type) [Fintype V] [DecidableEq V] [Nonempty V] (G : SimpleGraph V) [DecidableRel G.Adj], G.Connected ↔ ∀ i j : V, SE_math_994847_q.criterion G i j ≠ 0 := by
  intro V _ _ _ G _
  constructor
  · intro hconn i j
    exact criterion_ne_zero_of_reachable G (hconn i j)
  · intro hall
    exact ⟨fun i j => reachable_of_criterion_ne_zero G (hall i j)⟩

end SE_math_994847_q
