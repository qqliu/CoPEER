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

theorem bits_eq : bits = 565248 := by
  unfold bits payloadKiB bytesPerKiB bitsPerByte; norm_num

theorem low_bound : 10 ^ 170156 ≤ maximum := by
  unfold maximum; rw [bits_eq]; decide +kernel

theorem high_bound : 2 ^ bits ≤ 10 ^ 170157 := by
  rw [bits_eq]; decide +kernel

theorem max_lt : maximum < 10 ^ digitBound := by
  have h := high_bound
  have hp : 0 < 2 ^ bits := by positivity
  unfold maximum digitBound; omega

theorem repair_statement : ∀ H : Nat, Audit_reddit_math_2s4u2m.FitsBits Audit_reddit_math_2s4u2m.bits H → Audit_reddit_math_2s4u2m.HasAtMostDecDigits H Audit_reddit_math_2s4u2m.digitBound := by
  intro H hH
  unfold FitsBits at hH
  have h := high_bound
  refine ⟨by unfold digitBound; norm_num, ?_⟩
  unfold digitBound; omega

theorem repair_nonvacuous : Audit_reddit_math_2s4u2m.HasDecDigits Audit_reddit_math_2s4u2m.maximum Audit_reddit_math_2s4u2m.digitBound := by
  right
  refine ⟨by unfold digitBound; norm_num, ?_, max_lt⟩
  exact low_bound

theorem final_theorem : (Nat.digits 10 Audit_reddit_math_2s4u2m.maximum).length = Audit_reddit_math_2s4u2m.digitBound ∧ ∀ H : Nat, Audit_reddit_math_2s4u2m.FitsBits Audit_reddit_math_2s4u2m.bits H → (Nat.digits 10 H).length ≤ Audit_reddit_math_2s4u2m.digitBound := by
  refine ⟨?_, ?_⟩
  · apply le_antisymm
    · exact (Nat.digits_length_le_iff (by norm_num) _).2 max_lt
    · by_contra hc
      have h1 : (Nat.digits 10 maximum).length ≤ 170156 := by
        unfold digitBound at hc; omega
      have h2 := (Nat.digits_length_le_iff (by norm_num) _).1 h1
      have := low_bound
      omega
  · intro H hH
    exact (Nat.digits_length_le_iff (by norm_num) _).2 (repair_statement H hH).2

end Audit_reddit_math_2s4u2m
