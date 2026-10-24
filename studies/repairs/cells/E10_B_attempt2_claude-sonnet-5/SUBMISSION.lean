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

/-- If a power of the adjacency matrix has a nonzero entry at `i j`, there is a walk of that
length, hence `i` and `j` are reachable. -/
theorem adjMatrix_pow_ne_zero_reachable {V : Type} [Fintype V] [DecidableEq V]
    (G : SimpleGraph V) [DecidableRel G.Adj] (i j : V) (k : ℕ)
    (h : (G.adjMatrix ℕ ^ k) i j ≠ 0) : G.Reachable i j := by
  rw [SimpleGraph.adjMatrix_pow_apply_eq_card_walk] at h
  simp only [ne_eq, Nat.cast_eq_zero] at h
  have hpos : 0 < Fintype.card {p : G.Walk i j | p.length = k} := Nat.pos_of_ne_zero h
  obtain ⟨p, _⟩ := Fintype.card_pos_iff.mp hpos
  exact ⟨p⟩

/-- If `i` and `j` are reachable, some power (strictly less than the vertex count) of the
adjacency matrix has a nonzero entry at `i j`, witnessed by a shortest (bypassed) walk. -/
theorem reachable_exists_pow_ne_zero {V : Type} [Fintype V] [DecidableEq V]
    (G : SimpleGraph V) [DecidableRel G.Adj] {i j : V} (h : G.Reachable i j) :
    ∃ k < Fintype.card V, (G.adjMatrix ℕ ^ k) i j ≠ 0 := by
  obtain ⟨p⟩ := h
  refine ⟨p.bypass.length, SimpleGraph.Walk.IsPath.length_lt p.bypass_isPath, ?_⟩
  rw [SimpleGraph.adjMatrix_pow_apply_eq_card_walk]
  simp only [ne_eq, Nat.cast_eq_zero, Fintype.card_eq_zero_iff]
  intro hempty
  exact hempty.false ⟨p.bypass, rfl⟩

/-- `criterion` entrywise is zero iff every power `A^k`, `k < n`, is zero at that entry. -/
theorem criterion_apply_eq_zero_iff {V : Type} [Fintype V] [DecidableEq V]
    (G : SimpleGraph V) [DecidableRel G.Adj] (i j : V) :
    criterion G i j = 0 ↔ ∀ k ∈ Finset.range (Fintype.card V), (G.adjMatrix ℕ ^ k) i j = 0 := by
  unfold criterion
  rw [Matrix.sum_apply]
  exact Finset.sum_eq_zero_iff

theorem repair_statement : ∀ (V : Type) [Fintype V] [DecidableEq V] (G : SimpleGraph V) [DecidableRel G.Adj], ∀ i j : V, SE_math_994847_q.criterion G i j = 0 → ¬ G.Reachable i j := by
  intro V _ _ G _ i j hzero hreach
  obtain ⟨k, hk, hne⟩ := reachable_exists_pow_ne_zero G hreach
  have := (criterion_apply_eq_zero_iff G i j).mp hzero k (Finset.mem_range.mpr hk)
  exact hne this

theorem repair_nonvacuous : SE_math_994847_q.criterion (⊥ : SimpleGraph (Fin 2)) 0 0 ≠ 0 ∧ SE_math_994847_q.criterion (⊥ : SimpleGraph (Fin 2)) 0 1 = 0 := by
  constructor <;> decide

theorem final_theorem : ∀ (V : Type) [Fintype V] [DecidableEq V] [Nonempty V] (G : SimpleGraph V) [DecidableRel G.Adj], G.Connected ↔ ∀ i j : V, SE_math_994847_q.criterion G i j ≠ 0 := by
  intro V _ _ _ G _
  constructor
  · intro hconn i j hzero
    exact (repair_statement V G i j hzero) (hconn.preconnected i j)
  · intro hall
    refine ⟨fun i j => ?_⟩
    have hex : ∃ k ∈ Finset.range (Fintype.card V), (G.adjMatrix ℕ ^ k) i j ≠ 0 := by
      by_contra hc
      push_neg at hc
      exact hall i j ((criterion_apply_eq_zero_iff G i j).mpr hc)
    obtain ⟨k, _, hne⟩ := hex
    exact adjMatrix_pow_ne_zero_reachable G i j k hne

end SE_math_994847_q
