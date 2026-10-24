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

theorem repair_statement : ∀ b p k L : Nat, 2 ≤ b → SE_cs_1957_a2388_Census.drivingSum b (b ^ p) p k L = SE_cs_1957_a2388_Census.rhs b p k L := by
  intro b p k L hb
  have hb1 : 1 < b := hb
  unfold drivingSum drivingSumAux rhs
  have step1 : ∀ j ∈ Finset.range L, (b^p)^j * h b p k (b ^ (L - j)) = (b^L)^p * (L - j)^k := by
    intro j hj
    simp only [Finset.mem_range] at hj
    have hlog : lgb b (b ^ (L - j)) = L - j := by
      unfold lgb
      exact Nat.log_pow hb1 (L - j)
    unfold h
    rw [hlog, ← pow_mul, ← pow_mul, ← mul_assoc, ← pow_add]
    have heq : p * j + (L - j) * p = L * p := by
      have hjL : j + (L - j) = L := by omega
      calc p * j + (L - j) * p = p * j + p * (L - j) := by ring
        _ = p * (j + (L - j)) := by ring
        _ = p * L := by rw [hjL]
        _ = L * p := by ring
    rw [heq, pow_mul]
  rw [Finset.sum_congr rfl step1]
  rw [← Finset.mul_sum]
  congr 1
  have key : ∀ j ∈ Finset.range L, (L - j) = (L - 1 - j) + 1 := by
    intro j hj
    simp only [Finset.mem_range] at hj
    omega
  rw [Finset.sum_congr rfl (fun j hj => by rw [key j hj])]
  exact Finset.sum_range_reflect (fun i => (i+1)^k) L

theorem repair_nonvacuous : ∃ b p k L : Nat, 2 ≤ b ∧ SE_cs_1957_a2388_Census.rhs b p k L ≠ SE_cs_1957_a2388_Census.claimedRHS b p k L := by
  refine ⟨2, 1, 1, 2, ?_, ?_⟩
  · omega
  · decide

theorem final_theorem : ∀ b p k L : Nat, 2 ≤ b → SE_cs_1957_a2388_Census.drivingSum b (b ^ p) p k L = SE_cs_1957_a2388_Census.rhs b p k L := repair_statement

end SE_cs_1957_a2388_Census
