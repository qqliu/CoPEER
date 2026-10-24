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

theorem bits_value : bits = 565248 := by decide

theorem max_fits : maximum < 2^bits := by
  unfold maximum
  have hpos : 0 < 2^bits := Nat.two_pow_pos bits
  omega

abbrev pow_add_self := @pow_add ℕ _
abbrev pow_mul_self := @pow_mul ℕ _
abbrev mul_pow_self := @mul_pow ℕ _
theorem mul_lt_mul_strict {a b c d : ℕ} (h : a < b) (h2 : c < d) : a * c < b * d := Nat.mul_lt_mul_of_lt_of_lt h h2
theorem cancel_mul_left_lt (k : ℕ) {a b : ℕ} (h : k * a < k * b) : a < b := Nat.lt_of_mul_lt_mul_left h
theorem pow_five_lt {a b : ℕ} (h : a < b) : a^5 < b^5 := Nat.pow_lt_pow_left h (by decide)
theorem pow_eight_lt {a b : ℕ} (h : a < b) : a^8 < b^8 := Nat.pow_lt_pow_left h (by decide)
theorem pow_eighteen_lt {a b : ℕ} (h : a < b) : a^18 < b^18 := Nat.pow_lt_pow_left h (by decide)
theorem pow_twentyeight_lt {a b : ℕ} (h : a < b) : a^28 < b^28 := Nat.pow_lt_pow_left h (by decide)
theorem pow_215_lt {a b : ℕ} (h : a < b) : a^215 < b^215 := Nat.pow_lt_pow_left h (by decide)
theorem pow_484_lt {a b : ℕ} (h : a < b) : a^484 < b^484 := Nat.pow_lt_pow_left h (by decide)

theorem scaled_five_tail_lt {a b c d x y : ℕ} (hbase : c * a < d * b) (htail : d^5 * x < c^5 * y) :
    a^5 * x < b^5 * y := by
  have hp := mul_lt_mul_strict (pow_five_lt hbase) htail
  have hs : (c^5 * d^5) * (a^5 * x) < (c^5 * d^5) * (b^5 * y) := by
    calc
      (c^5 * d^5) * (a^5 * x) = (c * a)^5 * (d^5 * x) := by
        simp [mul_pow_self, Nat.mul_assoc, Nat.mul_comm, Nat.mul_left_comm]
      _ < (d * b)^5 * (c^5 * y) := hp
      _ = (c^5 * d^5) * (b^5 * y) := by
        simp [mul_pow_self, Nat.mul_assoc, Nat.mul_comm, Nat.mul_left_comm]
  exact cancel_mul_left_lt (c^5 * d^5) hs

theorem scaled_twentyeight_tail_lt {a b c d x y : ℕ} (hbase : c * a < d * b) (htail : d^28 * x < c^28 * y) :
    a^28 * x < b^28 * y := by
  have hp := mul_lt_mul_strict (pow_twentyeight_lt hbase) htail
  have hs : (c^28 * d^28) * (a^28 * x) < (c^28 * d^28) * (b^28 * y) := by
    calc
      (c^28 * d^28) * (a^28 * x) = (c * a)^28 * (d^28 * x) := by
        simp [mul_pow_self, Nat.mul_assoc, Nat.mul_comm, Nat.mul_left_comm]
      _ < (d * b)^28 * (c^28 * y) := hp
      _ = (c^28 * d^28) * (b^28 * y) := by
        simp [mul_pow_self, Nat.mul_assoc, Nat.mul_comm, Nat.mul_left_comm]
  exact cancel_mul_left_lt (c^28 * d^28) hs

theorem cancel_double_lt {a b : ℕ} (h : 2 * a < 2 * b) : a < b := cancel_mul_left_lt 2 h

theorem double_gap {a b : ℕ} (h : a < b) : 2 * a < 2 * b - 1 := by
  cases b with
  | zero => nomatch h
  | succ b =>
      have hab : a <= b := Nat.le_of_succ_le_succ h
      have hd : 2 * a <= 2 * b := Nat.mul_le_mul_left 2 hab
      have hs : 2 * a < Nat.succ (2 * b) := Nat.lt_succ_of_le hd
      simpa [Nat.mul_succ, Nat.add_assoc, Nat.add_comm, Nat.add_left_comm] using hs

-- lower block: 170156 = 351*484+272, 565248 = 1166*484+904
theorem lower_scaled_base : 251 * 10^59 < 250 * 2^196 := by decide
theorem lower_scaled_tail : 250^5 * 10^56 < 251^5 * 2^186 := by decide
theorem lower_block_main : 10^351 < 2^1166 := by
  have hsmall : (10^59)^5 * 10^56 < (2^196)^5 * 2^186 := scaled_five_tail_lt lower_scaled_base lower_scaled_tail
  calc
    10^351 = (10^59)^5 * 10^56 := by
      rw [show 351 = 59 * 5 + 56 by decide, pow_add_self, pow_mul_self]
    _ < (2^196)^5 * 2^186 := hsmall
    _ = 2^1166 := by
      rw [show 1166 = 196 * 5 + 186 by decide, pow_add_self, pow_mul_self]
theorem lower_small_tail : 10^34 < 2^113 := by decide
theorem lower_block_tail : 10^272 < 2^904 := by
  have h := pow_eight_lt lower_small_tail
  calc
    10^272 = (10^34)^8 := by rw [show 272 = 34 * 8 by decide, pow_mul_self]
    _ < (2^113)^8 := h
    _ = 2^904 := by rw [show 904 = 113 * 8 by decide, pow_mul_self]
theorem lower_main_repeated : (10^351)^484 < (2^1166)^484 := pow_484_lt lower_block_main
theorem lower_power_bound : 10^170156 < 2^565248 := by
  have hp := mul_lt_mul_strict lower_main_repeated lower_block_tail
  calc
    10^170156 = (10^351)^484 * 10^272 := by
      rw [show 170156 = 351 * 484 + 272 by decide, pow_add_self, pow_mul_self]
    _ < (2^1166)^484 * 2^904 := hp
    _ = 2^565248 := by
      rw [show 565248 = 1166 * 484 + 904 by decide, pow_add_self, pow_mul_self]
theorem tight_lower_bound : 10^170156 < maximum := by
  have hten : 2 * (5 * 10^170155) = 10^170156 := by
    calc
      2 * (5 * 10^170155) = 10 * 10^170155 := by rw [← Nat.mul_assoc]
      _ = 10^170155 * 10 := Nat.mul_comm _ _
      _ = 10^170156 := by rw [show 170156 = 170155 + 1 by decide, pow_add_self, pow_one]
  have htwo : 2 * 2^565247 = 2^565248 := by
    calc
      2 * 2^565247 = 2^565247 * 2 := Nat.mul_comm _ _
      _ = 2^565248 := by rw [show 565248 = 565247 + 1 by decide, pow_add_self, pow_one]
  have hfull : 2 * (5 * 10^170155) < 2 * 2^565247 := by
    calc
      2 * (5 * 10^170155) = 10^170156 := hten
      _ < 2^565248 := lower_power_bound
      _ = 2 * 2^565247 := htwo.symm
  have hhalf : 5 * 10^170155 < 2^565247 := cancel_double_lt hfull
  have hgap := double_gap hhalf
  rw [hten, htwo] at hgap
  simpa [maximum, bits_value] using hgap

-- upper block: 565248 = 2621*215+1733, 170157 = 789*215+522
theorem upper_scaled_base : 1037 * 2^93 < 1027 * 10^28 := by decide
theorem upper_scaled_tail : 1027^28 * 2^17 < 1037^28 * 10^5 := by decide
theorem upper_block_main : 2^2621 < 10^789 := by
  have hsmall : (2^93)^28 * 2^17 < (10^28)^28 * 10^5 := scaled_twentyeight_tail_lt upper_scaled_base upper_scaled_tail
  calc
    2^2621 = (2^93)^28 * 2^17 := by
      rw [show 2621 = 93 * 28 + 17 by decide, pow_add_self, pow_mul_self]
    _ < (10^28)^28 * 10^5 := hsmall
    _ = 10^789 := by
      rw [show 789 = 28 * 28 + 5 by decide, pow_add_self, pow_mul_self]
theorem upper_small_main : 2^93 < 10^28 := by decide
theorem upper_small_tail : 2^59 < 10^18 := by decide
theorem upper_block_tail : 2^1733 < 10^522 := by
  have hp := mul_lt_mul_strict (pow_eighteen_lt upper_small_main) upper_small_tail
  calc
    2^1733 = (2^93)^18 * 2^59 := by
      rw [show 1733 = 93 * 18 + 59 by decide, pow_add_self, pow_mul_self]
    _ < (10^28)^18 * 10^18 := hp
    _ = 10^522 := by
      rw [show 522 = 28 * 18 + 18 by decide, pow_add_self, pow_mul_self]
theorem upper_main_repeated : (2^2621)^215 < (10^789)^215 := pow_215_lt upper_block_main
theorem upper_power_bound : 2^565248 < 10^170157 := by
  have hp := mul_lt_mul_strict upper_main_repeated upper_block_tail
  calc
    2^565248 = (2^2621)^215 * 2^1733 := by
      rw [show 565248 = 2621 * 215 + 1733 by decide, pow_add_self, pow_mul_self]
    _ < (10^789)^215 * 10^522 := hp
    _ = 10^170157 := by
      rw [show 170157 = 789 * 215 + 522 by decide, pow_add_self, pow_mul_self]
theorem maximum_upper_bound : maximum < 10^170157 :=
  Nat.lt_trans max_fits (by simpa [bits_value] using upper_power_bound)

-- ===== OBLIGATIONS: keep the names and statements; replace each `sorry` by a proof =====
/-- Universal: every value fitting the source's bit budget has at most `digitBound` decimal digits. -/
theorem repair_statement : ∀ H : Nat, Audit_reddit_math_2s4u2m.FitsBits Audit_reddit_math_2s4u2m.bits H → Audit_reddit_math_2s4u2m.HasAtMostDecDigits H Audit_reddit_math_2s4u2m.digitBound := by
  intro H hH
  refine ⟨by decide, ?_⟩
  unfold FitsBits at hH
  rw [bits_value] at hH
  exact Nat.lt_trans hH upper_power_bound

/-- Non-vacuity (exactness): the bound is attained: the largest fitting value has exactly `digitBound` digits,
so no smaller count works and a merely loose upper bound is rejected. -/
theorem repair_nonvacuous : Audit_reddit_math_2s4u2m.HasDecDigits Audit_reddit_math_2s4u2m.maximum Audit_reddit_math_2s4u2m.digitBound := Or.inr ⟨by decide, Nat.le_of_lt tight_lower_bound, maximum_upper_bound⟩

/-- The endpoint of this record: the same count in Mathlib's own digit function: the largest fitting value has
exactly `digitBound` decimal digits and every fitting value has at most `digitBound`. If you cannot, replace this
declaration (this doc comment included) by the single line `-- CANNOT: <reason>`. -/
theorem final_theorem : (Nat.digits 10 Audit_reddit_math_2s4u2m.maximum).length = Audit_reddit_math_2s4u2m.digitBound ∧ ∀ H : Nat, Audit_reddit_math_2s4u2m.FitsBits Audit_reddit_math_2s4u2m.bits H → (Nat.digits 10 H).length ≤ Audit_reddit_math_2s4u2m.digitBound := by
  refine ⟨?_, ?_⟩
  · have hu : (Nat.digits 10 maximum).length ≤ digitBound :=
      (Nat.digits_length_le_iff (by decide : 1 < 10) maximum).2 (repair_statement maximum max_fits).2
    have hl : digitBound - 1 < (Nat.digits 10 maximum).length :=
      (Nat.lt_digits_length_iff (by decide : 1 < 10) maximum).2 (Nat.le_of_lt tight_lower_bound)
    omega
  · intro H hH
    exact (Nat.digits_length_le_iff (by decide : 1 < 10) H).2 (repair_statement H hH).2
-- ===== END OBLIGATIONS =====
end Audit_reddit_math_2s4u2m
