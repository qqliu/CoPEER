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

/-- Horner-scheme identity keeping every `pow` exponent small (`y`), so that big powers can be
built purely from small powers plus multiplication. -/
private lemma horner3 (a x y z w : Nat) : a ^ (x*y*y + z*y + w) = ((a^x)^y * a^z)^y * a^w := by
  simp [pow_add, pow_mul, mul_pow, mul_assoc]

private lemma bits_eq : bits = 565248 := by decide

private lemma pow2_565248_eq : (2:Nat)^565248 = ((2^56)^100 * 2^52)^100 * 2^48 := by
  rw [show (565248:Nat) = 56*100*100+52*100+48 from by norm_num]
  exact horner3 2 56 100 52 48

private lemma pow10_170157_eq : (10:Nat)^170157 = ((10^17)^100 * 10^1)^100 * 10^57 := by
  rw [show (170157:Nat) = 17*100*100+1*100+57 from by norm_num]
  exact horner3 10 17 100 1 57

private lemma pow10_170156_eq : (10:Nat)^170156 = ((10^17)^100 * 10^1)^100 * 10^56 := by
  rw [show (170156:Nat) = 17*100*100+1*100+56 from by norm_num]
  exact horner3 10 17 100 1 56

private lemma key_le : (2:Nat)^bits ≤ 10^170157 := by
  rw [bits_eq, pow2_565248_eq, pow10_170157_eq]
  norm_num

private lemma key_lt : (10:Nat)^170156 < 2^bits := by
  rw [bits_eq, pow2_565248_eq, pow10_170156_eq]
  norm_num

private lemma fits_lt (H : Nat) (hH : FitsBits bits H) : H < 10^digitBound := by
  have h2 : H < 2^bits := hH
  have := lt_of_lt_of_le h2 key_le
  simpa [digitBound] using this

private lemma max_lt : maximum < 10^digitBound := by
  have hpos : (0:Nat) < 2^bits := by positivity
  have hm : maximum < 2^bits := by
    unfold maximum
    omega
  have := lt_of_lt_of_le hm key_le
  simpa [digitBound] using this

private lemma max_ge : 10^(digitBound-1) ≤ maximum := by
  have h1 : (10:Nat)^170156 < 2^bits := key_lt
  have hm : (10:Nat)^170156 ≤ maximum := by
    unfold maximum
    omega
  simpa [digitBound] using hm

-- ===== OBLIGATIONS =====

theorem repair_statement : ∀ H : Nat, Audit_reddit_math_2s4u2m.FitsBits Audit_reddit_math_2s4u2m.bits H → Audit_reddit_math_2s4u2m.HasAtMostDecDigits H Audit_reddit_math_2s4u2m.digitBound := by
  intro H hH
  refine ⟨by norm_num [digitBound], fits_lt H hH⟩

theorem repair_nonvacuous : Audit_reddit_math_2s4u2m.HasDecDigits Audit_reddit_math_2s4u2m.maximum Audit_reddit_math_2s4u2m.digitBound := by
  refine Or.inr ⟨by norm_num [digitBound], max_ge, max_lt⟩

theorem final_theorem : (Nat.digits 10 Audit_reddit_math_2s4u2m.maximum).length = Audit_reddit_math_2s4u2m.digitBound ∧ ∀ H : Nat, Audit_reddit_math_2s4u2m.FitsBits Audit_reddit_math_2s4u2m.bits H → (Nat.digits 10 H).length ≤ Audit_reddit_math_2s4u2m.digitBound := by
  constructor
  · have hle : (Nat.digits 10 maximum).length ≤ digitBound :=
      (Nat.digits_length_le_iff (b := 10) (k := digitBound) (by norm_num) maximum).2 max_lt
    have hgt : digitBound - 1 < (Nat.digits 10 maximum).length :=
      (Nat.lt_digits_length_iff (b := 10) (k := digitBound - 1) (n := maximum) (by norm_num)).2 max_ge
    have hdpos : 0 < digitBound := by norm_num [digitBound]
    omega
  · intro H hH
    exact (Nat.digits_length_le_iff (b := 10) (k := digitBound) (by norm_num) H).2 (fits_lt H hH)

end Audit_reddit_math_2s4u2m
