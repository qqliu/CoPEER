import defs_only
/-!
Record E05: correction template (Nat model of Lemma A).
Fill the ONE hole `«HOLE»` in the FIXED PART (nothing else in the fixed part may change), then prove
the OBLIGATIONS below with exactly these names and statements. Helper lemmas may be added between the
fixed part and the obligations, inside the namespace. Import nothing else.
-/
namespace SE_cs_1957_a2388_Census

-- ===== FIXED PART: only the hole «HOLE» may be edited =====
/-- The corrected right-hand side of Lemma A in the Nat model: the value of the driving sum
`drivingSum b (b ^ p) p k L` (that is, `a = b ^ p`, `n = b ^ L`) as an expression in `b`, `p`, `k`, `L`.
It may use a `Finset.sum` over an explicit range in `L`, but may not refer to `drivingSum`, `drivingSumAux`,
`h`, `lgb`, `Nat.log`, `middleTerm` or `claimedRHS`; no `if`/`match`. -/
def rhs (b p k L : Nat) : Nat := (b ^ L) ^ p * ∑ j ∈ Finset.range L, (j + 1) ^ k

/-- The corrected Lemma A on the source's domain `b ≥ 2`, every `p`, `k`, `L` (shape fixed). -/
def CorrectedLemmaA : Prop := ∀ b p k L : Nat, 2 ≤ b → drivingSum b (b ^ p) p k L = rhs b p k L
-- ===== END FIXED PART =====

theorem drivingSum_eq_aux (b p k L : Nat) (hb : 2 ≤ b) :
    drivingSum b (b ^ p) p k L = (b ^ L) ^ p * ∑ j ∈ Finset.range L, (L - j) ^ k := by
  unfold drivingSum drivingSumAux
  rw [Finset.mul_sum]
  apply Finset.sum_congr rfl
  intro j hj
  simp only [Finset.mem_range] at hj
  unfold h
  have hlog : lgb b (b ^ (L - j)) = L - j := by
    unfold lgb
    exact Nat.log_pow hb (L - j)
  rw [hlog]
  have hpow : (b ^ p) ^ j * (b ^ (L - j)) ^ p = (b ^ L) ^ p := by
    rw [← pow_mul, ← pow_mul, ← pow_add, ← pow_mul]
    have hjL : j ≤ L := le_of_lt hj
    rw [Nat.mul_comm (L - j) p, ← Nat.mul_add, Nat.add_sub_cancel' hjL, Nat.mul_comm]
  calc (b ^ p) ^ j * ((b ^ (L - j)) ^ p * (L - j) ^ k)
      = (b ^ p) ^ j * (b ^ (L - j)) ^ p * (L - j) ^ k := by ring
    _ = (b ^ L) ^ p * (L - j) ^ k := by rw [hpow]

theorem sum_reflect_aux (k L : Nat) :
    ∑ j ∈ Finset.range L, (L - j) ^ k = ∑ j ∈ Finset.range L, (j + 1) ^ k := by
  have := Finset.sum_range_reflect (fun i => (i + 1) ^ k) L
  convert this using 2 with j hj
  simp only [Finset.mem_range] at hj
  congr 1
  omega

-- ===== OBLIGATIONS =====

theorem repair_statement : ∀ b p k L : Nat, 2 ≤ b → SE_cs_1957_a2388_Census.drivingSum b (b ^ p) p k L = SE_cs_1957_a2388_Census.rhs b p k L := by
  intro b p k L hb
  rw [drivingSum_eq_aux b p k L hb, sum_reflect_aux k L]
  rfl

theorem repair_nonvacuous : ∃ b p k L : Nat, 2 ≤ b ∧ SE_cs_1957_a2388_Census.rhs b p k L ≠ SE_cs_1957_a2388_Census.claimedRHS b p k L := by
  refine ⟨2, 1, 1, 2, by omega, ?_⟩
  decide

theorem final_theorem : ∀ b p k L : Nat, 2 ≤ b → SE_cs_1957_a2388_Census.drivingSum b (b ^ p) p k L = SE_cs_1957_a2388_Census.rhs b p k L := repair_statement

end SE_cs_1957_a2388_Census
