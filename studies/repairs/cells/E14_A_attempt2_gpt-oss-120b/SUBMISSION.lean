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

theorem repair_statement : ∀ H : Nat,
    Audit_reddit_math_2s4u2m.FitsBits Audit_reddit_math_2s4u2m.bits H →
    Audit_reddit_math_2s4u2m.HasAtMostDecDigits H Audit_reddit_math_2s4u2m.digitBound :=
by
  intro H hFit
  have hpos : 0 < digitBound := by decide
  have hle : (2 : Nat) ^ bits ≤ 10 ^ digitBound := by decide
  have hbound : H < 10 ^ digitBound := Nat.lt_of_lt_of_le hFit hle
  exact ⟨hpos, hbound⟩

theorem repair_nonvacuous :
    Audit_reddit_math_2s4u2m.HasDecDigits Audit_reddit_math_2s4u2m.maximum Audit_reddit_math_2s4u2m.digitBound :=
by
  right
  have hpos : 0 < digitBound := by decide
  have hlow : 10 ^ (digitBound - 1) ≤ maximum := by decide
  have hle : (2 : Nat) ^ bits ≤ 10 ^ digitBound := by decide
  have hsucc : maximum.succ ≤ 10 ^ digitBound := by
    simpa [maximum, Nat.succ_sub_one] using hle
  have hhigh : maximum < 10 ^ digitBound := Nat.lt_of_succ_le hsucc
  exact ⟨hpos, hlow, hhigh⟩

-- CANNOT: unable to relate `HasDecDigits` to `Nat.digits` length without heavy computation
-- final_theorem : (Nat.digits 10 Audit_reddit_math_2s4u2m.maximum).length = Audit_reddit_math_2s4u2m.digitBound ∧ ∀ H : Nat, Audit_reddit_math_2s4u2m.FitsBits Audit_reddit_math_2s4u2m.bits H → (Nat.digits 10 H).length ≤ Audit_reddit_math_2s4u2m.digitBound

end Audit_reddit_math_2s4u2m
