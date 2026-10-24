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
    Matrix V V ℕ := (G.adjMatrix ℕ + 1) ^ (Fintype.card V - 1)

/-- The corrected entrywise claim for every finite simple graph (shape fixed). -/
def CorrectedEntrywise : Prop :=
  ∀ (V : Type) [Fintype V] [DecidableEq V] (G : SimpleGraph V) [DecidableRel G.Adj],
    ∀ i j : V, criterion G i j = 0 → ¬ G.Reachable i j
-- ===== END FIXED PART =====

theorem key_pow {V : Type} [Fintype V] [DecidableEq V] (A : Matrix V V ℕ) (n : ℕ) (i j : V) :
    ((A + 1) ^ n) i j = 0 ↔ ∀ m ≤ n, (A ^ m) i j = 0 := by
  rw [(Commute.one_right A).add_pow', Matrix.sum_apply, Finset.sum_eq_zero_iff]
  simp only [Matrix.smul_apply, one_pow, mul_one, smul_eq_mul, Finset.mem_antidiagonal,
    mul_eq_zero, Prod.forall]
  constructor
  · intro h m hm
    rcases h m (n - m) (by omega) with h1 | h1
    · exact absurd h1 (Nat.choose_pos hm).ne'
    · exact h1
  · intro h a b hab
    right
    exact h a (by omega)

theorem walk_pow_ne_zero {V : Type} [Fintype V] [DecidableEq V] (G : SimpleGraph V)
    [DecidableRel G.Adj] (m : ℕ) (i j : V) :
    (G.adjMatrix ℕ ^ m) i j ≠ 0 ↔ ∃ p : G.Walk i j, p.length = m := by
  rw [SimpleGraph.adjMatrix_pow_apply_eq_card_walk, Nat.cast_id, Ne, Fintype.card_eq_zero_iff, not_isEmpty_iff]
  constructor
  · rintro ⟨⟨p, hp⟩⟩
    exact ⟨p, hp⟩
  · rintro ⟨p, hp⟩
    exact ⟨⟨p, hp⟩⟩

theorem criterion_ne_zero_iff {V : Type} [Fintype V] [DecidableEq V] (G : SimpleGraph V)
    [DecidableRel G.Adj] (i j : V) : criterion G i j ≠ 0 ↔ G.Reachable i j := by
  unfold criterion
  rw [Ne, key_pow]
  push_neg
  constructor
  · rintro ⟨m, _, hm⟩
    obtain ⟨p, _⟩ := (walk_pow_ne_zero G m i j).1 hm
    exact ⟨p⟩
  · rintro ⟨p⟩
    have hl := (p.bypass_isPath).length_lt
    exact ⟨p.bypass.length, by omega, (walk_pow_ne_zero G _ i j).2 ⟨p.bypass, rfl⟩⟩

theorem repair_statement : ∀ (V : Type) [Fintype V] [DecidableEq V] (G : SimpleGraph V) [DecidableRel G.Adj], ∀ i j : V, SE_math_994847_q.criterion G i j = 0 → ¬ G.Reachable i j := by
  intro V _ _ G _ i j h hr
  exact (criterion_ne_zero_iff G i j).2 hr h

theorem repair_nonvacuous : SE_math_994847_q.criterion (⊥ : SimpleGraph (Fin 2)) 0 0 ≠ 0 ∧ SE_math_994847_q.criterion (⊥ : SimpleGraph (Fin 2)) 0 1 = 0 := by
  constructor
  · exact (criterion_ne_zero_iff _ 0 0).2 (SimpleGraph.Reachable.refl _)
  · by_contra h
    have hr := (criterion_ne_zero_iff _ 0 1).1 h
    obtain ⟨p⟩ := hr
    cases p with
    | cons h' _ => exact h'

theorem final_theorem : ∀ (V : Type) [Fintype V] [DecidableEq V] [Nonempty V] (G : SimpleGraph V) [DecidableRel G.Adj], G.Connected ↔ ∀ i j : V, SE_math_994847_q.criterion G i j ≠ 0 := by
  intro V _ _ _ G _
  rw [SimpleGraph.connected_iff]
  simp only [criterion_ne_zero_iff]
  constructor
  · intro h i j
    exact h.1 i j
  · intro h
    exact ⟨h, inferInstance⟩

end SE_math_994847_q
