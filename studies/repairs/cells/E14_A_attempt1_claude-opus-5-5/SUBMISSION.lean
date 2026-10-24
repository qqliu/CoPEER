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

theorem pow_lt_aux : 2 ^ 565248 ≤ 10 ^ 170157 := by decide +kernel

theorem pow_ge_aux : 10 ^ 170156 ≤ 2 ^ 565248 - 1 := by decide +kernel

theorem repair_statement : ∀ H : Nat, Audit_reddit_math_2s4u2m.FitsBits Audit_reddit_math_2s4u2m.bits H → Audit_reddit_math_2s4u2m.HasAtMostDecDigits H Audit_reddit_math_2s4u2m.digitBound := by
  intro H h
  unfold FitsBits at h
  rw [bits_eq] at h
  refine ⟨by decide, ?_⟩
  exact lt_of_lt_of_le h pow_lt_aux

theorem max_lt : maximum < 10 ^ 170157 := by
  unfold maximum
  rw [bits_eq]
  have := pow_lt_aux
  have : 0 < 2 ^ 565248 := by positivity
  omega

theorem max_ge : 10 ^ 170156 ≤ maximum := by
  unfold maximum
  rw [bits_eq]
  exact pow_ge_aux

theorem repair_nonvacuous : Audit_reddit_math_2s4u2m.HasDecDigits Audit_reddit_math_2s4u2m.maximum Audit_reddit_math_2s4u2m.digitBound := by
  right
  exact ⟨by decide, max_ge, max_lt⟩

theorem final_theorem : (Nat.digits 10 Audit_reddit_math_2s4u2m.maximum).length = Audit_reddit_math_2s4u2m.digitBound ∧ ∀ H : Nat, Audit_reddit_math_2s4u2m.FitsBits Audit_reddit_math_2s4u2m.bits H → (Nat.digits 10 H).length ≤ Audit_reddit_math_2s4u2m.digitBound := by
  refine ⟨?_, ?_⟩
  · have h1 : (Nat.digits 10 maximum).length ≤ 170157 :=
      (Nat.digits_length_le_iff (by norm_num) maximum).mpr max_lt
    have h2 : ¬ (Nat.digits 10 maximum).length ≤ 170156 := by
      intro h
      have := (Nat.digits_length_le_iff (by norm_num) maximum).mp h
      have := max_ge
      omega
    show _ = 170157
    omega
  · intro H h
    have := (repair_statement H h).2
    exact (Nat.digits_length_le_iff (by norm_num) H).mpr this

end Audit_reddit_math_2s4u2m
