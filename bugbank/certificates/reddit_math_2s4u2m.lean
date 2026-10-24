import Mathlib.Data.Nat.Digits.Lemmas
import Mathlib.Algebra.Order.Ring.Nat
import Mathlib.Tactic.NormNum
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.Ring
import Mathlib.Tactic.FinCases

/- Human-guided audit: The exact original upper bound and extremal 565248-bit witness are retained. Mathlib power/order lemmas replace hand-built induction and binary addition trees. The actual Hamlet integer is covered universally; it is never replaced by the extremal value.
   Original witness action: KEPT. -/
namespace Audit_reddit_math_2s4u2m
def payloadKiB : Nat := 69
def bytesPerKiB : Nat := 1024
def bitsPerByte : Nat := 8
def bits : Nat := payloadKiB * bytesPerKiB * bitsPerByte

def FitsBits (b n : Nat) : Prop := n < 2^b

/- The disjunction is definitionally small even when `n` is a named enormous
power. Its two branches are exactly the stipulated convention: zero has one
digit, and the usual two power thresholds characterize every positive value.
The lower threshold makes the second branch false for zero. -/
def HasDecDigits (n d : Nat) : Prop :=
  (n = 0 /\ d = 1) \/
  (0 < d /\ 10^(d - 1) <= n /\ n < 10^d)

/- For positive `d`, this is precisely the upper-threshold meaning of at most
`d` ordinary decimal digits. It includes zero. -/
def HasAtMostDecDigits (n d : Nat) : Prop := 0 < d /\ n < 10^d

def maximum : Nat := 2^bits - 1
def control : Nat := 10^389999

theorem bits_eq : bits = 565248 := by
  decide

theorem control_eq : control = 10^389999 := by
  rfl


abbrev pow_add_self := @pow_add ℕ _
abbrev pow_mul_self := @pow_mul ℕ _
abbrev mul_pow_self := @mul_pow ℕ _
lemma mul_lt_mul_left_of_pos (k : ℕ) (hk : 0 < k) {a b : ℕ} (h : a < b) : k*a < k*b := Nat.mul_lt_mul_of_pos_left h hk
lemma mul_lt_mul_right_of_pos (k : ℕ) (hk : 0 < k) {a b : ℕ} (h : a < b) : a*k < b*k := Nat.mul_lt_mul_of_pos_right h hk
lemma mul_le_mul_left_self (k : ℕ) {a b : ℕ} (h : a ≤ b) : k*a ≤ k*b := Nat.mul_le_mul_left k h
lemma mul_le_mul_right_self (k : ℕ) {a b : ℕ} (h : a ≤ b) : a*k ≤ b*k := Nat.mul_le_mul_right k h
lemma mul_lt_mul_strict {a b c d : ℕ} (h : a < b) (h' : c < d) : a*c < b*d := Nat.mul_lt_mul_of_lt_of_lt h h'
lemma cancel_mul_left_lt (k : ℕ) {a b : ℕ} (h : k*a < k*b) : a < b := Nat.lt_of_mul_lt_mul_left h
lemma pow_pos_self {a : ℕ} (h : 0 < a) (n : ℕ) : 0 < a^n := pow_pos h n
lemma pow_five_lt {a b : ℕ} (h : a < b) : a^5 < b^5 := Nat.pow_lt_pow_left h (by decide)
lemma pow_eight_lt {a b : ℕ} (h : a < b) : a^8 < b^8 := Nat.pow_lt_pow_left h (by decide)
lemma pow_eighteen_lt {a b : ℕ} (h : a < b) : a^18 < b^18 := Nat.pow_lt_pow_left h (by decide)
lemma pow_twentyeight_lt {a b : ℕ} (h : a < b) : a^28 < b^28 := Nat.pow_lt_pow_left h (by decide)
lemma pow_215_lt {a b : ℕ} (h : a < b) : a^215 < b^215 := Nat.pow_lt_pow_left h (by decide)
lemma pow_484_lt {a b : ℕ} (h : a < b) : a^484 < b^484 := Nat.pow_lt_pow_left h (by decide)
lemma pow_282624_lt {a b : ℕ} (h : a < b) : a^282624 < b^282624 := Nat.pow_lt_pow_left h (by decide)
/- Abstract scale cancellation packages the delicate arithmetic. Only the
small hypotheses supplied to these lemmas are decided by computation. -/
theorem scaled_five_tail_lt {a b c d x y : Nat}
    (hbase : c * a < d * b) (htail : d^5 * x < c^5 * y) :
    a^5 * x < b^5 * y := by
  have hp := mul_lt_mul_strict (pow_five_lt hbase) htail
  have hs : (c^5 * d^5) * (a^5 * x) <
      (c^5 * d^5) * (b^5 * y) := by
    calc
      (c^5 * d^5) * (a^5 * x) =
          (c * a)^5 * (d^5 * x) := by
        simp [mul_pow_self, Nat.mul_assoc, Nat.mul_comm, Nat.mul_left_comm]
      _ < (d * b)^5 * (c^5 * y) := hp
      _ = (c^5 * d^5) * (b^5 * y) := by
        simp [mul_pow_self, Nat.mul_assoc, Nat.mul_comm, Nat.mul_left_comm]
  exact cancel_mul_left_lt (c^5 * d^5) hs

theorem scaled_twentyeight_tail_lt {a b c d x y : Nat}
    (hbase : c * a < d * b) (htail : d^28 * x < c^28 * y) :
    a^28 * x < b^28 * y := by
  have hp := mul_lt_mul_strict (pow_twentyeight_lt hbase) htail
  have hs : (c^28 * d^28) * (a^28 * x) <
      (c^28 * d^28) * (b^28 * y) := by
    calc
      (c^28 * d^28) * (a^28 * x) =
          (c * a)^28 * (d^28 * x) := by
        simp [mul_pow_self, Nat.mul_assoc, Nat.mul_comm, Nat.mul_left_comm]
      _ < (d * b)^28 * (c^28 * y) := hp
      _ = (c^28 * d^28) * (b^28 * y) := by
        simp [mul_pow_self, Nat.mul_assoc, Nat.mul_comm, Nat.mul_left_comm]
  exact cancel_mul_left_lt (c^28 * d^28) hs

theorem pred_lt_of_pos (n : Nat) (h : 0 < n) : n - 1 < n := by
  cases n with
  | zero => nomatch h
  | succ n => simp

theorem cancel_double_lt {a b : Nat} (h : 2 * a < 2 * b) : a < b :=
  cancel_mul_left_lt 2 h

/- If two ordered values are doubled, the predecessor of the larger even
value is still strictly above the smaller even value. -/
theorem double_gap {a b : Nat} (h : a < b) : 2 * a < 2 * b - 1 := by
  cases b with
  | zero => nomatch h
  | succ b =>
      have hab : a <= b := Nat.le_of_succ_le_succ h
      have hd : 2 * a <= 2 * b := mul_le_mul_left_self 2 hab
      have hs : 2 * a < Nat.succ (2 * b) := Nat.lt_succ_of_le hd
      simpa [Nat.mul_succ, Nat.add_assoc, Nat.add_comm,
        Nat.add_left_comm] using hs

/- Lower certificate: 170156 = 351*484+272 and
565248 = 1166*484+904. -/
theorem lower_scaled_base : 251 * 10^59 < 250 * 2^196 := by
  decide

theorem lower_scaled_tail : 250^5 * 10^56 < 251^5 * 2^186 := by
  decide

theorem lower_block_main : 10^351 < 2^1166 := by
  have hsmall : (10^59)^5 * 10^56 < (2^196)^5 * 2^186 :=
    scaled_five_tail_lt lower_scaled_base lower_scaled_tail
  calc
    10^351 = (10^59)^5 * 10^56 := by
      rw [show 351 = 59 * 5 + 56 by decide, pow_add_self, pow_mul_self]
    _ < (2^196)^5 * 2^186 := hsmall
    _ = 2^1166 := by
      rw [show 1166 = 196 * 5 + 186 by decide, pow_add_self,
        pow_mul_self]

theorem lower_small_tail : 10^34 < 2^113 := by
  decide

theorem lower_block_tail : 10^272 < 2^904 := by
  have h := pow_eight_lt lower_small_tail
  calc
    10^272 = (10^34)^8 := by
      rw [show 272 = 34 * 8 by decide, pow_mul_self]
    _ < (2^113)^8 := h
    _ = 2^904 := by
      rw [show 904 = 113 * 8 by decide, pow_mul_self]

theorem lower_main_repeated : (10^351)^484 < (2^1166)^484 :=
  pow_484_lt lower_block_main

theorem lower_power_bound : 10^170156 < 2^565248 := by
  have hp := mul_lt_mul_strict lower_main_repeated lower_block_tail
  calc
    10^170156 = (10^351)^484 * 10^272 := by
      rw [show 170156 = 351 * 484 + 272 by decide,
        pow_add_self, pow_mul_self]
    _ < (2^1166)^484 * 2^904 := hp
    _ = 2^565248 := by
      rw [show 565248 = 1166 * 484 + 904 by decide,
        pow_add_self, pow_mul_self]

theorem tight_lower_bound : 10^170156 < maximum := by
  have hten : 2 * (5 * 10^170155) = 10^170156 := by
    calc
      2 * (5 * 10^170155) = 10 * 10^170155 := by
        rw [← Nat.mul_assoc]
      _ = 10^170155 * 10 := Nat.mul_comm _ _
      _ = 10^170156 := by
        rw [show 170156 = 170155 + 1 by decide, pow_add_self, pow_one]
  have htwo : 2 * 2^565247 = 2^565248 := by
    calc
      2 * 2^565247 = 2^565247 * 2 := Nat.mul_comm _ _
      _ = 2^565248 := by
        rw [show 565248 = 565247 + 1 by decide, pow_add_self, pow_one]
  have hfull : 2 * (5 * 10^170155) < 2 * 2^565247 := by
    calc
      2 * (5 * 10^170155) = 10^170156 := hten
      _ < 2^565248 := lower_power_bound
      _ = 2 * 2^565247 := htwo.symm
  have hhalf : 5 * 10^170155 < 2^565247 := cancel_double_lt hfull
  have hgap := double_gap hhalf
  rw [hten, htwo] at hgap
  simpa [maximum, bits_eq] using hgap

/- Upper certificate: 565248 = 2621*215+1733 and
170157 = 789*215+522. The first block is extremely tight. The two scale
checks retain the margin lost by the individually false inequality
`2^17 < 10^5`. -/
theorem upper_scaled_base : 1037 * 2^93 < 1027 * 10^28 := by
  decide

theorem upper_scaled_tail : 1027^28 * 2^17 < 1037^28 * 10^5 := by
  decide

theorem upper_block_main : 2^2621 < 10^789 := by
  have hsmall : (2^93)^28 * 2^17 < (10^28)^28 * 10^5 :=
    scaled_twentyeight_tail_lt upper_scaled_base upper_scaled_tail
  calc
    2^2621 = (2^93)^28 * 2^17 := by
      rw [show 2621 = 93 * 28 + 17 by decide, pow_add_self, pow_mul_self]
    _ < (10^28)^28 * 10^5 := hsmall
    _ = 10^789 := by
      rw [show 789 = 28 * 28 + 5 by decide, pow_add_self, pow_mul_self]

theorem upper_small_main : 2^93 < 10^28 := by
  decide

theorem upper_small_tail : 2^59 < 10^18 := by
  decide

theorem upper_block_tail : 2^1733 < 10^522 := by
  have hp := mul_lt_mul_strict (pow_eighteen_lt upper_small_main)
    upper_small_tail
  calc
    2^1733 = (2^93)^18 * 2^59 := by
      rw [show 1733 = 93 * 18 + 59 by decide, pow_add_self, pow_mul_self]
    _ < (10^28)^18 * 10^18 := hp
    _ = 10^522 := by
      rw [show 522 = 28 * 18 + 18 by decide, pow_add_self, pow_mul_self]

theorem upper_main_repeated : (2^2621)^215 < (10^789)^215 :=
  pow_215_lt upper_block_main

theorem upper_power_bound : 2^565248 < 10^170157 := by
  have hp := mul_lt_mul_strict upper_main_repeated upper_block_tail
  calc
    2^565248 = (2^2621)^215 * 2^1733 := by
      rw [show 565248 = 2621 * 215 + 1733 by decide,
        pow_add_self, pow_mul_self]
    _ < (10^789)^215 * 10^522 := hp
    _ = 10^170157 := by
      rw [show 170157 = 789 * 215 + 522 by decide,
        pow_add_self, pow_mul_self]

/- Strict monotonicity of decimal powers, proved without recursion over either
of the two exponents used at its call sites. -/
theorem decimal_pow_lt_add (m k : Nat) (hk : 0 < k) :
    10^m < 10^(m + k) := by
  have hm : 0 < 10^m := pow_pos_self (by decide) m
  have hkpow : 1 < 10^k := by
    cases k with
    | zero => nomatch hk
    | succ n =>
        have hn : 0 < 10^n := pow_pos_self (by decide) n
        have hone : 1 <= 10^n := hn
        rw [Nat.pow_succ]
        exact Nat.lt_of_lt_of_le (by decide)
          (mul_le_mul_right_self 10 hone)
  rw [pow_add_self]
  simpa using mul_lt_mul_left_of_pos (10^m) hm hkpow

theorem maximum_fits : FitsBits bits maximum := by
  unfold FitsBits maximum
  exact pred_lt_of_pos (2^bits) (pow_pos_self (by decide) bits)

theorem maximum_upper_bound : maximum < 10^170157 := by
  exact Nat.lt_trans maximum_fits
    (by simpa [bits_eq] using upper_power_bound)

theorem maximum_has_170157_digits : HasDecDigits maximum 170157 := by
  apply Or.inr
  exact And.intro (by decide)
    (And.intro (Nat.le_of_lt tight_lower_bound) maximum_upper_bound)

theorem every_fitting_value_below_170157_digits (H : Nat)
    (hH : FitsBits bits H) : H < 10^170157 := by
  exact Nat.lt_trans hH
    (by simpa [bits_eq] using upper_power_bound)

theorem every_fitting_value_has_at_most_170157_digits (H : Nat)
    (hH : FitsBits bits H) : HasAtMostDecDigits H 170157 :=
  And.intro (by decide) (every_fitting_value_below_170157_digits H hH)

theorem control_power_threshold_strict : 10^170157 < control := by
  calc
    10^170157 < 10^(170157 + 219842) :=
      decimal_pow_lt_add 170157 219842 (by decide)
    _ = 10^389999 :=
      congrArg (fun e : Nat => 10^e) (by decide)
    _ = control := control_eq.symm

theorem no_fitting_value_has_390000_digits (H : Nat)
    (hH : FitsBits bits H) : Not (HasDecDigits H 390000) := by
  intro hd
  have hu := every_fitting_value_below_170157_digits H hH
  cases hd with
  | inl hz =>
      exact (by decide : Not (390000 = 1)) hz.2
  | inr hpositive =>
      have hpow : 10^389999 <= H := by
        exact Nat.le_trans
          (Nat.le_of_eq (congrArg (fun e : Nat => 10^e)
            (show 389999 = 390000 - 1 by decide))) hpositive.2.1
      have hcH : control <= H :=
        Nat.le_trans (Nat.le_of_eq control_eq) hpow
      exact Nat.not_lt_of_ge
        (Nat.le_trans (Nat.le_of_lt control_power_threshold_strict) hcH) hu

abbrev PublishedDecimalConversionAt (H : Nat) : Prop :=
  FitsBits bits H -> HasDecDigits H 390000

/- Load-bearing refutation. `maximum` is only the extremal unsigned value;
the universal conjuncts apply to Hamlet's actual encoded value. -/
theorem reddit_math_2s4u2m_load_bearing_refutation :
    bits = 565248 /\
    maximum = 2^bits - 1 /\
    FitsBits bits maximum /\
    10^170156 < maximum /\
    maximum < 10^170157 /\
    HasDecDigits maximum 170157 /\
    (forall H, FitsBits bits H -> H < 10^170157) /\
    (forall H, FitsBits bits H -> HasAtMostDecDigits H 170157) /\
    (forall H, FitsBits bits H -> Not (HasDecDigits H 390000)) /\
    Not (PublishedDecimalConversionAt maximum) := by
  constructor
  · exact bits_eq
  constructor
  · rfl
  constructor
  · exact maximum_fits
  constructor
  · exact tight_lower_bound
  constructor
  · exact maximum_upper_bound
  constructor
  · exact maximum_has_170157_digits
  constructor
  · exact every_fitting_value_below_170157_digits
  constructor
  · exact every_fitting_value_has_at_most_170157_digits
  constructor
  · exact no_fitting_value_has_390000_digits
  · intro hclaim
    exact no_fitting_value_has_390000_digits maximum maximum_fits
      (hclaim maximum_fits)

theorem control_has_390000_digits : HasDecDigits control 390000 := by
  apply Or.inr
  have hl : 10^(390000 - 1) <= control := by
    exact Nat.le_of_eq (Eq.trans
      (congrArg (fun e : Nat => 10^e)
        (show 390000 - 1 = 389999 by decide)) control_eq.symm)
  have hu : control < 10^390000 := by
    calc
      control = 10^389999 := control_eq
      _ < 10^(389999 + 1) := decimal_pow_lt_add 389999 1 (by decide)
      _ = 10^390000 :=
        congrArg (fun e : Nat => 10^e) (by decide)
  exact And.intro (by decide) (And.intro hl hu)

/- Route review's width comparison is exposed literally: `565248` is twice
`282624`, and `2^2 < 10`. The repetition is the fixed addition tree above,
not a 282624-deep induction. -/
theorem width_block_comparison : 2^2 < 10 := by
  decide

theorem width_block_repeated : (2^2)^282624 < 10^282624 :=
  pow_282624_lt width_block_comparison

theorem bits_pair_decomposition : bits = 2 * 282624 :=
  Eq.trans bits_eq (by decide)

theorem control_width_lower_bound : 2^bits < 10^282624 := by
  calc
    2^bits = 2^(2 * 282624) :=
      congrArg (fun e : Nat => 2^e) bits_pair_decomposition
    _ = (2^2)^282624 := pow_mul_self 2 2 282624
    _ < 10^282624 := width_block_repeated

theorem control_power_threshold : 10^282624 < control := by
  calc
    10^282624 < 10^(282624 + 107375) :=
      decimal_pow_lt_add 282624 107375 (by decide)
    _ = 10^389999 :=
      congrArg (fun e : Nat => 10^e) (by decide)
    _ = control := control_eq.symm

theorem control_power_threshold_le : 10^282624 <= control :=
  Nat.le_of_lt control_power_threshold

theorem control_does_not_fit : Not (FitsBits bits control) := by
  intro hfit
  have htooLarge : 2^bits < control :=
    Nat.lt_trans control_width_lower_bound control_power_threshold
  exact Nat.not_lt_of_ge (Nat.le_of_lt htooLarge) hfit

/- Meaningful negative control: the digit predicate accepts a genuine
390000-digit value, while the material 565248-bit premise rejects it. -/
theorem reddit_math_2s4u2m_negative_control :
    control = 10^389999 /\
    HasDecDigits control 390000 /\
    bits = 2 * 282624 /\
    2^2 < 10 /\
    282624 < 389999 /\
    2^bits < 10^282624 /\
    10^282624 < control /\
    10^282624 <= control /\
    Not (FitsBits bits control) := by
  constructor
  · exact control_eq
  constructor
  · exact control_has_390000_digits
  constructor
  · exact bits_pair_decomposition
  constructor
  · exact width_block_comparison
  constructor
  · decide
  constructor
  · exact control_width_lower_bound
  constructor
  · exact control_power_threshold
  constructor
  · exact control_power_threshold_le
  · exact control_does_not_fit


theorem certificate_thresholds : HasDecDigits maximum 170157 ∧ (∀ H : ℕ, FitsBits bits H → HasAtMostDecDigits H 170157) := ⟨maximum_has_170157_digits, every_fitting_value_has_at_most_170157_digits⟩
theorem certificate : (Nat.digits 10 maximum).length = 170157 ∧
    ∀ H : ℕ, FitsBits bits H → (Nat.digits 10 H).length ≤ 170157 := by
  have hu : (Nat.digits 10 maximum).length ≤ 170157 :=
    (Nat.digits_length_le_iff (by decide : 1 < 10) maximum).2 maximum_upper_bound
  have hl : 170156 < (Nat.digits 10 maximum).length :=
    (Nat.lt_digits_length_iff (by decide : 1 < 10) maximum).2 (Nat.le_of_lt tight_lower_bound)
  refine ⟨by omega, ?_⟩
  intro H hH
  exact (Nat.digits_length_le_iff (by decide : 1 < 10) H).2
    (every_fitting_value_below_170157_digits H hH)
end Audit_reddit_math_2s4u2m
