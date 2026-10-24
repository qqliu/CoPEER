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

theorem upper_pow : (2 : Nat)^565248 ≤ 10^170157 := by decide +kernel

theorem lower_pow : (10 : Nat)^170156 ≤ 2^565248 - 1 := by decide +kernel

theorem max_eq : maximum = 2^565248 - 1 := by
  unfold maximum; rw [bits_eq]

theorem max_lt : maximum < 10^170157 := by
  rw [max_eq]
  have := upper_pow
  have hpos : 0 < (2:Nat)^565248 := Nat.two_pow_pos _
  omega

theorem max_ge : 10^170156 ≤ maximum := by
  rw [max_eq]; exact lower_pow

theorem repair_statement : ∀ H : Nat, Audit_reddit_math_2s4u2m.FitsBits Audit_reddit_math_2s4u2m.bits H → Audit_reddit_math_2s4u2m.HasAtMostDecDigits H Audit_reddit_math_2s4u2m.digitBound := by
  intro H hH
  unfold FitsBits at hH
  rw [bits_eq] at hH
  refine ⟨by decide, ?_⟩
  show H < 10^170157
  exact Nat.lt_of_lt_of_le hH upper_pow

theorem repair_nonvacuous : Audit_reddit_math_2s4u2m.HasDecDigits Audit_reddit_math_2s4u2m.maximum Audit_reddit_math_2s4u2m.digitBound := by
  right
  refine ⟨by decide, ?_, ?_⟩
  · show 10^170156 ≤ maximum
    exact max_ge
  · exact max_lt

theorem final_theorem : (Nat.digits 10 Audit_reddit_math_2s4u2m.maximum).length = Audit_reddit_math_2s4u2m.digitBound ∧ ∀ H : Nat, Audit_reddit_math_2s4u2m.FitsBits Audit_reddit_math_2s4u2m.bits H → (Nat.digits 10 H).length ≤ Audit_reddit_math_2s4u2m.digitBound := by
  refine ⟨?_, ?_⟩
  · have h1 : (Nat.digits 10 maximum).length ≤ 170157 :=
      (Nat.digits_length_le_iff (by norm_num) _).2 max_lt
    have h2 : 170156 < (Nat.digits 10 maximum).length :=
      (Nat.lt_digits_length_iff (by norm_num) _).2 max_ge
    show _ = 170157
    omega
  · intro H hH
    exact (Nat.digits_length_le_iff (by norm_num) _).2 (repair_statement H hH).2

end Audit_reddit_math_2s4u2m
