import defs_only
namespace SE_cs_1957_a2388_Census

def rhs (b p k L : Nat) : Nat :=
  b ^ (p * L) * (Finset.range L).sum (fun j => (L - j) ^ k)

def CorrectedLemmaA : Prop :=
  ∀ b p k L : Nat, 2 ≤ b → drivingSum b (b ^ p) p k L = rhs b p k L

theorem repair_statement :
    ∀ b p k L : Nat, 2 ≤ b → SE_cs_1957_a2388_Census.drivingSum b (b ^ p) p k L = SE_cs_1957_a2388_Census.rhs b p k L
| b, p, k, L, hb => by
  unfold SE_cs_1957_a2388_Census.drivingSum SE_cs_1957_a2388_Census.drivingSumAux SE_cs_1957_a2388_Census.rhs SE_cs_1957_a2388_Census.h
  have hb1 : 1 < b := (Nat.succ_le_iff).1 hb
  have hsum :
      (Finset.range L).sum (fun j =>
        (b ^ p) ^ j * ((b ^ (L - j)) ^ p * (Nat.log b (b ^ (L - j))) ^ k))
        =
      (Finset.range L).sum (fun j => b ^ (p * L) * (L - j) ^ k) := by
    apply Finset.sum_congr rfl
    intro j hj
    have h1 : (b ^ p) ^ j = b ^ (p * j) := by
      simpa [Nat.mul_comm] using (Nat.pow_mul b p j).symm
    have h2 : (b ^ (L - j)) ^ p = b ^ (p * (L - j)) := by
      simpa [Nat.mul_comm] using (Nat.pow_mul b (L - j) p).symm
    have hlog : Nat.log b (b ^ (L - j)) = L - j := by
      by_cases hzero : L = j
      · subst hzero
        simp [Nat.log_one]
      · have hpos : 0 < L - j := Nat.sub_pos_of_lt (by
          have : j < L := Finset.mem_range.mp hj
          exact this)
        simpa [Nat.log_pow hb1 hpos]
    calc
      (b ^ p) ^ j * ((b ^ (L - j)) ^ p * (Nat.log b (b ^ (L - j))) ^ k)
          = (b ^ (p * j)) * (b ^ (p * (L - j)) * (L - j) ^ k) := by
            simpa [h1, h2, hlog]
      _ = (b ^ (p * j) * b ^ (p * (L - j))) * (L - j) ^ k := by
            ring
      _ = b ^ (p * j + p * (L - j)) * (L - j) ^ k := by
            simpa [Nat.pow_add] using rfl
      _ = b ^ (p * L) * (L - j) ^ k := by
            have hsum' : p * j + p * (L - j) = p * L := by
              have hjle : j ≤ L := Nat.le_of_lt (Finset.mem_range.mp hj)
              have hadd : j + (L - j) = L := Nat.add_sub_cancel' hjle
              calc
                p * j + p * (L - j) = p * (j + (L - j)) := by
                  simpa [Nat.mul_add, Nat.add_comm, Nat.add_left_comm, Nat.add_assoc]
                _ = p * L := by simpa [hadd]
            simpa [hsum']
  simpa [Finset.mul_sum, hsum]

theorem repair_nonvacuous :
    ∃ b p k L : Nat, 2 ≤ b ∧ SE_cs_1957_a2388_Census.rhs b p k L ≠ SE_cs_1957_a2388_Census.claimedRHS b p k L :=
by
  refine ⟨2, 1, 1, 2, ?_, ?_⟩
  · exact le_rfl
  · have : SE_cs_1957_a2388_Census.rhs 2 1 1 2 = 12 := by
      simp [rhs, claimedRHS, Nat.pow_mul] 
    have : SE_cs_1957_a2388_Census.claimedRHS 2 1 1 2 = 16 := by
      simp [claimedRHS, Nat.pow_mul] 
    intro h
    have : 12 = 16 := by
      simpa [*] using h
    decide

theorem final_theorem :
    ∀ b p k L : Nat, 2 ≤ b → SE_cs_1957_a2388_Census.drivingSum b (b ^ p) p k L = SE_cs_1957_a2388_Census.rhs b p k L :=
  repair_statement

end SE_cs_1957_a2388_Census
