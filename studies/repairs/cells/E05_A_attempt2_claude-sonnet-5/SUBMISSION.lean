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
def rhs (b p k L : Nat) : Nat := (b ^ L) ^ p * ∑ i ∈ Finset.range L, (i + 1) ^ k

/-- The corrected Lemma A on the source's domain `b ≥ 2`, every `p`, `k`, `L` (shape fixed). -/
def CorrectedLemmaA : Prop := ∀ b p k L : Nat, 2 ≤ b → drivingSum b (b ^ p) p k L = rhs b p k L
-- ===== END FIXED PART =====

/-- Each term of the driving sum simplifies once we know `Nat.log b (b ^ m) = m`. -/
theorem term_eq (b p k L j : Nat) (hb : 2 ≤ b) (hj : j < L) :
    (b ^ p) ^ j * h b p k (b ^ (L - j)) = (b ^ L) ^ p * (L - j) ^ k := by
  have hb1 : 1 < b := hb
  have hlog : lgb b (b ^ (L - j)) = L - j := Nat.log_pow hb1 (L - j)
  unfold h
  rw [hlog]
  have hsplit : (b ^ (L - j)) ^ p = b ^ ((L - j) * p) := by rw [pow_mul]
  have hsplit2 : (b ^ p) ^ j = b ^ (p * j) := by rw [pow_mul]
  have hL : L - j + j = L := Nat.sub_add_cancel (le_of_lt hj)
  rw [hsplit2, hsplit, ← mul_assoc, ← pow_add]
  have heq : p * j + (L - j) * p = L * p := by
    have : p * j + (L - j) * p = p * (j + (L - j)) := by ring
    rw [this, Nat.add_sub_cancel' (le_of_lt hj)]
    ring
  rw [heq]
  have hbLp : (b ^ L) ^ p = b ^ (L * p) := by rw [pow_mul]
  rw [hbLp]

theorem drivingSumAux_eq (b p k L m : Nat) (hb : 2 ≤ b) (hm : m ≤ L) :
    drivingSumAux b (b ^ p) p k L m = (b ^ L) ^ p * ∑ j ∈ Finset.range m, (L - j) ^ k := by
  unfold drivingSumAux
  rw [Finset.mul_sum]
  apply Finset.sum_congr rfl
  intro j hj
  rw [Finset.mem_range] at hj
  exact term_eq b p k L j hb (lt_of_lt_of_le hj hm)

/-- Reindexing: `∑ j ∈ range L, (L - j) ^ k = ∑ i ∈ range L, (i + 1) ^ k`. -/
theorem reindex_sum (k L : Nat) :
    ∑ j ∈ Finset.range L, (L - j) ^ k = ∑ i ∈ Finset.range L, (i + 1) ^ k := by
  apply Finset.sum_nbij' (fun j => L - 1 - j) (fun i => L - 1 - i)
  · intro j hj
    rw [Finset.mem_range] at hj
    rw [Finset.mem_range]
    omega
  · intro i hi
    rw [Finset.mem_range] at hi
    rw [Finset.mem_range]
    omega
  · intro j hj
    rw [Finset.mem_range] at hj
    omega
  · intro i hi
    rw [Finset.mem_range] at hi
    omega
  · intro j hj
    rw [Finset.mem_range] at hj
    congr 1
    omega

theorem repair_statement : ∀ b p k L : Nat, 2 ≤ b → SE_cs_1957_a2388_Census.drivingSum b (b ^ p) p k L = SE_cs_1957_a2388_Census.rhs b p k L := by
  intro b p k L hb
  unfold drivingSum rhs
  rw [drivingSumAux_eq b p k L L hb (le_refl L), reindex_sum]

theorem repair_nonvacuous : ∃ b p k L : Nat, 2 ≤ b ∧ SE_cs_1957_a2388_Census.rhs b p k L ≠ SE_cs_1957_a2388_Census.claimedRHS b p k L := by
  refine ⟨2, 0, 1, 2, ?_, ?_⟩
  · decide
  · unfold rhs claimedRHS
    decide

theorem final_theorem : ∀ b p k L : Nat, 2 ≤ b → SE_cs_1957_a2388_Census.drivingSum b (b ^ p) p k L = SE_cs_1957_a2388_Census.rhs b p k L := repair_statement

end SE_cs_1957_a2388_Census
