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

/-- Repeated-squaring helper: `pw2 a k` computes `a ^ (2^k)` by `k` successive squarings, so
evaluating it only needs recursion depth `k` (not `2^k`). -/
def pw2 (a : Nat) : Nat → Nat
  | 0 => a
  | (k+1) => (pw2 a k) * (pw2 a k)

theorem pw2_eq (a k : Nat) : pw2 a k = a ^ (2^k) := by
  induction k with
  | zero => simp [pw2]
  | succ k ih =>
      show pw2 a k * pw2 a k = a ^ 2^(k+1)
      rw [ih, ← pow_add, ← two_mul, pow_succ']

/-- `2^565248` as a product of squaring-chain terms, matching the binary decomposition
`565248 = 2^19 + 2^15 + 2^13`. -/
theorem two_pow_bits_eq : (2:Nat)^565248 = pw2 2 19 * pw2 2 15 * pw2 2 13 := by
  rw [pw2_eq, pw2_eq, pw2_eq, ← pow_add, ← pow_add]; norm_num

/-- `10^170157` as a product of squaring-chain terms, matching the binary decomposition
`170157 = 2^17+2^15+2^12+2^11+2^7+2^5+2^3+2^2+2^0`. -/
theorem ten_pow_digitBound_eq :
    (10:Nat)^digitBound =
      pw2 10 17 * pw2 10 15 * pw2 10 12 * pw2 10 11 * pw2 10 7 * pw2 10 5 * pw2 10 3 * pw2 10 2 * pw2 10 0 := by
  show (10:Nat)^170157 = _
  rw [pw2_eq, pw2_eq, pw2_eq, pw2_eq, pw2_eq, pw2_eq, pw2_eq, pw2_eq, pw2_eq,
    ← pow_add, ← pow_add, ← pow_add, ← pow_add, ← pow_add, ← pow_add, ← pow_add, ← pow_add]
  norm_num

/-- `10^(digitBound - 1) = 10^170156` as a product of squaring-chain terms, matching the binary
decomposition `170156 = 2^17+2^15+2^12+2^11+2^7+2^5+2^3+2^2`. -/
theorem ten_pow_digitBound_pred_eq :
    (10:Nat)^(digitBound - 1) =
      pw2 10 17 * pw2 10 15 * pw2 10 12 * pw2 10 11 * pw2 10 7 * pw2 10 5 * pw2 10 3 * pw2 10 2 := by
  show (10:Nat)^170156 = _
  rw [pw2_eq, pw2_eq, pw2_eq, pw2_eq, pw2_eq, pw2_eq, pw2_eq, pw2_eq,
    ← pow_add, ← pow_add, ← pow_add, ← pow_add, ← pow_add, ← pow_add, ← pow_add]
  norm_num

theorem two_pow_bits_le : (2:Nat)^565248 ≤ 10^digitBound := by
  rw [two_pow_bits_eq, ten_pow_digitBound_eq]
  decide

theorem ten_pow_digitBound_pred_lt : (10:Nat)^(digitBound - 1) < 2^565248 := by
  rw [ten_pow_digitBound_pred_eq, two_pow_bits_eq]
  decide

theorem bits_eq : bits = 565248 := by
  simp [bits, payloadKiB, bytesPerKiB, bitsPerByte]

theorem digitBound_pos : 0 < digitBound := by
  simp [digitBound]

theorem digitBound_pred_succ : digitBound - 1 + 1 = digitBound := by
  simp [digitBound]

-- ===== OBLIGATIONS =====

theorem repair_statement : ∀ H : Nat, Audit_reddit_math_2s4u2m.FitsBits Audit_reddit_math_2s4u2m.bits H → Audit_reddit_math_2s4u2m.HasAtMostDecDigits H Audit_reddit_math_2s4u2m.digitBound := by
  intro H hH
  refine ⟨digitBound_pos, ?_⟩
  have : H < 2^565248 := by rw [← bits_eq]; exact hH
  exact lt_of_lt_of_le this two_pow_bits_le

theorem repair_nonvacuous : Audit_reddit_math_2s4u2m.HasDecDigits Audit_reddit_math_2s4u2m.maximum Audit_reddit_math_2s4u2m.digitBound := by
  right
  have hpos : 0 < (2:Nat)^bits := pow_pos (by norm_num) bits
  have hlow : (10:Nat)^(digitBound-1) < 2^bits := by rw [bits_eq]; exact ten_pow_digitBound_pred_lt
  have hupp : (2:Nat)^bits ≤ 10^digitBound := by rw [bits_eq]; exact two_pow_bits_le
  refine ⟨digitBound_pos, ?_, ?_⟩
  · show (10:Nat)^(digitBound-1) ≤ 2^bits - 1
    generalize (10:Nat)^(digitBound-1) = A at hlow ⊢
    generalize (2:Nat)^bits = B at hpos hlow hupp ⊢
    omega
  · show (2:Nat)^bits - 1 < 10^digitBound
    generalize (2:Nat)^bits = B at hpos hupp ⊢
    generalize (10:Nat)^digitBound = C at hupp ⊢
    omega

theorem maximum_ne_zero : maximum ≠ 0 := by
  have hb : 0 < bits := by simp [bits, payloadKiB, bytesPerKiB, bitsPerByte]
  have h1 : (2:Nat) ≤ 2^bits := by
    calc (2:Nat) = 2^1 := (pow_one 2).symm
    _ ≤ 2^bits := Nat.pow_le_pow_right (by norm_num) hb
  have h2 : (1:Nat) < 2^bits := by omega
  show (2:Nat)^bits - 1 ≠ 0
  exact (Nat.sub_pos_of_lt h2).ne'

theorem final_theorem : (Nat.digits 10 Audit_reddit_math_2s4u2m.maximum).length = Audit_reddit_math_2s4u2m.digitBound ∧ ∀ H : Nat, Audit_reddit_math_2s4u2m.FitsBits Audit_reddit_math_2s4u2m.bits H → (Nat.digits 10 H).length ≤ Audit_reddit_math_2s4u2m.digitBound := by
  have hb : (1:Nat) < 10 := by norm_num
  obtain ⟨_, hge, hlt2⟩ := repair_nonvacuous.resolve_left (fun h => maximum_ne_zero h.1)
  constructor
  · have hle : (Nat.digits 10 maximum).length ≤ digitBound := by
      rw [Nat.digits_length_le_iff hb]; exact hlt2
    have hlt : digitBound - 1 < (Nat.digits 10 maximum).length := by
      rw [Nat.lt_digits_length_iff hb]; exact hge
    omega
  · intro H hH
    rw [Nat.digits_length_le_iff hb]
    exact repair_statement H hH |>.2

end Audit_reddit_math_2s4u2m
