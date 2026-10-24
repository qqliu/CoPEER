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
def rhs (b p k L : Nat) : Nat :=
  ∑ j ∈ Finset.range L, (b ^ p) ^ j * ((b ^ (L - j)) ^ p * (L - j) ^ k)

/-- The corrected Lemma A on the source's domain `b ≥ 2`, every `p`, `k`, `L` (shape fixed). -/
def CorrectedLemmaA : Prop := ∀ b p k L : Nat, 2 ≤ b → drivingSum b (b ^ p) p k L = rhs b p k L
-- ===== END FIXED PART =====

theorem repair_statement :
    ∀ b p k L : Nat, 2 ≤ b → SE_cs_1957_a2388_Census.drivingSum b (b ^ p) p k L = SE_cs_1957_a2388_Census.rhs b p k L
| b, p, k, L, hb => by
  unfold SE_cs_1957_a2388_Census.drivingSum SE_cs_1957_a2388_Census.drivingSumAux SE_cs_1957_a2388_Census.rhs
  have hb' : 1 < b := (Nat.succ_le_iff).1 hb
  simp [SE_cs_1957_a2388_Census.h, SE_cs_1957_a2388_Census.lgb, Nat.log_pow hb']

theorem repair_nonvacuous :
    ∃ b p k L : Nat, 2 ≤ b ∧ SE_cs_1957_a2388_Census.rhs b p k L ≠ SE_cs_1957_a2388_Census.claimedRHS b p k L :=
by
  refine ⟨2, 1, 1, 2, ?_, ?_⟩
  · decide
  · decide

theorem final_theorem :
    ∀ b p k L : Nat, 2 ≤ b → SE_cs_1957_a2388_Census.drivingSum b (b ^ p) p k L = SE_cs_1957_a2388_Census.rhs b p k L :=
  repair_statement

end SE_cs_1957_a2388_Census
