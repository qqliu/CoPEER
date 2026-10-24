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

theorem repair_statement : ∀ (V : Type) [Fintype V] [DecidableEq V] (G : SimpleGraph V) [DecidableRel G.Adj], ∀ i j : V, SE_math_994847_q.criterion G i j = 0 → ¬ G.Reachable i j := by
  intro V _ _ G _ i j hij hreach
  obtain ⟨p⟩ := hreach
  set q := p.toPath with hq
  have hlen : q.val.length < Fintype.card V := q.property.length_lt
  have hlenmem : q.val.length ∈ Finset.range (Fintype.card V) := Finset.mem_range.mpr hlen
  have hsum : criterion G i j = ∑ k ∈ Finset.range (Fintype.card V), (G.adjMatrix ℕ ^ k) i j := by
    unfold criterion
    rw [Matrix.sum_apply]
  rw [hsum] at hij
  have hzero : (G.adjMatrix ℕ ^ q.val.length) i j = 0 :=
    (Finset.sum_eq_zero_iff (f := fun k => (G.adjMatrix ℕ ^ k) i j)).mp hij q.val.length hlenmem
  have hpos : 0 < (G.adjMatrix ℕ ^ q.val.length) i j := by
    rw [G.adjMatrix_pow_apply_eq_card_walk]
    apply Fintype.card_pos_iff.mpr
    exact ⟨⟨q.val, rfl⟩⟩
  omega

theorem repair_nonvacuous : SE_math_994847_q.criterion (⊥ : SimpleGraph (Fin 2)) 0 0 ≠ 0 ∧ SE_math_994847_q.criterion (⊥ : SimpleGraph (Fin 2)) 0 1 = 0 := by
  constructor
  · unfold criterion
    decide
  · unfold criterion
    decide

theorem final_theorem : ∀ (V : Type) [Fintype V] [DecidableEq V] [Nonempty V] (G : SimpleGraph V) [DecidableRel G.Adj], G.Connected ↔ ∀ i j : V, SE_math_994847_q.criterion G i j ≠ 0 := by
  intro V _ _ _ G _
  constructor
  · intro hconn i j
    have hreach : G.Reachable i j := hconn i j
    intro hzero
    exact repair_statement V G i j hzero hreach
  · intro hcrit
    rw [SimpleGraph.connected_iff]
    refine ⟨?_, ‹Nonempty V›⟩
    intro i j
    by_contra hnr
    -- if not reachable, then criterion i j = 0? We need the converse direction.
    have := hcrit i j
    apply this
    unfold criterion
    have hall : ∀ k, (G.adjMatrix ℕ ^ k) i j = 0 := by
      intro k
      rw [G.adjMatrix_pow_apply_eq_card_walk]
      have : IsEmpty { p : G.Walk i j | p.length = k } := by
        constructor
        rintro ⟨p, _⟩
        exact hnr ⟨p⟩
      simp [Fintype.card_eq_zero_iff.mpr this]
    rw [Matrix.sum_apply]
    apply Finset.sum_eq_zero
    intro k _
    exact hall k

end SE_math_994847_q
