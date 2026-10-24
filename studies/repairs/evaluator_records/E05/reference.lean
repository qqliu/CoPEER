import defs_only
/- EVALUATOR-ONLY reference correction for E05 (original package: trueRHS, line 48; repair, line 180). -/
namespace SE_cs_1957_a2388_Census.Ref

/-- Reference corrected right-hand side: `n^p * ∑_{i=1}^{L} i^k` at `n = b^L`. -/
def rhs (b p k L : Nat) : Nat := (b ^ L) ^ p * ∑ i ∈ Finset.range L, (i + 1) ^ k

theorem term_eq (b p k L j : Nat) (hb : 2 ≤ b) (hj : j < L) :
    (b ^ p) ^ j * h b p k (b ^ (L - j)) = (b ^ L) ^ p * (L - j) ^ k := by
  unfold h lgb
  rw [Nat.log_pow (by omega)]
  have e : b ^ L = b ^ j * b ^ (L - j) := by
    rw [← pow_add]
    congr 1
    omega
  rw [e]
  ring

theorem universal : ∀ b p k L : Nat, 2 ≤ b → drivingSum b (b ^ p) p k L = rhs b p k L := by
  intro b p k L hb
  unfold drivingSum drivingSumAux rhs
  have key : ∑ j ∈ Finset.range L, (b ^ p) ^ j * h b p k (b ^ (L - j))
      = ∑ j ∈ Finset.range L, (b ^ L) ^ p * (L - 1 - j + 1) ^ k := by
    apply Finset.sum_congr rfl
    intro j hj
    rw [Finset.mem_range] at hj
    rw [term_eq b p k L j hb hj]
    have e : L - j = L - 1 - j + 1 := by omega
    rw [e]
  rw [key, Finset.sum_range_reflect (fun j => (b ^ L) ^ p * (j + 1) ^ k) L, Finset.mul_sum]

end SE_cs_1957_a2388_Census.Ref
