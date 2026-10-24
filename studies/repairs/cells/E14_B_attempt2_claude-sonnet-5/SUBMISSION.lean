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

/-- Binary decomposition of `2^565248` into pieces with small (≤ 256) stated exponents, avoiding the
elaborator's large-exponent evaluation guard. -/
theorem two_pow_eq : (2:Nat)^565248 = (((2:Nat)^256)^256)^8 * ((2:Nat)^256)^160 := by
  rw [show (565248:Nat) = 256*(256*8+160) from by norm_num, pow_mul, pow_add, pow_mul]

/-- Same decomposition for `10^170157`. -/
theorem ten_pow_173_eq : (10:Nat)^170157 = (((10:Nat)^256)^256)^2 * ((10:Nat)^256)^152 * (10:Nat)^173 := by
  rw [show (170157:Nat) = 256*(256*2+152)+173 from by norm_num, pow_add, pow_mul, pow_add, pow_mul]

/-- Same decomposition for `10^170156`. -/
theorem ten_pow_172_eq : (10:Nat)^170156 = (((10:Nat)^256)^256)^2 * ((10:Nat)^256)^152 * (10:Nat)^172 := by
  rw [show (170156:Nat) = 256*(256*2+152)+172 from by norm_num, pow_add, pow_mul, pow_add, pow_mul]

/-- The key numeric fact: `2^565248 < 10^170157`. -/
theorem check_hi : (2:Nat)^565248 < 10^170157 := by
  rw [two_pow_eq, ten_pow_173_eq]
  norm_num

/-- The key numeric fact: `10^170156 ≤ 2^565248 - 1`. -/
theorem check_lo : (10:Nat)^170156 ≤ 2^565248 - 1 := by
  rw [two_pow_eq, ten_pow_172_eq]
  norm_num

theorem bits_eq : bits = 565248 := by decide

theorem maximum_eq : maximum = 2^565248 - 1 := by
  unfold maximum
  rw [bits_eq]

theorem maximum_lt : maximum < 10^170157 := by
  rw [maximum_eq]
  have h2 : (2:Nat)^565248 - 1 < 2^565248 := by
    have : 0 < (2:Nat)^565248 := Nat.two_pow_pos _
    omega
  exact Nat.lt_trans h2 check_hi

theorem maximum_ge : (10:Nat)^170156 ≤ maximum := by
  rw [maximum_eq]
  exact check_lo

theorem fitting_lt (H : Nat) (hH : FitsBits bits H) : H < 10^170157 := by
  unfold FitsBits at hH
  rw [bits_eq] at hH
  exact Nat.lt_trans hH check_hi

-- ===== OBLIGATIONS =====

theorem repair_statement : ∀ H : Nat, Audit_reddit_math_2s4u2m.FitsBits Audit_reddit_math_2s4u2m.bits H → Audit_reddit_math_2s4u2m.HasAtMostDecDigits H Audit_reddit_math_2s4u2m.digitBound := by
  intro H hH
  refine ⟨by decide, ?_⟩
  exact fitting_lt H hH

theorem repair_nonvacuous : Audit_reddit_math_2s4u2m.HasDecDigits Audit_reddit_math_2s4u2m.maximum Audit_reddit_math_2s4u2m.digitBound := by
  apply Or.inr
  refine ⟨by decide, maximum_ge, maximum_lt⟩

theorem final_theorem : (Nat.digits 10 Audit_reddit_math_2s4u2m.maximum).length = Audit_reddit_math_2s4u2m.digitBound ∧ ∀ H : Nat, Audit_reddit_math_2s4u2m.FitsBits Audit_reddit_math_2s4u2m.bits H → (Nat.digits 10 H).length ≤ Audit_reddit_math_2s4u2m.digitBound := by
  constructor
  · have hle : (Nat.digits 10 maximum).length ≤ digitBound :=
      (Nat.digits_length_le_iff (by norm_num) maximum).mpr maximum_lt
    have hlt : digitBound - 1 < (Nat.digits 10 maximum).length :=
      (Nat.lt_digits_length_iff (by norm_num) maximum).mpr (by
        show (10:Nat)^(digitBound - 1) ≤ maximum
        norm_num [digitBound]
        exact maximum_ge)
    omega
  · intro H hH
    exact (Nat.digits_length_le_iff (by norm_num) H).mpr (fitting_lt H hH)

end Audit_reddit_math_2s4u2m
