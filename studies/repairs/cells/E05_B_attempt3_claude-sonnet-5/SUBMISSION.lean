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
def rhs (b p k L : Nat) : Nat := (b ^ L) ^ p * ∑ j ∈ Finset.range L, (L - j) ^ k

/-- The corrected Lemma A on the source's domain `b ≥ 2`, every `p`, `k`, `L` (shape fixed). -/
def CorrectedLemmaA : Prop := ∀ b p k L : Nat, 2 ≤ b → drivingSum b (b ^ p) p k L = rhs b p k L
-- ===== END FIXED PART =====

theorem repair_statement : ∀ b p k L : Nat, 2 ≤ b → SE_cs_1957_a2388_Census.drivingSum b (b ^ p) p k L = SE_cs_1957_a2388_Census.rhs b p k L := by
  intro b p k L hb
  show drivingSumAux b (b ^ p) p k L L = rhs b p k L
  unfold drivingSumAux rhs
  rw [Finset.mul_sum]
  apply Finset.sum_congr rfl
  intro j hj
  simp only [Finset.mem_range] at hj
  have hjL : j ≤ L := le_of_lt hj
  have h1 : j + (L - j) = L := by omega
  have hexp : p * j + (L - j) * p = L * p := by
    calc p * j + (L - j) * p = (j + (L - j)) * p := by ring
      _ = L * p := by rw [h1]
  have key : (b ^ p) ^ j * (b ^ (L - j)) ^ p = (b ^ L) ^ p := by
    rw [← pow_mul, ← pow_mul, ← pow_add, hexp, pow_mul]
  show (b ^ p) ^ j * h b p k (b ^ (L - j)) = (b ^ L) ^ p * (L - j) ^ k
  unfold h lgb
  rw [Nat.log_pow (by omega : 1 < b)]
  rw [← mul_assoc, key]

theorem repair_nonvacuous : ∃ b p k L : Nat, 2 ≤ b ∧ SE_cs_1957_a2388_Census.rhs b p k L ≠ SE_cs_1957_a2388_Census.claimedRHS b p k L := by
  refine ⟨2, 1, 1, 2, by omega, ?_⟩
  decide

theorem final_theorem : ∀ b p k L : Nat, 2 ≤ b → SE_cs_1957_a2388_Census.drivingSum b (b ^ p) p k L = SE_cs_1957_a2388_Census.rhs b p k L := repair_statement

end SE_cs_1957_a2388_Census
