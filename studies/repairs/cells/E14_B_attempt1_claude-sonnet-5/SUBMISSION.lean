import defs_only
/-!
Record E14: correction template.
Fill the ONE hole `«HOLE»` in the FIXED PART (nothing else in the fixed part may change), then prove
the OBLIGATIONS below with exactly these names and statements. Helper lemmas may be added between the
fixed part and the obligations, inside the namespace. Import nothing else.
-/
namespace Audit_reddit_math_2s4u2m

-- ===== FIXED PART: only the hole «HOLE» may be edited =====
/-- The corrected decimal digit count for the source's 565248-bit budget. The hole must be a single
natural-number literal (decimal digits only): no arithmetic, no names, no `Nat.log`, no `Nat.digits`. -/
def digitBound : Nat := 170157

/-- The corrected located statement (shape fixed): every value fitting the budget has at most `digitBound`
decimal digits, and the largest fitting value has exactly `digitBound` digits (so the bound is the least one). -/
def CorrectedDigitCount : Prop :=
  (∀ H : Nat, FitsBits bits H → HasAtMostDecDigits H digitBound) ∧ HasDecDigits maximum digitBound
-- ===== END FIXED PART =====

/-- Fast repeated-squaring helper: `dbl b k = b ^ (2 ^ k)`, computed by `k` squarings so that huge
exponents never appear literally in a single `^` node (avoiding the exponent-size safety threshold). -/
def dbl (b : Nat) : Nat → Nat
  | 0 => b
  | (k+1) => dbl b k * dbl b k

theorem dbl_eq (b : Nat) : ∀ k, dbl b k = b ^ (2 ^ k) := by
  intro k
  induction k with
  | zero => simp [dbl]
  | succ n ih =>
    show dbl b n * dbl b n = b ^ (2 ^ (n+1))
    rw [ih, ← pow_add, ← two_mul, ← pow_succ']

theorem bits_eq : bits = 565248 := by decide

theorem pow2_565248 : (2:Nat)^565248 = dbl 2 19 * dbl 2 15 * dbl 2 13 := by
  rw [dbl_eq, dbl_eq, dbl_eq, ← pow_add, ← pow_add]
  norm_num

theorem pow10_170156 : (10:Nat)^170156 =
    dbl 10 17 * dbl 10 15 * dbl 10 12 * dbl 10 11 * dbl 10 7 * dbl 10 5 * dbl 10 3 * dbl 10 2 := by
  rw [dbl_eq, dbl_eq, dbl_eq, dbl_eq, dbl_eq, dbl_eq, dbl_eq, dbl_eq,
    ← pow_add, ← pow_add, ← pow_add, ← pow_add, ← pow_add, ← pow_add, ← pow_add]
  norm_num

theorem pow10_170157 : (10:Nat)^170157 =
    dbl 10 17 * dbl 10 15 * dbl 10 12 * dbl 10 11 * dbl 10 7 * dbl 10 5 * dbl 10 3 * dbl 10 2 * 10 := by
  rw [dbl_eq, dbl_eq, dbl_eq, dbl_eq, dbl_eq, dbl_eq, dbl_eq, dbl_eq,
    ← pow_add, ← pow_add, ← pow_add, ← pow_add, ← pow_add, ← pow_add, ← pow_add]
  norm_num
  rw [pow_succ]

/-- The largest fitting value is strictly below `10^170157`. -/
theorem numeric_upper : (2:Nat)^565248 < 10^170157 := by
  rw [pow2_565248, pow10_170157]
  norm_num [dbl]

/-- `10^170156` is strictly below `2^565248`, hence at most `maximum = 2^565248 - 1`. -/
theorem numeric_lower : (10:Nat)^170156 < 2^565248 := by
  rw [pow2_565248, pow10_170156]
  norm_num [dbl]

theorem maximum_eq : maximum = 2^565248 - 1 := by
  unfold maximum
  rw [bits_eq]

theorem fitbits_lt (H : Nat) (hH : FitsBits bits H) : H < 2^565248 := by
  unfold FitsBits at hH
  rw [bits_eq] at hH
  exact hH

theorem repair_statement : ∀ H : Nat, Audit_reddit_math_2s4u2m.FitsBits Audit_reddit_math_2s4u2m.bits H → Audit_reddit_math_2s4u2m.HasAtMostDecDigits H Audit_reddit_math_2s4u2m.digitBound := by
  intro H hH
  refine ⟨by decide, ?_⟩
  have h1 : H < 2^565248 := fitbits_lt H hH
  have h2 : (2:Nat)^565248 < 10^170157 := numeric_upper
  unfold digitBound
  exact lt_trans h1 h2

theorem repair_nonvacuous : Audit_reddit_math_2s4u2m.HasDecDigits Audit_reddit_math_2s4u2m.maximum Audit_reddit_math_2s4u2m.digitBound := by
  unfold HasDecDigits digitBound
  right
  refine ⟨by decide, ?_, ?_⟩
  · rw [maximum_eq]
    have h := numeric_lower
    omega
  · rw [maximum_eq]
    have h := numeric_upper
    omega

theorem final_theorem : (Nat.digits 10 Audit_reddit_math_2s4u2m.maximum).length = Audit_reddit_math_2s4u2m.digitBound ∧ ∀ H : Nat, Audit_reddit_math_2s4u2m.FitsBits Audit_reddit_math_2s4u2m.bits H → (Nat.digits 10 H).length ≤ Audit_reddit_math_2s4u2m.digitBound := by
  have hb : (1:Nat) < 10 := by decide
  constructor
  · have hle : (Nat.digits 10 maximum).length ≤ 170157 := by
      rw [Nat.digits_length_le_iff hb]
      rw [maximum_eq]
      have h := numeric_upper
      omega
    have hlt : 170156 < (Nat.digits 10 maximum).length := by
      rw [Nat.lt_digits_length_iff hb]
      rw [maximum_eq]
      have h := numeric_lower
      omega
    unfold digitBound
    omega
  · intro H hH
    rw [Nat.digits_length_le_iff hb]
    have h1 : H < 2^565248 := fitbits_lt H hH
    have h2 : (2:Nat)^565248 < 10^170157 := numeric_upper
    unfold digitBound
    exact lt_trans h1 h2

end Audit_reddit_math_2s4u2m
