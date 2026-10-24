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

-- ===== OBLIGATIONS: keep the names and statements; replace each `sorry` by a proof =====
/-- Universal: the corrected identity for every `b ≥ 2`, `p`, `k`, `L`. -/
theorem repair_statement : ∀ b p k L : Nat, 2 ≤ b → SE_cs_1957_a2388_Census.drivingSum b (b ^ p) p k L = SE_cs_1957_a2388_Census.rhs b p k L := by
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

/-- Non-vacuity: the corrected right-hand side differs from the source's `claimedRHS` at some point of
the domain. -/
theorem repair_nonvacuous : ∃ b p k L : Nat, 2 ≤ b ∧ SE_cs_1957_a2388_Census.rhs b p k L ≠ SE_cs_1957_a2388_Census.claimedRHS b p k L := ⟨2, 1, 1, 2, by norm_num, by decide⟩

/-- The endpoint of this record is the corrected universal statement itself; restate it here, e.g.
`:= repair_statement`. If you cannot, replace this declaration (this doc comment included) by the single
line `-- CANNOT: <reason>`. -/
theorem final_theorem : ∀ b p k L : Nat, 2 ≤ b → SE_cs_1957_a2388_Census.drivingSum b (b ^ p) p k L = SE_cs_1957_a2388_Census.rhs b p k L := repair_statement
-- ===== END OBLIGATIONS =====
end SE_cs_1957_a2388_Census
