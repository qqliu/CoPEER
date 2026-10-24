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

/- Helper machinery: computing 2^565248 and 10^170157 / 10^170156 exactly, using only repeated
squaring (never taking `^` of a literal to a huge exponent directly), so that the comparisons
below are tractable for the kernel. -/

def cpow : Nat → Nat
  | 0 => 2
  | i+1 => cpow i * cpow i

def dpow : Nat → Nat
  | 0 => 10
  | i+1 => dpow i * dpow i

private lemma double_pow (a i : Nat) : a ^ (2^(i+1)) = a^(2^i) * a^(2^i) := by
  have h : (2:Nat)^(i+1) = 2^i + 2^i := by rw [pow_succ]; ring
  rw [h, pow_add]

private lemma cpow_eq : ∀ i, cpow i = (2:Nat)^(2^i)
  | 0 => by norm_num [cpow]
  | (i+1) => by
      show cpow i * cpow i = (2:Nat)^(2^(i+1))
      rw [cpow_eq i, ← double_pow 2 i]

private lemma dpow_eq : ∀ i, dpow i = (10:Nat)^(2^i)
  | 0 => by norm_num [dpow]
  | (i+1) => by
      show dpow i * dpow i = (10:Nat)^(2^(i+1))
      rw [dpow_eq i, ← double_pow 10 i]

private lemma pow2_565248 : (2:Nat)^565248 = cpow 19 * (cpow 15 * cpow 13) := by
  have hb : (565248:Nat) = 2^19 + (2^15 + 2^13) := by norm_num
  rw [hb, pow_add, pow_add, cpow_eq 19, cpow_eq 15, cpow_eq 13]

private lemma pow10_170157 : (10:Nat)^170157 =
    dpow 17 * (dpow 15 * (dpow 12 * (dpow 11 * (dpow 7 * (dpow 5 * (dpow 3 * (dpow 2 * dpow 0))))))) := by
  have h : (170157:Nat) = 2^17+(2^15+(2^12+(2^11+(2^7+(2^5+(2^3+(2^2+2^0))))))) := by norm_num
  rw [h, pow_add, pow_add, pow_add, pow_add, pow_add, pow_add, pow_add, pow_add,
    dpow_eq 17, dpow_eq 15, dpow_eq 12, dpow_eq 11, dpow_eq 7, dpow_eq 5, dpow_eq 3, dpow_eq 2, dpow_eq 0]

private lemma pow10_170156 : (10:Nat)^170156 =
    dpow 17 * (dpow 15 * (dpow 12 * (dpow 11 * (dpow 7 * (dpow 5 * (dpow 3 * dpow 2)))))) := by
  have h : (170156:Nat) = 2^17+(2^15+(2^12+(2^11+(2^7+(2^5+(2^3+2^2)))))) := by norm_num
  rw [h, pow_add, pow_add, pow_add, pow_add, pow_add, pow_add, pow_add,
    dpow_eq 17, dpow_eq 15, dpow_eq 12, dpow_eq 11, dpow_eq 7, dpow_eq 5, dpow_eq 3, dpow_eq 2]

private lemma key_le : (2:Nat)^565248 ≤ (10:Nat)^170157 := by
  rw [pow2_565248, pow10_170157]
  decide

private lemma key_lt : (10:Nat)^170156 < (2:Nat)^565248 := by
  rw [pow2_565248, pow10_170156]
  decide

private lemma bits_eq : bits = 565248 := by
  unfold bits payloadKiB bytesPerKiB bitsPerByte
  norm_num

-- ===== OBLIGATIONS =====

theorem repair_statement : ∀ H : Nat, Audit_reddit_math_2s4u2m.FitsBits Audit_reddit_math_2s4u2m.bits H → Audit_reddit_math_2s4u2m.HasAtMostDecDigits H Audit_reddit_math_2s4u2m.digitBound := by
  intro H hH
  unfold FitsBits at hH
  rw [bits_eq] at hH
  refine ⟨by norm_num [digitBound], ?_⟩
  calc H < 2^565248 := hH
    _ ≤ 10^170157 := key_le
    _ = 10^digitBound := by norm_num [digitBound]

theorem repair_nonvacuous : Audit_reddit_math_2s4u2m.HasDecDigits Audit_reddit_math_2s4u2m.maximum Audit_reddit_math_2s4u2m.digitBound := by
  unfold HasDecDigits maximum
  right
  rw [bits_eq]
  refine ⟨by norm_num [digitBound], ?_, ?_⟩
  · show 10^(digitBound - 1) ≤ 2^565248 - 1
    have h1 : (10:Nat)^170156 < 2^565248 := key_lt
    have h2 : digitBound - 1 = 170156 := by norm_num [digitBound]
    rw [h2]
    omega
  · show 2^565248 - 1 < 10^digitBound
    have h1 : (2:Nat)^565248 ≤ 10^170157 := key_le
    have h2 : digitBound = 170157 := by norm_num [digitBound]
    rw [h2]
    omega

theorem final_theorem : (Nat.digits 10 Audit_reddit_math_2s4u2m.maximum).length = Audit_reddit_math_2s4u2m.digitBound ∧ ∀ H : Nat, Audit_reddit_math_2s4u2m.FitsBits Audit_reddit_math_2s4u2m.bits H → (Nat.digits 10 H).length ≤ Audit_reddit_math_2s4u2m.digitBound := by
  have hmax_fits : FitsBits bits maximum := by
    unfold FitsBits maximum
    have : (0:Nat) < 2^bits := pow_pos (by norm_num) bits
    omega
  have hmax_bound := repair_statement maximum hmax_fits
  have hlen_le : (Nat.digits 10 maximum).length ≤ digitBound :=
    (Nat.digits_length_le_iff (by norm_num) maximum).mpr hmax_bound.2
  have hlen_gt : digitBound - 1 < (Nat.digits 10 maximum).length := by
    have hnv := repair_nonvacuous
    unfold HasDecDigits at hnv
    have hnv' : (0 < digitBound ∧ 10^(digitBound-1) ≤ maximum ∧ maximum < 10^digitBound) := by
      rcases hnv with h | h
      · exact absurd h.2 (by norm_num [digitBound])
      · exact h
    exact (Nat.lt_digits_length_iff (by norm_num) maximum).mpr hnv'.2.1
  have : (Nat.digits 10 maximum).length = digitBound := by omega
  refine ⟨this, ?_⟩
  intro H hH
  have hB := repair_statement H hH
  exact (Nat.digits_length_le_iff (by norm_num) H).mpr hB.2

end Audit_reddit_math_2s4u2m
