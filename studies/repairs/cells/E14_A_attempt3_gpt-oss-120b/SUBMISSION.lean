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

/-! ### Obligations -/

theorem repair_statement :
    ∀ H : Nat,
      Audit_reddit_math_2s4u2m.FitsBits Audit_reddit_math_2s4u2m.bits H →
        Audit_reddit_math_2s4u2m.HasAtMostDecDigits H Audit_reddit_math_2s4u2m.digitBound :=
by
  intro H hfit
  have hlt : H < 2 ^ bits := hfit
  have hpow : 2 ^ bits ≤ 10 ^ digitBound := by
    decide
  have : H < 10 ^ digitBound := Nat.lt_of_lt_of_le hlt hpow
  exact ⟨by decide, this⟩

theorem repair_nonvacuous :
    Audit_reddit_math_2s4u2m.HasDecDigits
      Audit_reddit_math_2s4u2m.maximum
      Audit_reddit_math_2s4u2m.digitBound :=
by
  have hpow_le : 2 ^ bits ≤ 10 ^ digitBound := by
    decide
  have hpow_lt : 2 ^ bits < 10 ^ digitBound := Nat.lt_of_le_of_lt hpow_le (by
    have : (10 : Nat) ^ digitBound ≠ 2 ^ bits := by
      decide
    exact Nat.lt_of_le_of_ne (Nat.le_of_lt (by decide)) this)
  have hmax_lt : maximum < 10 ^ digitBound := by
    -- `maximum = 2 ^ bits - 1`
    have : maximum + 1 = 2 ^ bits := by
      unfold maximum
      ring
    have : maximum < 2 ^ bits := by
      have : maximum + 1 ≤ 2 ^ bits := by
        simpa [this] using Nat.le_succ (maximum)
      exact Nat.lt_of_succ_le this
    exact Nat.lt_of_lt_of_le this (Nat.le_of_lt hpow_lt)
  have hpow_ge : 10 ^ (digitBound - 1) ≤ 2 ^ bits := by
    have : (10 : Nat) ^ (digitBound - 1) < 10 ^ digitBound := Nat.pow_lt_pow_of_lt_left (by decide) _
    exact Nat.lt_of_lt_of_le this (by
      have : 2 ^ bits ≤ 10 ^ digitBound := hpow_le
      exact Nat.le_of_lt this)
  have hmax_ge : 10 ^ (digitBound - 1) ≤ maximum := by
    have : 10 ^ (digitBound - 1) ≤ 2 ^ bits := hpow_ge
    have : 10 ^ (digitBound - 1) ≤ maximum + 1 := by
      simpa [maximum, Nat.add_comm] using this
    exact Nat.le_of_lt_succ (Nat.lt_of_le_of_lt this (by decide))
  left
  right
  constructor
  · exact Nat.succ_pos _
  · exact ⟨by
      have : 0 < digitBound := by decide
      exact this, hmax_ge, hmax_lt⟩

theorem final_theorem :
    (Nat.digits 10 Audit_reddit_math_2s4u2m.maximum).length =
        Audit_reddit_math_2s4u2m.digitBound ∧
      ∀ H : Nat,
        Audit_reddit_math_2s4u2m.FitsBits Audit_reddit_math_2s4u2m.bits H →
          (Nat.digits 10 H).length ≤ Audit_reddit_math_2s4u2m.digitBound :=
by
  constructor
  · -- length of digits of `maximum`
    have hdec : Audit_reddit_math_2s4u2m.HasDecDigits maximum digitBound :=
      repair_nonvacuous
    rcases hdec with hzero | ⟨hpos, hlow, hhigh⟩
    · cases hzero
    · have : (Nat.digits 10 maximum).length = digitBound := by
        -- `Nat.digits` length equals `digitBound` for positive numbers with exact digit count
        have : (Nat.digits 10 maximum).length = Nat.succ (Nat.log 10 maximum) := by
          simpa [Nat.digits_len] using rfl
        have : Nat.log 10 maximum = digitBound - 1 := by
          apply Nat.log_eq_iff_pow_le_pow_succ.2
          exact ⟨hlow, hhigh⟩
        simpa [this, Nat.succ_sub_one] using this
      exact this
  · intro H hfit
    have hbound := repair_statement H hfit
    rcases hbound with ⟨hpos, hlt⟩
    exact Nat.le_of_lt hlt

SUBMITTED
