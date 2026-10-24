import defs_only
/-!
Record E05: correction template (Nat model of Lemma A).
Fill the ONE hole `«HOLE»` in the FIXED PART (nothing else in the fixed part may change), then prove
the OBLIGATIONS below with exactly these names and statements. Helper lemmas may be added between the
fixed part and the obligations, inside the namespace. Import nothing else.
-/
namespace SE_cs_1957_a2388_Census

open scoped BigOperators

-- ===== FIXED PART: only the hole «HOLE» may be edited =====
/-- The corrected right-hand side of Lemma A in the Nat model: the value of the driving sum
`drivingSum b (b ^ p) p k L` (that is, `a = b ^ p`, `n = b ^ L`) as an expression in `b`, `p`, `k`, `L`.
It may use a `Finset.sum` over an explicit range in `L`, but may not refer to `drivingSum`, `drivingSumAux`,
`h`, `lgb`, `Nat.log`, `middleTerm` or `claimedRHS`; no `if`/`match`. -/
def rhs (b p k L : Nat) : Nat := (b ^ p) ^ L * (Finset.sum (Finset.range L) fun j => (L - j) ^ k)

/-- The corrected Lemma A on the source's domain `b ≥ 2`, every `p`, `k`, `L` (shape fixed). -/
def CorrectedLemmaA : Prop := ∀ b p k L : Nat, 2 ≤ b → drivingSum b (b ^ p) p k L = rhs b p k L
-- ===== END FIXED PART =====

/-- Universal: the corrected identity for every `b ≥ 2`, `p`, `k`, `L`. -/
theorem repair_statement :
    ∀ b p k L : Nat, 2 ≤ b →
      SE_cs_1957_a2388_Census.drivingSum b (b ^ p) p k L = SE_cs_1957_a2388_Census.rhs b p k L :=
by
  intro b p k L hb
  -- unfold definitions of drivingSum and rhs
  unfold SE_cs_1957_a2388_Census.drivingSum SE_cs_1957_a2388_Census.drivingSumAux SE_cs_1957_a2388_Census.rhs
  have hb1 : 1 < b := (Nat.succ_le_iff).mp hb
  -- rewrite the whole sum, simplifying each term
  have hsum :
      (Finset.sum (Finset.range L) fun j =>
        (b ^ p) ^ j * SE_cs_1957_a2388_Census.h b p k (b ^ (L - j))) =
        Finset.sum (Finset.range L) fun j =>
          (b ^ p) ^ L * (L - j) ^ k := by
    apply Finset.sum_congr rfl
    intro j hj
    have hle : j ≤ L := Nat.le_of_lt (Finset.mem_range.mp hj)
    unfold SE_cs_1957_a2388_Census.h SE_cs_1957_a2388_Census.lgb
    simp [Nat.pow_mul, Nat.log_pow hb1, Nat.mul_comm, Nat.mul_left_comm, Nat.mul_assoc,
          Nat.add_sub_cancel hle, Nat.mul_add, Nat.add_comm, Nat.add_left_comm, Nat.add_assoc]
  calc
    (Finset.sum (Finset.range L) fun j =>
        (b ^ p) ^ j * SE_cs_1957_a2388_Census.h b p k (b ^ (L - j))) =
        Finset.sum (Finset.range L) fun j => (b ^ p) ^ L * (L - j) ^ k := hsum
    _ = (b ^ p) ^ L *
        (Finset.sum (Finset.range L) fun j => (L - j) ^ k) := by
          simpa [Finset.mul_sum] using
            (Finset.mul_sum (s := Finset.range L) (a := (b ^ p) ^ L)
                (f := fun j => (L - j) ^ k)).symm
    _ = (b ^ p) ^ L *
        (Finset.sum (Finset.range L) fun j => (L - j) ^ k) := rfl

/-- Non-vacuity: the corrected RHS differs from the source's claimed RHS at some point. -/
theorem repair_nonvacuous :
    ∃ b p k L : Nat, 2 ≤ b ∧ SE_cs_1957_a2388_Census.rhs b p k L ≠ SE_cs_1957_a2388_Census.claimedRHS b p k L :=
by
  refine ⟨2, 1, 1, 2, ?_, ?_⟩
  · decide
  · have h : (12 : Nat) ≠ 16 := by decide
    simpa [rhs, claimedRHS] using h

/-- Final theorem: restatement of the corrected universal statement. -/
theorem final_theorem :
    ∀ b p k L : Nat, 2 ≤ b →
      SE_cs_1957_a2388_Census.drivingSum b (b ^ p) p k L = SE_cs_1957_a2388_Census.rhs b p k L :=
  repair_statement

end SE_cs_1957_a2388_Census
