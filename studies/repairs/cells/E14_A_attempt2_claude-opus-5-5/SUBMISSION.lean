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

theorem upper_aux : 2 ^ bits ≤ 10 ^ digitBound := by decide +kernel

theorem lower_aux : 10 ^ (digitBound - 1) ≤ maximum := by decide +kernel

theorem repair_statement : ∀ H : Nat, Audit_reddit_math_2s4u2m.FitsBits Audit_reddit_math_2s4u2m.bits H → Audit_reddit_math_2s4u2m.HasAtMostDecDigits H Audit_reddit_math_2s4u2m.digitBound := by
  intro H h
  exact ⟨by decide, lt_of_lt_of_le h upper_aux⟩

theorem max_lt : maximum < 10 ^ digitBound := by
  have h := upper_aux
  have : 0 < 2 ^ bits := by positivity
  unfold maximum; omega

theorem repair_nonvacuous : Audit_reddit_math_2s4u2m.HasDecDigits Audit_reddit_math_2s4u2m.maximum Audit_reddit_math_2s4u2m.digitBound := by
  exact Or.inr ⟨by decide, lower_aux, max_lt⟩

theorem final_theorem : (Nat.digits 10 Audit_reddit_math_2s4u2m.maximum).length = Audit_reddit_math_2s4u2m.digitBound ∧ ∀ H : Nat, Audit_reddit_math_2s4u2m.FitsBits Audit_reddit_math_2s4u2m.bits H → (Nat.digits 10 H).length ≤ Audit_reddit_math_2s4u2m.digitBound := by
  refine ⟨?_, ?_⟩
  · apply le_antisymm
    · exact (Nat.digits_length_le_iff (by norm_num) _).2 max_lt
    · by_contra hc
      have h1 : (Nat.digits 10 maximum).length ≤ digitBound - 1 := by
        have : digitBound = 170157 := rfl
        omega
      have h2 := (Nat.digits_length_le_iff (by norm_num) _).1 h1
      have := lower_aux
      omega
  · intro H h
    exact (Nat.digits_length_le_iff (by norm_num) _).2 (lt_of_lt_of_le h upper_aux)

end Audit_reddit_math_2s4u2m
