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

theorem bits_eq : bits = 565248 := by decide

theorem upper_pow : (2 : Nat)^565248 ≤ 10^170157 := Nat.le_of_ble_eq_true rfl

theorem lower_pow : (10 : Nat)^170156 ≤ 2^565248 - 1 := Nat.le_of_ble_eq_true rfl

theorem max_lt : maximum < 10^170157 := by
  unfold maximum
  rw [bits_eq]
  have := upper_pow
  have hp : 0 < (2:Nat)^565248 := Nat.two_pow_pos _
  omega

theorem repair_statement : ∀ H : Nat, Audit_reddit_math_2s4u2m.FitsBits Audit_reddit_math_2s4u2m.bits H → Audit_reddit_math_2s4u2m.HasAtMostDecDigits H Audit_reddit_math_2s4u2m.digitBound := by
  intro H hH
  unfold FitsBits at hH
  rw [bits_eq] at hH
  refine ⟨by decide, ?_⟩
  show H < 10^170157
  exact Nat.lt_of_lt_of_le hH upper_pow

theorem repair_nonvacuous : Audit_reddit_math_2s4u2m.HasDecDigits Audit_reddit_math_2s4u2m.maximum Audit_reddit_math_2s4u2m.digitBound := by
  right
  refine ⟨by decide, ?_, max_lt⟩
  show 10^170156 ≤ maximum
  unfold maximum
  rw [bits_eq]
  exact lower_pow

theorem final_theorem : (Nat.digits 10 Audit_reddit_math_2s4u2m.maximum).length = Audit_reddit_math_2s4u2m.digitBound ∧ ∀ H : Nat, Audit_reddit_math_2s4u2m.FitsBits Audit_reddit_math_2s4u2m.bits H → (Nat.digits 10 H).length ≤ Audit_reddit_math_2s4u2m.digitBound := by
  refine ⟨?_, ?_⟩
  · show (Nat.digits 10 maximum).length = 170157
    have h1 : (Nat.digits 10 maximum).length ≤ 170157 :=
      (Nat.lt_base_pow_iff_digits_le 10 maximum 170157 (by norm_num)).mp max_lt
    have h2 : ¬ (Nat.digits 10 maximum).length ≤ 170156 := by
      intro h
      have := (Nat.lt_base_pow_iff_digits_le 10 maximum 170156 (by norm_num)).mpr h
      have hl : (10:Nat)^170156 ≤ maximum := by
        unfold maximum; rw [bits_eq]; exact lower_pow
      omega
    omega
  · intro H hH
    exact (Nat.lt_base_pow_iff_digits_le 10 H 170157 (by norm_num)).mp (repair_statement H hH).2

end Audit_reddit_math_2s4u2m
