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
def rhs (b p k L : Nat) : Nat := (b ^ L) ^ p * (∑ i ∈ Finset.range L, (i + 1) ^ k)

/-- The corrected Lemma A on the source's domain `b ≥ 2`, every `p`, `k`, `L` (shape fixed). -/
def CorrectedLemmaA : Prop := ∀ b p k L : Nat, 2 ≤ b → drivingSum b (b ^ p) p k L = rhs b p k L
-- ===== END FIXED PART =====

theorem drivingSum_eq_rhs (b p k L : Nat) (hb : 2 ≤ b) :
    drivingSum b (b ^ p) p k L = rhs b p k L := by
  have hb1 : 1 < b := hb
  unfold drivingSum drivingSumAux
  have step : ∀ j ∈ Finset.range L, (b ^ p) ^ j * h b p k (b ^ (L - j)) = (b ^ L) ^ p * (L - j) ^ k := by
    intro j hj
    rw [Finset.mem_range] at hj
    unfold h lgb
    rw [Nat.log_pow hb1]
    have hjle : j ≤ L := le_of_lt hj
    have hsplit : (b ^ (L - j)) ^ p * (b ^ p) ^ j = (b ^ L) ^ p := by
      rw [← pow_mul, ← pow_mul, ← pow_add, ← pow_mul]
      congr 1
      have hcancel : (L - j) + j = L := Nat.sub_add_cancel hjle
      calc (L - j) * p + p * j = (L - j) * p + j * p := by ring
        _ = ((L - j) + j) * p := by rw [Nat.add_mul]
        _ = L * p := by rw [hcancel]
    calc (b ^ p) ^ j * ((b ^ (L - j)) ^ p * (L - j) ^ k)
        = ((b ^ (L - j)) ^ p * (b ^ p) ^ j) * (L - j) ^ k := by ring
      _ = (b ^ L) ^ p * (L - j) ^ k := by rw [hsplit]
  rw [Finset.sum_congr rfl step]
  unfold rhs
  rw [← Finset.mul_sum]
  congr 1
  have hrefl := Finset.sum_range_reflect (fun i => (i + 1) ^ k) L
  rw [← hrefl]
  apply Finset.sum_congr rfl
  intro j hj
  rw [Finset.mem_range] at hj
  congr 1
  omega

theorem repair_statement : ∀ b p k L : Nat, 2 ≤ b → SE_cs_1957_a2388_Census.drivingSum b (b ^ p) p k L = SE_cs_1957_a2388_Census.rhs b p k L :=
  fun b p k L hb => drivingSum_eq_rhs b p k L hb

theorem repair_nonvacuous : ∃ b p k L : Nat, 2 ≤ b ∧ SE_cs_1957_a2388_Census.rhs b p k L ≠ SE_cs_1957_a2388_Census.claimedRHS b p k L := by
  refine ⟨2, 0, 1, 2, le_refl 2, ?_⟩
  unfold rhs claimedRHS
  decide

theorem final_theorem : ∀ b p k L : Nat, 2 ≤ b → SE_cs_1957_a2388_Census.drivingSum b (b ^ p) p k L = SE_cs_1957_a2388_Census.rhs b p k L := repair_statement

end SE_cs_1957_a2388_Census
