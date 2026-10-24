import Mathlib

/-!
# Where Long and Wagner's layered sets beat the bound (d - 1)/d, for ALL d

Lean 4.30.0 with Mathlib (rational arithmetic, finite sets). The list of constructs that certificates in
this repository must not contain was checked by a text scan recorded in `RECEIPT.json`; the axioms each
headline theorem depends on are printed by the `#print axioms` lines and recorded there as well.

## Part A (namespace `LayeredBoundary`): the arithmetic boundary

`g 1 = 1` and, for `P = 2 ^ l` with `1 ≤ l` and `1 ≤ m ≤ P`, `g (P + m - 1) = (1 + g m) / (2 * P)`
(`g_step`; every `d ≥ 2` is `P + m - 1` for exactly one such pair: `decomp`, `decomp_unique`).
`h d = d * g d`. Headline theorems, each for EVERY `d ≥ 2`:

* `h_lt_one_iff`  : `h d < 1 ↔ ¬ Exceptional d`, where `Exceptional d` says `d = 2 ^ k`, `d + 1 = 2 ^ k`
  or `d + 2 = 2 ^ k` for some `k`;
* `h_eq_one_iff`  : `h d = 1 ↔ IsPowTwo d`;
* `one_lt_h_iff`  : `1 < h d ↔ Exceptional d ∧ ¬ IsPowTwo d`;
* `density_gt_iff`, `density_eq_iff` : the same two statements for `1 - g d` against `(d - 1)/d`;
* `h_le_nine_eighths` : `h d ≤ 9 / 8` for every `d ≥ 1`.

Route. Cases (i), (ii), (iii) follow the written proof (closed forms at `m = 1`, `m = P`, `m = P - 1`).
In case (iv), `2 ≤ m ≤ P - 2`, the written proof splits into `m ≤ P/2 - 1` and `m = P - 2` and uses the
bound `h ≤ 9/8`; the formal proof instead carries the single invariant `d * h d ≤ d + 1`
(that is, `h d ≤ 1 + 1/d`) through the strong induction, which closes case (iv) without knowing which
`m` have `h m > 1`.

## Part A' (same namespace): the written proof's own steps, one by one

Every intermediate claim of the written proof, and its case (iv) as written (`written_case_iv`).
No step of the written proof was found to be wrong.

## Part B (namespace `LongWagner`): the link to the sets

Long and Wagner's layers `L_i`, their recursive set `C_d ⊆ Z_(2^n)` and the theorem
`card_C_iff_fits : |C_d| = (1 - g d) * 2 ^ n ↔ Fits n d`, where `Fits n d` says that no layer past `L_n`
is used; `fits_of_le : d ≤ n → Fits n d`.

NOT certified anywhere in this file: that `C_d` contains no projective d-cube (Long and Wagner,
Theorem 1.10). That statement is cited, not formalised.
-/

namespace LayeredBoundary

/-- The missing density. `g 0 = g 1 = 1` (the value at 0 is never used). For `d ≥ 2`,
`g d = (1 + g (d - 2 ^ l + 1)) / (2 * 2 ^ l)` with `l = ⌊log₂ d⌋`. -/
def g (d : ℕ) : ℚ :=
  if h : d ≤ 1 then 1
  else (1 + g (d - 2 ^ Nat.log 2 d + 1)) / (2 * 2 ^ Nat.log 2 d)
termination_by d
decreasing_by
  have h2 : 2 ≤ d := by omega
  have hl : 1 ≤ Nat.log 2 d := Nat.log_pos (by norm_num) h2
  have hp : 2 ^ 1 ≤ 2 ^ Nat.log 2 d := Nat.pow_le_pow_right (by norm_num) hl
  have hle : 2 ^ Nat.log 2 d ≤ d := Nat.pow_log_le_self 2 (by omega)
  omega

/-- `h d = d * g d`; the layered set beats the bound `(d - 1)/d` iff `h d < 1`. -/
def h (d : ℕ) : ℚ := (d : ℚ) * g d

theorem g_one : g 1 = 1 := by
  rw [g]; simp

theorem two_le_two_pow {l : ℕ} (hl : 1 ≤ l) : 2 ≤ 2 ^ l := by
  calc 2 = 2 ^ 1 := by norm_num
    _ ≤ 2 ^ l := Nat.pow_le_pow_right (by norm_num) hl

/-- The unfolding equation in the form used by the paper. -/
theorem g_step (l m : ℕ) (hl : 1 ≤ l) (hm1 : 1 ≤ m) (hm : m ≤ 2 ^ l) :
    g (2 ^ l + m - 1) = (1 + g m) / (2 * 2 ^ l) := by
  have hP : 2 ≤ 2 ^ l := two_le_two_pow hl
  have hlog : Nat.log 2 (2 ^ l + m - 1) = l := by
    apply Nat.log_eq_of_pow_le_of_lt_pow
    · omega
    · rw [pow_succ]; omega
  have hd : ¬ (2 ^ l + m - 1 ≤ 1) := by omega
  rw [g, dif_neg hd, hlog]
  have : 2 ^ l + m - 1 - 2 ^ l + 1 = m := by omega
  rw [this]

/-- Every `d ≥ 2` is `2 ^ l + m - 1` with `1 ≤ l`, `1 ≤ m ≤ 2 ^ l`. -/
theorem decomp (d : ℕ) (hd : 2 ≤ d) :
    ∃ l m : ℕ, 1 ≤ l ∧ 1 ≤ m ∧ m ≤ 2 ^ l ∧ d = 2 ^ l + m - 1 := by
  refine ⟨Nat.log 2 d, d - 2 ^ Nat.log 2 d + 1, Nat.log_pos (by norm_num) hd, by omega, ?_, ?_⟩
  · have := Nat.lt_pow_succ_log_self (b := 2) (by norm_num) d
    rw [Nat.succ_eq_add_one, pow_succ] at this
    omega
  · have := Nat.pow_log_le_self 2 (x := d) (by omega)
    omega

/-- The pair is unique: `l = ⌊log₂ d⌋`. -/
theorem decomp_unique {l m l' m' : ℕ} (hm1 : 1 ≤ m) (hm : m ≤ 2 ^ l) (hm1' : 1 ≤ m') (hm' : m' ≤ 2 ^ l')
    (e : 2 ^ l + m - 1 = 2 ^ l' + m' - 1) : l = l' ∧ m = m' := by
  have h1 : Nat.log 2 (2 ^ l + m - 1) = l := by
    apply Nat.log_eq_of_pow_le_of_lt_pow
    · omega
    · rw [pow_succ]; omega
  have h2 : Nat.log 2 (2 ^ l' + m' - 1) = l' := by
    apply Nat.log_eq_of_pow_le_of_lt_pow
    · omega
    · rw [pow_succ]; omega
  have hl : l = l' := by rw [← h1, ← h2, e]
  subst hl
  exact ⟨rfl, by omega⟩

theorem cast_d (l m : ℕ) (hm1 : 1 ≤ m) : ((2 ^ l + m - 1 : ℕ) : ℚ) = (2 : ℚ) ^ l + m - 1 := by
  have hpos : 0 < 2 ^ l := Nat.two_pow_pos l
  have : 2 ^ l + m - 1 + 1 = 2 ^ l + m := by omega
  have h2 : (((2 ^ l + m - 1 : ℕ) : ℚ) + 1) = (2 : ℚ) ^ l + m := by exact_mod_cast this
  linarith

/-- `h (P + m - 1) = (P + m - 1) (1 + g m) / (2 P)`. -/
theorem h_step (l m : ℕ) (hl : 1 ≤ l) (hm1 : 1 ≤ m) (hm : m ≤ 2 ^ l) :
    h (2 ^ l + m - 1) = ((2 : ℚ) ^ l + m - 1) * ((1 + g m) / (2 * 2 ^ l)) := by
  rw [h, g_step l m hl hm1 hm, cast_d l m hm1]

/-! ### Closed forms -/

/-- (i) `g (2 ^ j) = 1 / 2 ^ j`. -/
theorem g_pow (j : ℕ) : g (2 ^ j) = 1 / 2 ^ j := by
  rcases Nat.eq_zero_or_pos j with rfl | hj
  · simpa using g_one
  · have := g_step j 1 hj le_rfl (Nat.one_le_two_pow)
    rw [g_one] at this
    have e : 2 ^ j + 1 - 1 = 2 ^ j := by simp
    rw [e] at this
    rw [this]
    have hP : (0 : ℚ) < 2 ^ j := by positivity
    field_simp
    ring

/-- (i) `h (2 ^ j) = 1`. -/
theorem h_pow (j : ℕ) : h (2 ^ j) = 1 := by
  rw [h, g_pow]
  have hP : (0 : ℚ) < 2 ^ j := by positivity
  push_cast
  field_simp

/-- `g (2 P - 1) = (1 + 1/P) / (2 P)` for `P = 2 ^ j`, `j ≥ 1`. -/
theorem g_two_pow_sub_one (j : ℕ) (hj : 1 ≤ j) :
    g (2 ^ j + 2 ^ j - 1) = (1 + 1 / 2 ^ j) / (2 * 2 ^ j) := by
  rw [g_step j (2 ^ j) hj Nat.one_le_two_pow le_rfl, g_pow]

/-! ### The inequality that closes case (iv) -/

theorem poly_ineq (P m : ℚ) (hm : 3 ≤ m) (hP : m + 2 ≤ P) (hP8 : 8 ≤ P) :
    (P + m - 1) * (m * m + m + 1) < 2 * P * (m * m) := by
  rcases le_or_gt 4 m with h4 | h4
  · nlinarith [mul_nonneg (sub_nonneg.mpr hP) (sub_nonneg.mpr h4),
      mul_nonneg (sub_nonneg.mpr h4) (sub_nonneg.mpr h4),
      mul_nonneg (mul_nonneg (sub_nonneg.mpr hP) (sub_nonneg.mpr h4)) (sub_nonneg.mpr h4)]
  · nlinarith [mul_nonneg (sub_nonneg.mpr hP8) (sub_nonneg.mpr hm),
      mul_nonneg (sub_nonneg.mpr hm) (sub_nonneg.mpr hm),
      mul_nonneg (mul_nonneg (sub_nonneg.mpr hP8) (sub_nonneg.mpr hm)) (sub_nonneg.mpr hm)]

/-- If `m² x ≤ m + 1` (that is, `h m ≤ 1 + 1/m` with `x = g m`), `3 ≤ m ≤ P - 2` and `P ≥ 8`, then
`(P + m - 1)(1 + x) < 2 P`, i.e. `h (P + m - 1) < 1`. -/
theorem key_ineq (P m x : ℚ) (hm : 3 ≤ m) (hP : m + 2 ≤ P) (hP8 : 8 ≤ P)
    (hx : m * m * x ≤ m + 1) : (P + m - 1) * (1 + x) < 2 * P := by
  have hmm : 0 < m * m := by nlinarith
  have hd : 0 < P + m - 1 := by linarith
  have h1 : (P + m - 1) * (m * m * x) ≤ (P + m - 1) * (m + 1) :=
    mul_le_mul_of_nonneg_left hx hd.le
  have h2 := poly_ineq P m hm hP hP8
  have h3 : (P + m - 1) * (1 + x) * (m * m) < 2 * P * (m * m) := by nlinarith
  exact lt_of_mul_lt_mul_right h3 hmm.le

/-! ### The four cases of the recursion step -/

/-- Invariant carried through the strong induction: `d * h d ≤ d + 1`, i.e. `h d ≤ 1 + 1/d`. -/
def Bound (d : ℕ) : Prop := (d : ℚ) * h d ≤ d + 1

/-- Rational arithmetic of case (ii): the value at `2P - 1`. -/
theorem val_ii (P : ℚ) (hP : 2 ≤ P) :
    (P + P - 1) * ((1 + 1 / P) / (2 * P)) = 1 + (P - 1) / (2 * P ^ 2) ∧
    1 < (P + P - 1) * ((1 + 1 / P) / (2 * P)) ∧
    (P + P - 1) * ((1 + 1 / P) / (2 * P)) ≤ 9 / 8 ∧
    (P + P - 1) * ((P + P - 1) * ((1 + 1 / P) / (2 * P))) ≤ (P + P - 1) + 1 := by
  have hP0 : 0 < P := by linarith
  have e : (P + P - 1) * ((1 + 1 / P) / (2 * P)) = 1 + (P - 1) / (2 * P ^ 2) := by
    field_simp
    ring
  have hq : 0 < 2 * P ^ 2 := by positivity
  refine ⟨e, ?_, ?_, ?_⟩
  · rw [e]
    have : 0 < (P - 1) / (2 * P ^ 2) := div_pos (by linarith) hq
    linarith
  · rw [e]
    have : (P - 1) / (2 * P ^ 2) ≤ 1 / 8 := by
      rw [div_le_iff₀ hq]
      nlinarith [sq_nonneg (P - 2)]
    linarith
  · rw [e]
    have : (P + P - 1) * ((P - 1) / (2 * P ^ 2)) ≤ 1 := by
      rw [← mul_div_assoc, div_le_iff₀ hq]
      nlinarith
    nlinarith

/-- Rational arithmetic of case (iii): the value at `2P - 2` with `P = 2Q`. -/
theorem val_iii (Q : ℚ) (hQ : 2 ≤ Q) :
    (2 * Q + (2 * Q - 1) - 1) * ((1 + (1 + 1 / Q) / (2 * Q)) / (2 * (2 * Q))) =
      1 + (Q - 1) / (4 * Q ^ 3) ∧
    1 < (2 * Q + (2 * Q - 1) - 1) * ((1 + (1 + 1 / Q) / (2 * Q)) / (2 * (2 * Q))) ∧
    (2 * Q + (2 * Q - 1) - 1) * ((1 + (1 + 1 / Q) / (2 * Q)) / (2 * (2 * Q))) ≤ 9 / 8 ∧
    (2 * Q + (2 * Q - 1) - 1) *
      ((2 * Q + (2 * Q - 1) - 1) * ((1 + (1 + 1 / Q) / (2 * Q)) / (2 * (2 * Q)))) ≤
      (2 * Q + (2 * Q - 1) - 1) + 1 := by
  have hQ0 : 0 < Q := by linarith
  have e : (2 * Q + (2 * Q - 1) - 1) * ((1 + (1 + 1 / Q) / (2 * Q)) / (2 * (2 * Q))) =
      1 + (Q - 1) / (4 * Q ^ 3) := by
    field_simp
    ring
  have hq : 0 < 4 * Q ^ 3 := by positivity
  refine ⟨e, ?_, ?_, ?_⟩
  · rw [e]
    have : 0 < (Q - 1) / (4 * Q ^ 3) := div_pos (by linarith) hq
    linarith
  · rw [e]
    have : (Q - 1) / (4 * Q ^ 3) ≤ 1 / 8 := by
      rw [div_le_iff₀ hq]
      nlinarith [mul_pos hQ0 hQ0, mul_pos (mul_pos hQ0 hQ0) hQ0]
    linarith
  · rw [e]
    have : (2 * Q + (2 * Q - 1) - 1) * ((Q - 1) / (4 * Q ^ 3)) ≤ 1 := by
      rw [← mul_div_assoc, div_le_iff₀ hq]
      nlinarith [mul_pos hQ0 hQ0, mul_pos (mul_pos hQ0 hQ0) hQ0]
    nlinarith

theorem two_pow_cast_ge (l : ℕ) (hl : 1 ≤ l) : (2 : ℚ) ≤ 2 ^ l := by
  exact_mod_cast two_le_two_pow hl

/-- Case (i): `m = 1`. -/
theorem case_i (l : ℕ) : h (2 ^ l + 1 - 1) = 1 ∧ Bound (2 ^ l + 1 - 1) := by
  have e : 2 ^ l + 1 - 1 = 2 ^ l := by simp
  rw [e, Bound, h_pow]
  exact ⟨rfl, by linarith⟩

/-- Case (ii): `m = P`, so `d = 2P - 1`. -/
theorem case_ii (l : ℕ) (hl : 1 ≤ l) :
    1 < h (2 ^ l + 2 ^ l - 1) ∧ h (2 ^ l + 2 ^ l - 1) ≤ 9 / 8 ∧ Bound (2 ^ l + 2 ^ l - 1) := by
  have hs := h_step l (2 ^ l) hl Nat.one_le_two_pow le_rfl
  rw [g_pow] at hs
  have hc := cast_d l (2 ^ l) Nat.one_le_two_pow
  push_cast at hs hc
  obtain ⟨_, h1, h2, h3⟩ := val_ii ((2 : ℚ) ^ l) (two_pow_cast_ge l hl)
  rw [Bound, hs, hc]
  exact ⟨h1, h2, h3⟩

/-- Case (iii): `m = P - 1` with `P = 2 ^ (j + 1)`, `j ≥ 1`, so `d = 2P - 2`. -/
theorem case_iii (j : ℕ) (hj : 1 ≤ j) :
    1 < h (2 ^ (j + 1) + (2 ^ (j + 1) - 1) - 1) ∧ h (2 ^ (j + 1) + (2 ^ (j + 1) - 1) - 1) ≤ 9 / 8 ∧
    Bound (2 ^ (j + 1) + (2 ^ (j + 1) - 1) - 1) := by
  have hQ : 2 ≤ 2 ^ j := two_le_two_pow hj
  have hm1 : 1 ≤ 2 ^ (j + 1) - 1 := by rw [pow_succ]; omega
  have hs := h_step (j + 1) (2 ^ (j + 1) - 1) (by omega) hm1 (by omega)
  have em : 2 ^ (j + 1) - 1 = 2 ^ j + 2 ^ j - 1 := by rw [pow_succ]; omega
  have hg : g (2 ^ (j + 1) - 1) = (1 + 1 / 2 ^ j) / (2 * 2 ^ j) := by
    rw [em]; exact g_two_pow_sub_one j hj
  have hmc : ((2 ^ (j + 1) - 1 : ℕ) : ℚ) = 2 * (2 : ℚ) ^ j - 1 := by
    have : 2 ^ (j + 1) - 1 + 1 = 2 * 2 ^ j := by rw [pow_succ]; omega
    have h2 : (((2 ^ (j + 1) - 1 : ℕ) : ℚ) + 1) = 2 * (2 : ℚ) ^ j := by exact_mod_cast this
    linarith
  have hc := cast_d (j + 1) (2 ^ (j + 1) - 1) hm1
  rw [hmc] at hc
  rw [hg, hmc] at hs
  have hp : (2 : ℚ) ^ (j + 1) = 2 * 2 ^ j := by rw [pow_succ]; ring
  rw [hp] at hs hc
  obtain ⟨_, h1, h2, h3⟩ := val_iii ((2 : ℚ) ^ j) (two_pow_cast_ge j hj)
  rw [Bound, hs, hc]
  exact ⟨h1, h2, h3⟩

/-- Case (iv): `2 ≤ m ≤ P - 2`. Uses the invariant at `m`. -/
theorem case_iv (l m : ℕ) (hl : 1 ≤ l) (hm2 : 2 ≤ m) (hm : m + 2 ≤ 2 ^ l) (hb : Bound m) :
    h (2 ^ l + m - 1) < 1 ∧ Bound (2 ^ l + m - 1) := by
  have hs := h_step l m hl (by omega) (by omega)
  have hP4 : (4 : ℚ) ≤ 2 ^ l := by
    have : 4 ≤ 2 ^ l := by omega
    exact_mod_cast this
  have hP0 : (0 : ℚ) < 2 * 2 ^ l := by positivity
  have hmq : (2 : ℚ) ≤ m := by exact_mod_cast hm2
  have hmP : (m : ℚ) + 2 ≤ 2 ^ l := by exact_mod_cast hm
  have hlt : h (2 ^ l + m - 1) < 1 := by
    rw [hs, ← mul_div_assoc, div_lt_one hP0]
    rcases Nat.lt_or_ge m 3 with h3 | h3
    · have hm_eq : m = 2 := by omega
      subst hm_eq
      have : g 2 = 1 / 2 := by simpa using g_pow 1
      rw [this]
      push_cast
      linarith
    · have hl3 : 3 ≤ l := by
        by_contra hc
        have : l = 1 ∨ l = 2 := by omega
        rcases this with rfl | rfl <;> norm_num at hm <;> omega
      have hP8n : 2 ^ 3 ≤ 2 ^ l := Nat.pow_le_pow_right (by norm_num) hl3
      have hP8 : (8 : ℚ) ≤ 2 ^ l := by
        have : 8 ≤ 2 ^ l := by simpa using hP8n
        exact_mod_cast this
      have hm3 : (3 : ℚ) ≤ m := by exact_mod_cast h3
      have hx : (m : ℚ) * m * g m ≤ m + 1 := by
        have := hb
        rw [Bound, h] at this
        linarith [this, mul_assoc (m : ℚ) m (g m)]
      exact key_ineq _ _ _ hm3 hmP hP8 hx
  refine ⟨hlt, ?_⟩
  rw [Bound]
  have hd0 : (0 : ℚ) ≤ ((2 ^ l + m - 1 : ℕ) : ℚ) := Nat.cast_nonneg _
  nlinarith

/-! ### The invariant holds for every d ≥ 1 -/

theorem bound_all : ∀ d : ℕ, 1 ≤ d → Bound d := by
  intro d
  induction d using Nat.strong_induction_on with
  | _ d ih =>
    intro hd1
    rcases Nat.lt_or_ge d 2 with hd | hd
    · have : d = 1 := by omega
      subst this
      rw [Bound, h, g_one]; norm_num
    · obtain ⟨l, m, hl, hm1, hm, rfl⟩ := decomp d hd
      have hP : 2 ≤ 2 ^ l := two_le_two_pow hl
      have hb : Bound m := ih m (by omega) hm1
      by_cases c1 : m = 1
      · subst c1; exact (case_i l).2
      by_cases c2 : m = 2 ^ l
      · subst c2; exact (case_ii l hl).2.2
      by_cases c3 : m + 1 = 2 ^ l
      · have hl2 : 2 ≤ l := by
          by_contra hc
          have : l = 1 := by omega
          subst this
          norm_num at c3
          omega
        obtain ⟨j, rfl⟩ : ∃ j, l = j + 1 := ⟨l - 1, by omega⟩
        have : m = 2 ^ (j + 1) - 1 := by omega
        subst this
        exact (case_iii j (by omega)).2.2
      · exact (case_iv l m hl (by omega) (by omega) hb).2

/-! ### Classification -/

/-- `d` is a power of two. -/
def IsPowTwo (d : ℕ) : Prop := ∃ k : ℕ, d = 2 ^ k

/-- `d` is of the form `2 ^ k`, `2 ^ k - 1` or `2 ^ k - 2`. -/
def Exceptional (d : ℕ) : Prop := ∃ k : ℕ, d = 2 ^ k ∨ d + 1 = 2 ^ k ∨ d + 2 = 2 ^ k

theorem IsPowTwo.exceptional {d : ℕ} (hd : IsPowTwo d) : Exceptional d := by
  obtain ⟨k, hk⟩ := hd
  exact ⟨k, Or.inl hk⟩

/-- Nothing strictly between `2 ^ l` and `2 ^ (l + 1)` is a power of two. -/
theorem not_pow_between {l x : ℕ} (h1 : 2 ^ l < x) (h2 : x < 2 ^ (l + 1)) : ¬ ∃ k : ℕ, x = 2 ^ k := by
  rintro ⟨k, rfl⟩
  have hlk : l < k := (Nat.pow_lt_pow_iff_right (by norm_num)).mp h1
  have : 2 ^ (l + 1) ≤ 2 ^ k := Nat.pow_le_pow_right (by norm_num) hlk
  omega

/-- The trichotomy, for every `d ≥ 2`. -/
theorem classify (d : ℕ) (hd : 2 ≤ d) :
    (IsPowTwo d ∧ h d = 1) ∨
    (Exceptional d ∧ ¬ IsPowTwo d ∧ 1 < h d ∧ h d ≤ 9 / 8) ∨
    (¬ Exceptional d ∧ h d < 1) := by
  obtain ⟨l, m, hl, hm1, hm, rfl⟩ := decomp d hd
  have hP : 2 ≤ 2 ^ l := two_le_two_pow hl
  have hpow : 2 ^ (l + 1) = 2 ^ l + 2 ^ l := by rw [pow_succ]; omega
  by_cases c1 : m = 1
  · subst c1
    exact Or.inl ⟨⟨l, by simp⟩, (case_i l).1⟩
  by_cases c2 : m = 2 ^ l
  · subst c2
    refine Or.inr (Or.inl ⟨⟨l + 1, Or.inr (Or.inl (by omega))⟩, ?_, (case_ii l hl).1, (case_ii l hl).2.1⟩)
    exact not_pow_between (l := l) (by omega) (by omega)
  by_cases c3 : m + 1 = 2 ^ l
  · have hl2 : 2 ≤ l := by
      by_contra hc
      have : l = 1 := by omega
      subst this
      norm_num at c3
      omega
    have hP4 : 2 ^ 2 ≤ 2 ^ l := Nat.pow_le_pow_right (by norm_num) hl2
    obtain ⟨j, rfl⟩ : ∃ j, l = j + 1 := ⟨l - 1, by omega⟩
    have hm_eq : m = 2 ^ (j + 1) - 1 := by omega
    subst hm_eq
    refine Or.inr (Or.inl ⟨⟨j + 1 + 1, Or.inr (Or.inr (by omega))⟩, ?_,
      (case_iii j (by omega)).1, (case_iii j (by omega)).2.1⟩)
    exact not_pow_between (l := j + 1) (by omega) (by omega)
  · refine Or.inr (Or.inr ⟨?_, (case_iv l m hl (by omega) (by omega) (bound_all m hm1)).1⟩)
    rintro ⟨k, hk | hk | hk⟩
    · exact not_pow_between (l := l) (x := 2 ^ l + m - 1) (by omega) (by omega) ⟨k, hk⟩
    · exact not_pow_between (l := l) (x := 2 ^ l + m - 1 + 1) (by omega) (by omega) ⟨k, hk⟩
    · exact not_pow_between (l := l) (x := 2 ^ l + m - 1 + 2) (by omega) (by omega) ⟨k, hk⟩

/-! ### Headline theorems (target A), for EVERY d ≥ 2 -/

/-- `h d < 1` iff `d` is not of the form `2 ^ k - 2`, `2 ^ k - 1` or `2 ^ k`. -/
theorem h_lt_one_iff (d : ℕ) (hd : 2 ≤ d) : h d < 1 ↔ ¬ Exceptional d := by
  rcases classify d hd with ⟨hp, he⟩ | ⟨hex, _, hgt, _⟩ | ⟨hne, hlt⟩
  · exact ⟨fun hlt => absurd hlt (by rw [he]; exact lt_irrefl _), fun hne => absurd hp.exceptional hne⟩
  · exact ⟨fun hlt => absurd (lt_trans hlt hgt) (lt_irrefl _), fun hne => absurd hex hne⟩
  · exact ⟨fun _ => hne, fun _ => hlt⟩

/-- `h d = 1` iff `d` is a power of two. -/
theorem h_eq_one_iff (d : ℕ) (hd : 2 ≤ d) : h d = 1 ↔ IsPowTwo d := by
  rcases classify d hd with ⟨hp, he⟩ | ⟨_, hnp, hgt, _⟩ | ⟨hne, hlt⟩
  · exact ⟨fun _ => hp, fun _ => he⟩
  · exact ⟨fun he => absurd hgt (by rw [he]; exact lt_irrefl _), fun hp => absurd hp hnp⟩
  · exact ⟨fun he => absurd hlt (by rw [he]; exact lt_irrefl _), fun hp => absurd hp.exceptional hne⟩

/-- `1 < h d` iff `d` is `2 ^ k - 1` or `2 ^ k - 2` without being a power of two. -/
theorem one_lt_h_iff (d : ℕ) (hd : 2 ≤ d) : 1 < h d ↔ Exceptional d ∧ ¬ IsPowTwo d := by
  rcases classify d hd with ⟨hp, he⟩ | ⟨hex, hnp, hgt, _⟩ | ⟨hne, hlt⟩
  · exact ⟨fun hgt => absurd hgt (by rw [he]; exact lt_irrefl _), fun hh => absurd hp hh.2⟩
  · exact ⟨fun _ => ⟨hex, hnp⟩, fun _ => hgt⟩
  · exact ⟨fun hgt => absurd (lt_trans hlt hgt) (lt_irrefl _), fun hh => absurd hh.1 hne⟩

/-- `h d ≤ 9/8` for every `d ≥ 1`. -/
theorem h_le_nine_eighths (d : ℕ) (hd : 1 ≤ d) : h d ≤ 9 / 8 := by
  rcases Nat.lt_or_ge d 2 with h1 | h2
  · have : d = 1 := by omega
    subst this
    rw [h, g_one]; norm_num
  · rcases classify d h2 with ⟨_, he⟩ | ⟨_, _, _, hle⟩ | ⟨_, hlt⟩
    · rw [he]; norm_num
    · exact hle
    · linarith

/-- `h d ≤ 1 + 1/d` for every `d ≥ 1` (the invariant, in divided form). -/
theorem h_le_one_add_inv (d : ℕ) (hd : 1 ≤ d) : h d ≤ 1 + 1 / (d : ℚ) := by
  have hb := bound_all d hd
  rw [Bound] at hb
  have hd0 : (0 : ℚ) < d := by exact_mod_cast hd
  rw [show (1 : ℚ) + 1 / (d : ℚ) = ((d : ℚ) + 1) / d by field_simp, le_div_iff₀ hd0]
  linarith

/-- The paper's sentence in density form: `1 - g d > (d - 1)/d` iff `d` is not exceptional. -/
theorem density_gt_iff (d : ℕ) (hd : 2 ≤ d) : ((d : ℚ) - 1) / d < 1 - g d ↔ ¬ Exceptional d := by
  rw [← h_lt_one_iff d hd, h]
  have hd0 : (0 : ℚ) < d := by
    have : 0 < d := by omega
    exact_mod_cast this
  rw [div_lt_iff₀ hd0]
  constructor <;> intro hh <;> nlinarith

/-- Equality with the bound `(d - 1)/d` holds exactly at powers of two. -/
theorem density_eq_iff (d : ℕ) (hd : 2 ≤ d) : 1 - g d = ((d : ℚ) - 1) / d ↔ IsPowTwo d := by
  rw [← h_eq_one_iff d hd, h]
  have hd0 : (0 : ℚ) < d := by
    have : 0 < d := by omega
    exact_mod_cast this
  rw [eq_div_iff hd0.ne']
  constructor <;> intro hh <;> nlinarith

end LayeredBoundary

#print axioms LayeredBoundary.g_step
#print axioms LayeredBoundary.decomp
#print axioms LayeredBoundary.decomp_unique
#print axioms LayeredBoundary.classify
#print axioms LayeredBoundary.h_lt_one_iff
#print axioms LayeredBoundary.h_eq_one_iff
#print axioms LayeredBoundary.one_lt_h_iff
#print axioms LayeredBoundary.h_le_nine_eighths
#print axioms LayeredBoundary.h_le_one_add_inv
#print axioms LayeredBoundary.density_gt_iff
#print axioms LayeredBoundary.density_eq_iff

/-! # Part A'. The written proof's own steps, certified one by one

The headline theorems above do not depend on anything in this part. It records that each claim made in
the written proof (PRIOR_WORK_AND_EXTENSION.md, section 4) is correct, and that its case (iv) argument,
as written (bound 9/8, sub-cases `m ≤ P/2 - 1` and `m = P - 2`), is a valid inductive step.
-/

namespace LayeredBoundary

/-- Spot values of `g`, the same as in the finite check `LayeredDensityBoundary.lean`:
densities 5/8, 13/16, 53/64, 27/32, 29/32 at d = 3, 5, 6, 7, 9. -/
theorem spot_values :
    g 2 = 1 / 2 ∧ g 3 = 3 / 8 ∧ g 5 = 3 / 16 ∧ g 6 = 11 / 64 ∧ g 7 = 5 / 32 ∧ g 9 = 3 / 32 := by
  have h2 : g 2 = 1 / 2 := by simpa using g_pow 1
  have h4 : g 4 = 1 / 4 := by
    have := g_pow 2
    norm_num at this
    exact this
  have h3 : g 3 = 3 / 8 := by
    have := g_step 1 2 le_rfl (by norm_num) (by norm_num)
    norm_num [h2] at this
    exact this
  have h5 : g 5 = 3 / 16 := by
    have := g_step 2 2 (by norm_num) (by norm_num) (by norm_num)
    norm_num [h2] at this
    exact this
  have h6 : g 6 = 11 / 64 := by
    have := g_step 2 3 (by norm_num) (by norm_num) (by norm_num)
    norm_num [h3] at this
    exact this
  have h7 : g 7 = 5 / 32 := by
    have := g_step 2 4 (by norm_num) (by norm_num) (by norm_num)
    norm_num [h4] at this
    exact this
  have h9 : g 9 = 3 / 32 := by
    have := g_step 3 2 (by norm_num) (by norm_num) (by norm_num)
    norm_num [h2] at this
    exact this
  exact ⟨h2, h3, h5, h6, h7, h9⟩

/-- `φ(m) = m (P - m + 1) / (P + m - 1)`. -/
def phi (P m : ℚ) : ℚ := m * (P - m + 1) / (P + m - 1)

/-- `φ(m) - 1 = (m - 1)(P - m - 1) / (P + m - 1)`. -/
theorem phi_sub_one (P m : ℚ) (hd : 0 < P + m - 1) :
    phi P m - 1 = (m - 1) * (P - m - 1) / (P + m - 1) := by
  rw [phi]
  field_simp
  ring

theorem sign_helper {a c t : ℚ} (hc : 0 < c) (e : a - 1 = c * t) :
    (a < 1 ↔ t < 0) ∧ (a = 1 ↔ t = 0) ∧ (1 < a ↔ 0 < t) := by
  refine ⟨⟨?_, ?_⟩, ⟨?_, ?_⟩, ⟨?_, ?_⟩⟩
  · intro ha
    by_contra ht
    rw [not_lt] at ht
    have := mul_nonneg hc.le ht
    linarith
  · intro ht
    have := mul_neg_of_pos_of_neg hc ht
    linarith
  · intro ha
    have h0 : c * t = 0 := by linarith
    rcases mul_eq_zero.mp h0 with hh | hh
    · exact absurd hh hc.ne'
    · exact hh
  · intro ht
    rw [ht, mul_zero] at e
    linarith
  · intro ha
    by_contra ht
    rw [not_lt] at ht
    have := mul_nonpos_of_nonneg_of_nonpos hc.le ht
    linarith
  · intro ht
    have := mul_pos hc ht
    linarith

/-- `h (P + m - 1) - 1 = ((P + m - 1) / (2 P m)) (h m - φ(m))`: the factor is positive, so the sign of
`h (P + m - 1) - 1` is the sign of `h m - φ(m)`. -/
theorem h_sub_one_eq (l m : ℕ) (hl : 1 ≤ l) (hm1 : 1 ≤ m) (hm : m ≤ 2 ^ l) :
    h (2 ^ l + m - 1) - 1 =
      (((2 : ℚ) ^ l + m - 1) / (2 * 2 ^ l * m)) * (h m - phi (2 ^ l) m) := by
  have hP : (0 : ℚ) < 2 ^ l := by positivity
  have hm0 : (0 : ℚ) < m := by exact_mod_cast hm1
  have hd : (0 : ℚ) < 2 ^ l + m - 1 := by
    have : (1 : ℚ) ≤ m := by exact_mod_cast hm1
    linarith
  rw [h_step l m hl hm1 hm, h, phi]
  field_simp
  ring

/-- "`h (P + m - 1) < 1` iff `h m < φ(m)`, and likewise for `=` and `>`." -/
theorem h_vs_phi (l m : ℕ) (hl : 1 ≤ l) (hm1 : 1 ≤ m) (hm : m ≤ 2 ^ l) :
    (h (2 ^ l + m - 1) < 1 ↔ h m < phi (2 ^ l) m) ∧
    (h (2 ^ l + m - 1) = 1 ↔ h m = phi (2 ^ l) m) ∧
    (1 < h (2 ^ l + m - 1) ↔ phi (2 ^ l) m < h m) := by
  have hP : (0 : ℚ) < 2 ^ l := by positivity
  have hm0 : (0 : ℚ) < m := by exact_mod_cast hm1
  have hd : (0 : ℚ) < 2 ^ l + m - 1 := by
    have : (1 : ℚ) ≤ m := by exact_mod_cast hm1
    linarith
  have hc : (0 : ℚ) < ((2 : ℚ) ^ l + m - 1) / (2 * 2 ^ l * m) := by positivity
  obtain ⟨a, b, c⟩ := sign_helper hc (h_sub_one_eq l m hl hm1 hm)
  exact ⟨a.trans sub_neg, b.trans sub_eq_zero, c.trans sub_pos⟩

/-- "`φ(1) = φ(P - 1) = 1`, `φ(P) < 1`, and `φ(m) > 1` for `2 ≤ m ≤ P - 2`." -/
theorem phi_facts (P : ℚ) (hP : 2 ≤ P) :
    phi P 1 = 1 ∧ phi P (P - 1) = 1 ∧ phi P P < 1 ∧ ∀ m : ℚ, 2 ≤ m → m + 2 ≤ P → 1 < phi P m := by
  refine ⟨?_, ?_, ?_, ?_⟩
  · have := phi_sub_one P 1 (by linarith)
    simp at this
    linarith
  · have := phi_sub_one P (P - 1) (by linarith)
    simp at this
    linarith
  · have h1 := phi_sub_one P P (by linarith)
    have : (P - 1) * (P - P - 1) / (P + P - 1) < 0 :=
      div_neg_of_neg_of_pos (by nlinarith) (by linarith)
    linarith
  · intro m hm hmP
    have h1 := phi_sub_one P m (by linarith)
    have : 0 < (m - 1) * (P - m - 1) / (P + m - 1) :=
      div_pos (mul_pos (by linarith) (by linarith)) (by linarith)
    linarith

/-- (ii) "`h (2P - 1) = 1 + (P - 1) / (2 P²)`". -/
theorem h_two_pow_sub_one_eq (l : ℕ) (hl : 1 ≤ l) :
    h (2 ^ l + 2 ^ l - 1) = 1 + ((2 : ℚ) ^ l - 1) / (2 * (2 ^ l) ^ 2) := by
  have hs := h_step l (2 ^ l) hl Nat.one_le_two_pow le_rfl
  rw [g_pow] at hs
  push_cast at hs
  rw [hs]
  exact (val_ii ((2 : ℚ) ^ l) (two_pow_cast_ge l hl)).1

/-- (iii) "`h (2P - 2) = (P - 1 + h (P - 1)) / P`", here with `P = 2 ^ l`, `l ≥ 1`. -/
theorem h_two_pow_sub_two_eq (l : ℕ) (hl : 1 ≤ l) :
    h (2 ^ l + (2 ^ l - 1) - 1) = ((2 : ℚ) ^ l - 1 + h (2 ^ l - 1)) / 2 ^ l := by
  have hP : 2 ≤ 2 ^ l := two_le_two_pow hl
  have hs := h_step l (2 ^ l - 1) hl (by omega) (by omega)
  have hmc : ((2 ^ l - 1 : ℕ) : ℚ) = (2 : ℚ) ^ l - 1 := by
    have : 2 ^ l - 1 + 1 = 2 ^ l := by omega
    have h2 : (((2 ^ l - 1 : ℕ) : ℚ) + 1) = (2 : ℚ) ^ l := by exact_mod_cast this
    linarith
  have hP0 : (0 : ℚ) < 2 ^ l := by positivity
  rw [hs, h, hmc]
  field_simp
  ring

/-- "`g (P - 2) = (P² + 2P + 8) / P³`" for `P = 2 ^ (j + 2) ≥ 8`. -/
theorem g_pow_sub_two (j : ℕ) (hj : 1 ≤ j) :
    g (2 ^ (j + 2) - 2) =
      (((2 : ℚ) ^ (j + 2)) ^ 2 + 2 * 2 ^ (j + 2) + 8) / ((2 : ℚ) ^ (j + 2)) ^ 3 := by
  have hQ : 2 ≤ 2 ^ j := two_le_two_pow hj
  have e1 : 2 ^ (j + 2) - 2 = 2 ^ (j + 1) + (2 ^ (j + 1) - 1) - 1 := by
    rw [pow_succ, pow_succ]; omega
  have e2 : 2 ^ (j + 1) - 1 = 2 ^ j + 2 ^ j - 1 := by rw [pow_succ]; omega
  have hm1 : 1 ≤ 2 ^ (j + 1) - 1 := by rw [pow_succ]; omega
  rw [e1, g_step (j + 1) (2 ^ (j + 1) - 1) (by omega) hm1 (by omega), e2, g_two_pow_sub_one j hj]
  have hQ0 : (0 : ℚ) < 2 ^ j := by positivity
  rw [pow_succ, pow_succ, pow_succ]
  field_simp
  ring

/-- "`φ(m) ≥ 9/5` for `3 ≤ m ≤ P/2 - 1`" (the conclusion the written proof draws from quasi-concavity;
proved here directly, with equality at `P = 8`, `m = 3`). -/
theorem phi_ge_nine_fifths (P m : ℚ) (hm : 3 ≤ m) (hP : 2 * m + 2 ≤ P) : 9 / 5 ≤ phi P m := by
  have hd : 0 < P + m - 1 := by linarith
  rw [phi, le_div_iff₀ hd]
  nlinarith [mul_nonneg (sub_nonneg.mpr hm) (sub_nonneg.mpr hm),
    mul_nonneg (sub_nonneg.mpr hP) (sub_nonneg.mpr hm)]

/-- `φ(m) > 9/8` whenever `2 ≤ m ≤ P/2 - 1`. -/
theorem phi_gt_nine_eighths (P m : ℚ) (hm : 2 ≤ m) (hP : 2 * m + 2 ≤ P) : 9 / 8 < phi P m := by
  have hd : 0 < P + m - 1 := by linarith
  rw [phi, lt_div_iff₀ hd]
  nlinarith [mul_nonneg (sub_nonneg.mpr hm) (sub_nonneg.mpr hm),
    mul_nonneg (sub_nonneg.mpr hP) (sub_nonneg.mpr hm)]

/-- "`h (P - 2) < φ(P - 2) = 3 (P - 2) / (2P - 3)` reduces to `P² + 10 P - 24 < P³`, true for `P ≥ 8`." -/
theorem written_last_step (P : ℚ) (hP : 8 ≤ P) :
    phi P (P - 2) = 3 * (P - 2) / (2 * P - 3) ∧
    ((P - 2) * ((P ^ 2 + 2 * P + 8) / P ^ 3) < phi P (P - 2) ↔ P ^ 2 + 10 * P - 24 < P ^ 3) ∧
    P ^ 2 + 10 * P - 24 < P ^ 3 := by
  have hP0 : 0 < P := by linarith
  have h3 : 0 < 2 * P - 3 := by linarith
  have hP3 : 0 < P ^ 3 := by positivity
  have e : phi P (P - 2) = 3 * (P - 2) / (2 * P - 3) := by
    rw [phi]
    have : P + (P - 2) - 1 = 2 * P - 3 := by ring
    rw [this]
    congr 1
    ring
  have hlast : P ^ 2 + 10 * P - 24 < P ^ 3 := by nlinarith [mul_pos hP0 hP0]
  refine ⟨e, ?_, hlast⟩
  rw [e, ← mul_div_assoc, div_lt_div_iff₀ hP3 h3]
  constructor
  · intro hh
    have h2 : 0 < P - 2 := by linarith
    nlinarith
  · intro hh
    have h2 : 0 < P - 2 := by linarith
    nlinarith

/-- The case split of (iv): an `m` of the form `2 ^ k - 1` or `2 ^ k - 2` with `m ≤ P - 2` has
`m ≤ P/2 - 1` or `m = P - 2`. -/
theorem written_split {l m k : ℕ} (hm : m + 2 ≤ 2 ^ l) (hk : m + 1 = 2 ^ k ∨ m + 2 = 2 ^ k) :
    2 * m + 2 ≤ 2 ^ l ∨ m + 2 = 2 ^ l := by
  have hkl : 2 ^ k ≤ 2 ^ l := by rcases hk with hh | hh <;> omega
  have hkl' : k ≤ l := (Nat.pow_le_pow_iff_right (by norm_num)).mp hkl
  rcases Nat.eq_or_lt_of_le hkl' with rfl | hlt
  · rcases hk with hh | hh
    · omega
    · exact Or.inr hh
  · have h2 : 2 ^ (k + 1) ≤ 2 ^ l := Nat.pow_le_pow_right (by norm_num) hlt
    rw [pow_succ] at h2
    left
    rcases hk with hh | hh <;> omega

/-- **Case (iv) exactly as written.** From the induction hypothesis at `m` alone (either `h m ≤ 1`, or
`m` is `2 ^ k - 1` or `2 ^ k - 2` and `h m ≤ 9/8`) it follows that `h (P + m - 1) < 1` for `2 ≤ m ≤ P - 2`. -/
theorem written_case_iv (l m : ℕ) (hl : 1 ≤ l) (hm2 : 2 ≤ m) (hm : m + 2 ≤ 2 ^ l)
    (ih : h m ≤ 1 ∨ ((∃ k : ℕ, m + 1 = 2 ^ k ∨ m + 2 = 2 ^ k) ∧ h m ≤ 9 / 8)) :
    h (2 ^ l + m - 1) < 1 := by
  rw [(h_vs_phi l m hl (by omega) (by omega)).1]
  have hP4 : (4 : ℚ) ≤ 2 ^ l := by
    have : 4 ≤ 2 ^ l := by omega
    exact_mod_cast this
  have hmq : (2 : ℚ) ≤ m := by exact_mod_cast hm2
  have hmP : (m : ℚ) + 2 ≤ 2 ^ l := by exact_mod_cast hm
  have hphi1 : 1 < phi (2 ^ l) m := (phi_facts ((2 : ℚ) ^ l) (by linarith)).2.2.2 m hmq hmP
  rcases ih with h1 | ⟨⟨k, hk⟩, h98⟩
  · linarith
  · rcases written_split hm hk with hsmall | hbig
    · have hs : 2 * (m : ℚ) + 2 ≤ 2 ^ l := by exact_mod_cast hsmall
      have := phi_gt_nine_eighths ((2 : ℚ) ^ l) m hmq hs
      linarith
    · rcases Nat.lt_or_ge l 3 with hl3 | hl3
      · -- P = 4, m = 2, a power of two
        have hl2 : l = 2 := by
          rcases (show l = 1 ∨ l = 2 by omega) with rfl | rfl
          · norm_num at hm; omega
          · rfl
        subst hl2
        have hm_eq : m = 2 := by norm_num at hbig; omega
        subst hm_eq
        have : h 2 = 1 := by simpa using h_pow 1
        rw [this]
        exact_mod_cast hphi1
      · obtain ⟨j, rfl⟩ : ∃ j, l = j + 2 := ⟨l - 2, by omega⟩
        have hm_eq : m = 2 ^ (j + 2) - 2 := by omega
        have hP8n : 2 ^ 3 ≤ 2 ^ (j + 2) := Nat.pow_le_pow_right (by norm_num) hl3
        have hP8 : (8 : ℚ) ≤ 2 ^ (j + 2) := by
          have : 8 ≤ 2 ^ (j + 2) := by simpa using hP8n
          exact_mod_cast this
        have hmc : (m : ℚ) = (2 : ℚ) ^ (j + 2) - 2 := by
          have : m + 2 = 2 ^ (j + 2) := hbig
          have h2 : (m : ℚ) + 2 = (2 : ℚ) ^ (j + 2) := by exact_mod_cast this
          linarith
        rw [h, hm_eq, g_pow_sub_two j (by omega), ← hm_eq, hmc]
        exact (written_last_step _ hP8).2.1.mpr (written_last_step _ hP8).2.2

/-! ### The four clauses of the written Proposition, in its own indexing -/

/-- (i) `h (2 ^ l) = 1`. -/
theorem prop_i (l : ℕ) : h (2 ^ l) = 1 := h_pow l

/-- (ii) `1 < h (2 ^ l - 1) ≤ 9/8` for `l ≥ 2`. -/
theorem prop_ii (l : ℕ) (hl : 2 ≤ l) : 1 < h (2 ^ l - 1) ∧ h (2 ^ l - 1) ≤ 9 / 8 := by
  obtain ⟨j, rfl⟩ : ∃ j, l = j + 1 := ⟨l - 1, by omega⟩
  have hc := case_ii j (by omega)
  have e : 2 ^ (j + 1) - 1 = 2 ^ j + 2 ^ j - 1 := by rw [pow_succ]; omega
  rw [e]
  exact ⟨hc.1, hc.2.1⟩

/-- (iii) `1 < h (2 ^ l - 2) ≤ 9/8` for `l ≥ 3`. -/
theorem prop_iii (l : ℕ) (hl : 3 ≤ l) : 1 < h (2 ^ l - 2) ∧ h (2 ^ l - 2) ≤ 9 / 8 := by
  obtain ⟨j, rfl⟩ : ∃ j, l = j + 2 := ⟨l - 2, by omega⟩
  have hc := case_iii j (by omega)
  have hQ : 2 ≤ 2 ^ j := two_le_two_pow (by omega)
  have e : 2 ^ (j + 2) - 2 = 2 ^ (j + 1) + (2 ^ (j + 1) - 1) - 1 := by
    rw [pow_succ, pow_succ]; omega
  rw [e]
  exact ⟨hc.1, hc.2.1⟩

/-- (iv) `h d < 1` for every other `d ≥ 2`. -/
theorem prop_iv (d : ℕ) (hd : 2 ≤ d) (hne : ¬ Exceptional d) : h d < 1 :=
  (h_lt_one_iff d hd).mpr hne

end LayeredBoundary

#print axioms LayeredBoundary.prop_i
#print axioms LayeredBoundary.prop_ii
#print axioms LayeredBoundary.prop_iii
#print axioms LayeredBoundary.prop_iv
#print axioms LayeredBoundary.spot_values
#print axioms LayeredBoundary.h_vs_phi
#print axioms LayeredBoundary.phi_facts
#print axioms LayeredBoundary.h_two_pow_sub_one_eq
#print axioms LayeredBoundary.h_two_pow_sub_two_eq
#print axioms LayeredBoundary.g_pow_sub_two
#print axioms LayeredBoundary.phi_ge_nine_fifths
#print axioms LayeredBoundary.written_last_step
#print axioms LayeredBoundary.written_case_iv

/-! # Part B. Long and Wagner's layered set `C_d` and its cardinality

Model of `Z_(2^n)`: representatives `0 ≤ x < 2 ^ n`, multiplication reduced modulo `2 ^ n`.
Long and Wagner (arXiv:1810.01225, Section 1.2) put `L_i = {x : x ≡ 2^(i-1) (mod 2^i)}` for `1 ≤ i ≤ n`
and (Section 3.1) `C_1 = ∅`, `C_d = L_[1,l] ∪ {2^(l+1) · x : x ∈ C_(d - 2^l + 1)}` with `l` the largest
integer such that `2 ^ l ≤ d`, "assum[ing] that there is enough space in Z_(2^n) for our construction to
fit (i.e. no layers past L_n are included)". `C n d` below is that recursion taken literally, with the
product computed in `Z_(2^n)`; `idx d` is the set of layer indices; `Fits n d` is the quoted condition.
-/

namespace LongWagner

open Finset LayeredBoundary

/-- The layer `L_i` of `Z_(2^n)`: `x ≡ 2^(i-1) (mod 2^i)`, on representatives below `2 ^ n`.
For `i > n` this is empty (Long and Wagner's extra layer `L_(n+1) = {0}` is never part of a fitting `C_d`). -/
def layer (n i : ℕ) : Finset ℕ := (range (2 ^ n)).filter fun x => x % 2 ^ i = 2 ^ (i - 1)

/-- `L_[1,l] = L_1 ∪ ... ∪ L_l`. -/
def lowLayers (n l : ℕ) : Finset ℕ := (Icc 1 l).biUnion (layer n)

/-- Long and Wagner's `C_d ⊆ Z_(2^n)`, by their recursion, elementwise product taken modulo `2 ^ n`. -/
def C (n : ℕ) (d : ℕ) : Finset ℕ :=
  if h : d ≤ 1 then ∅
  else lowLayers n (Nat.log 2 d) ∪
    (C n (d - 2 ^ Nat.log 2 d + 1)).image fun x => (2 ^ (Nat.log 2 d + 1) * x) % 2 ^ n
termination_by d
decreasing_by
  have h2 : 2 ≤ d := by omega
  have hl : 1 ≤ Nat.log 2 d := Nat.log_pos (by norm_num) h2
  have hp : 2 ^ 1 ≤ 2 ^ Nat.log 2 d := Nat.pow_le_pow_right (by norm_num) hl
  have hle : 2 ^ Nat.log 2 d ≤ d := Nat.pow_log_le_self 2 (by omega)
  omega

/-- The indices of the layers that make up `C_d` (independent of `n`). -/
def idx (d : ℕ) : Finset ℕ :=
  if h : d ≤ 1 then ∅
  else Icc 1 (Nat.log 2 d) ∪ (idx (d - 2 ^ Nat.log 2 d + 1)).image (· + (Nat.log 2 d + 1))
termination_by d
decreasing_by
  have h2 : 2 ≤ d := by omega
  have hl : 1 ≤ Nat.log 2 d := Nat.log_pos (by norm_num) h2
  have hp : 2 ^ 1 ≤ 2 ^ Nat.log 2 d := Nat.pow_le_pow_right (by norm_num) hl
  have hle : 2 ^ Nat.log 2 d ≤ d := Nat.pow_log_le_self 2 (by omega)
  omega

/-- "There is enough space in `Z_(2^n)` for the construction to fit (no layers past `L_n` are included)". -/
def Fits (n d : ℕ) : Prop := ∀ i ∈ idx d, i ≤ n

/-- The index of the top layer of `C_d` (0 when `C_d` is empty). -/
def top (d : ℕ) : ℕ := (idx d).sup id

theorem fits_iff_top_le (n d : ℕ) : Fits n d ↔ top d ≤ n := by
  rw [top, Finset.sup_le_iff]; rfl

theorem C_of_le_one {n d : ℕ} (hd : d ≤ 1) : C n d = ∅ := by rw [C, dif_pos hd]
theorem idx_of_le_one {d : ℕ} (hd : d ≤ 1) : idx d = ∅ := by rw [idx, dif_pos hd]

theorem C_of_two_le {n d : ℕ} (hd : 2 ≤ d) :
    C n d = lowLayers n (Nat.log 2 d) ∪
      (C n (d - 2 ^ Nat.log 2 d + 1)).image fun x => (2 ^ (Nat.log 2 d + 1) * x) % 2 ^ n := by
  rw [C, dif_neg (by omega)]

theorem idx_of_two_le {d : ℕ} (hd : 2 ≤ d) :
    idx d = Icc 1 (Nat.log 2 d) ∪ (idx (d - 2 ^ Nat.log 2 d + 1)).image (· + (Nat.log 2 d + 1)) := by
  rw [idx, dif_neg (by omega)]

theorem sub_lt_self_of_two_le {d : ℕ} (hd : 2 ≤ d) : d - 2 ^ Nat.log 2 d + 1 < d := by
  have hl : 1 ≤ Nat.log 2 d := Nat.log_pos (by norm_num) hd
  have hp : 2 ^ 1 ≤ 2 ^ Nat.log 2 d := Nat.pow_le_pow_right (by norm_num) hl
  have hle : 2 ^ Nat.log 2 d ≤ d := Nat.pow_log_le_self 2 (by omega)
  omega

theorem idx_pos : ∀ d : ℕ, ∀ i ∈ idx d, 1 ≤ i := by
  intro d
  induction d using Nat.strong_induction_on with
  | _ d ih =>
    intro i hi
    rcases Nat.lt_or_ge d 2 with hd | hd
    · rw [idx_of_le_one (by omega)] at hi; simp at hi
    · rw [idx_of_two_le hd, mem_union, mem_image] at hi
      rcases hi with hi | ⟨j, _, rfl⟩
      · exact (mem_Icc.mp hi).1
      · omega

/-! ### Layers: multiplication, disjointness, size -/

/-- Multiplying `L_i` by `2 ^ k` in `Z_(2^n)` gives `L_(i+k)`, as long as `i + k ≤ n`. -/
theorem image_mul_layer (n i k : ℕ) (hi : 1 ≤ i) (hik : i + k ≤ n) :
    (layer n i).image (fun x => (2 ^ k * x) % 2 ^ n) = layer n (i + k) := by
  have hsplit : 2 ^ (i + k) = 2 ^ k * 2 ^ i := by rw [← pow_add, add_comm]
  have hsplit' : 2 ^ (i + k - 1) = 2 ^ k * 2 ^ (i - 1) := by
    rw [← pow_add]; congr 1; omega
  ext y
  simp only [mem_image, layer, mem_filter, mem_range]
  constructor
  · rintro ⟨x, ⟨_, hxi⟩, rfl⟩
    refine ⟨Nat.mod_lt _ (by positivity), ?_⟩
    rw [Nat.mod_mod_of_dvd _ (pow_dvd_pow 2 hik), hsplit, Nat.mul_mod_mul_left, hxi, hsplit']
  · rintro ⟨hy, hyi⟩
    have h2k : 2 ^ k ∣ y := by
      rw [← Nat.div_add_mod y (2 ^ (i + k)), hyi, hsplit, hsplit']
      exact dvd_add (Dvd.dvd.mul_right (dvd_mul_right _ _) _) (dvd_mul_right _ _)
    obtain ⟨x, rfl⟩ := h2k
    refine ⟨x, ⟨?_, ?_⟩, Nat.mod_eq_of_lt hy⟩
    · have : 0 < 2 ^ k := by positivity
      nlinarith
    · rw [hsplit, Nat.mul_mod_mul_left, hsplit'] at hyi
      exact Nat.eq_of_mul_eq_mul_left (by positivity) hyi

theorem layer_disjoint_of_lt (n : ℕ) {i j : ℕ} (hij : i < j) :
    Disjoint (layer n i) (layer n j) := by
  rw [Finset.disjoint_left]
  intro x hx hx'
  simp only [layer, mem_filter, mem_range] at hx hx'
  have h1 : x % 2 ^ j % 2 ^ i = x % 2 ^ i := Nat.mod_mod_of_dvd _ (pow_dvd_pow 2 hij.le)
  rw [hx'.2, hx.2] at h1
  have h2 : 2 ^ i ∣ 2 ^ (j - 1) := pow_dvd_pow 2 (by omega)
  rw [Nat.mod_eq_zero_of_dvd h2] at h1
  have : 0 < 2 ^ (i - 1) := by positivity
  omega

theorem layer_disjoint (n : ℕ) {i j : ℕ} (hij : i ≠ j) :
    Disjoint (layer n i) (layer n j) := by
  rcases Nat.lt_or_gt_of_ne hij with h | h
  · exact layer_disjoint_of_lt n h
  · exact (layer_disjoint_of_lt n h).symm

/-- `|L_i| = 2 ^ (n - i)` for `1 ≤ i ≤ n`. -/
theorem card_layer (n i : ℕ) (hi : 1 ≤ i) (hin : i ≤ n) : (layer n i).card = 2 ^ (n - i) := by
  have hpow : 2 ^ i * 2 ^ (n - i) = 2 ^ n := by rw [← pow_add]; congr 1; omega
  have h1 : 2 ^ (i - 1) < 2 ^ i := Nat.pow_lt_pow_right (by norm_num) (by omega)
  have himg : layer n i = (range (2 ^ (n - i))).image fun t => 2 ^ i * t + 2 ^ (i - 1) := by
    ext x
    simp only [layer, mem_filter, mem_range, mem_image]
    constructor
    · rintro ⟨hx, hxi⟩
      refine ⟨x / 2 ^ i, ?_, ?_⟩
      · apply Nat.div_lt_of_lt_mul; rwa [hpow]
      · rw [← hxi]; exact Nat.div_add_mod x (2 ^ i)
    · rintro ⟨t, ht, rfl⟩
      constructor
      · have h2 : 2 ^ i * (t + 1) ≤ 2 ^ i * 2 ^ (n - i) := Nat.mul_le_mul_left _ ht
        rw [hpow, mul_add, mul_one] at h2
        omega
      · rw [Nat.mul_add_mod]; exact Nat.mod_eq_of_lt h1
  rw [himg, card_image_of_injective, card_range]
  intro a b hab
  have hab' : 2 ^ i * a + 2 ^ (i - 1) = 2 ^ i * b + 2 ^ (i - 1) := hab
  have : 2 ^ i * a = 2 ^ i * b := by omega
  exact Nat.eq_of_mul_eq_mul_left (by positivity) this

/-- The layer in the paper's wording: `x ∈ L_i` iff `2 ^ (i - 1)` exactly divides `x`. -/
theorem mem_layer_iff_exactly_divides (n i x : ℕ) (hi : 1 ≤ i) :
    x ∈ layer n i ↔ x < 2 ^ n ∧ 2 ^ (i - 1) ∣ x ∧ ¬ 2 ^ i ∣ x := by
  obtain ⟨j, rfl⟩ : ∃ j, i = j + 1 := ⟨i - 1, by omega⟩
  simp only [layer, mem_filter, mem_range, Nat.add_sub_cancel]
  have hsplit : 2 ^ (j + 1) = 2 ^ j * 2 := pow_succ 2 j
  constructor
  · rintro ⟨hx, hmod⟩
    refine ⟨hx, ?_, ?_⟩
    · rw [← Nat.div_add_mod x (2 ^ (j + 1)), hmod, hsplit]
      exact dvd_add (Dvd.dvd.mul_right (dvd_mul_right _ _) _) dvd_rfl
    · intro hdvd
      have h0 := Nat.mod_eq_zero_of_dvd hdvd
      have : 0 < 2 ^ j := by positivity
      omega
  · rintro ⟨hx, ⟨y, rfl⟩, hnd⟩
    refine ⟨hx, ?_⟩
    rw [hsplit, Nat.mul_mod_mul_left]
    rcases Nat.mod_two_eq_zero_or_one y with h0 | h1
    · exfalso
      apply hnd
      rw [hsplit]
      exact Nat.mul_dvd_mul_left _ (Nat.dvd_of_mod_eq_zero h0)
    · rw [h1, mul_one]

/-! ### `C_d` is the union of the layers indexed by `idx d` -/

theorem C_eq_layers (n : ℕ) : ∀ d : ℕ, Fits n d → C n d = (idx d).biUnion (layer n) := by
  intro d
  induction d using Nat.strong_induction_on with
  | _ d ih =>
    intro hfit
    rcases Nat.lt_or_ge d 2 with hd | hd
    · rw [C_of_le_one (by omega), idx_of_le_one (by omega)]; rfl
    · have hfit' : ∀ i ∈ idx (d - 2 ^ Nat.log 2 d + 1), i + (Nat.log 2 d + 1) ≤ n := by
        intro i hi
        apply hfit
        rw [idx_of_two_le hd, mem_union]
        exact Or.inr (mem_image.mpr ⟨i, hi, rfl⟩)
      have ihm := ih _ (sub_lt_self_of_two_le hd) (fun i hi => by have := hfit' i hi; omega)
      rw [C_of_two_le hd, ihm, idx_of_two_le hd, union_biUnion, biUnion_image, image_biUnion, lowLayers]
      congr 1
      apply biUnion_congr rfl
      intro i hi
      exact image_mul_layer n i _ (idx_pos _ i hi) (hfit' i hi)

/-- `|C_d| = Σ_{i ∈ idx d} 2 ^ (n - i)` when the construction fits. -/
theorem card_C_eq_sum (n d : ℕ) (hfit : Fits n d) : (C n d).card = ∑ i ∈ idx d, 2 ^ (n - i) := by
  rw [C_eq_layers n d hfit, card_biUnion]
  · exact sum_congr rfl fun i hi => card_layer n i (idx_pos d i hi) (hfit i hi)
  · intro i hi j hj hij
    exact layer_disjoint n hij

/-! ### The density of the index set is `1 - g d` -/

theorem geom_sum (l : ℕ) : ∑ i ∈ Icc 1 l, ((1 : ℚ) / 2) ^ i = 1 - (1 / 2) ^ l := by
  induction l with
  | zero => simp
  | succ l ih => rw [sum_Icc_succ_top (by omega), ih, pow_succ]; ring

/-- `Σ_{i ∈ idx d} 2^(-i) = 1 - g d`, for every `d`. -/
theorem sum_idx : ∀ d : ℕ, ∑ i ∈ idx d, ((1 : ℚ) / 2) ^ i = 1 - g d := by
  intro d
  induction d using Nat.strong_induction_on with
  | _ d ih =>
    rcases Nat.lt_or_ge d 2 with hd | hd
    · have hg : g d = 1 := by rw [g, dif_pos (by omega)]
      rw [idx_of_le_one (by omega), hg]; simp
    · have hg : g d = (1 + g (d - 2 ^ Nat.log 2 d + 1)) / (2 * 2 ^ Nat.log 2 d) := by
        rw [g, dif_neg (by omega)]
      have hdisj : Disjoint (Icc 1 (Nat.log 2 d))
          ((idx (d - 2 ^ Nat.log 2 d + 1)).image (· + (Nat.log 2 d + 1))) := by
        rw [Finset.disjoint_left]
        intro x hx hx'
        obtain ⟨j, _, rfl⟩ := mem_image.mp hx'
        have := (mem_Icc.mp hx).2
        omega
      rw [idx_of_two_le hd, sum_union hdisj, geom_sum,
        sum_image (fun a _ b _ hab => by simpa using hab)]
      have hshift : ∑ i ∈ idx (d - 2 ^ Nat.log 2 d + 1), ((1 : ℚ) / 2) ^ (i + (Nat.log 2 d + 1)) =
          (1 / 2) ^ (Nat.log 2 d + 1) * ∑ i ∈ idx (d - 2 ^ Nat.log 2 d + 1), ((1 : ℚ) / 2) ^ i := by
        rw [mul_sum]
        exact sum_congr rfl fun i _ => by rw [pow_add]; ring
      rw [hshift, ih _ (sub_lt_self_of_two_le hd), hg]
      have hP : (0 : ℚ) < 2 ^ Nat.log 2 d := by positivity
      rw [pow_succ, one_div_pow]
      field_simp
      ring

/-! ### Headline theorem (target B) -/

/-- **`|C_d| = (1 - g d) · 2 ^ n`** for every `d` and every `n` such that no layer past `L_n` is used. -/
theorem card_C (n d : ℕ) (hfit : Fits n d) : ((C n d).card : ℚ) = (1 - g d) * 2 ^ n := by
  rw [card_C_eq_sum n d hfit, ← sum_idx d, sum_mul]
  push_cast
  apply sum_congr rfl
  intro i hi
  have hin : i ≤ n := hfit i hi
  have h2 : (2 : ℚ) ^ n = 2 ^ (n - i) * 2 ^ i := by rw [← pow_add]; congr 1; omega
  have hi0 : (0 : ℚ) < 2 ^ i := by positivity
  rw [h2, one_div_pow]
  field_simp

/-- Same statement with the hypothesis written as `top d ≤ n`. -/
theorem card_C_of_top_le (n d : ℕ) (h : top d ≤ n) : ((C n d).card : ℚ) = (1 - g d) * 2 ^ n :=
  card_C n d ((fits_iff_top_le n d).mpr h)

/-! ### The fitting condition is exact, and `n ≥ d` is enough -/

theorem geom_Ioc (n k : ℕ) :
    ∑ i ∈ Ioc n (n + k), ((1 : ℚ) / 2) ^ i = (1 / 2) ^ n - (1 / 2) ^ (n + k) := by
  induction k with
  | zero => simp
  | succ k ih => rw [← add_assoc, sum_Ioc_succ_top (by omega), ih, pow_succ]; ring

theorem sum_tail_lt (n : ℕ) (B : Finset ℕ) (hB : ∀ i ∈ B, n < i) :
    ∑ i ∈ B, ((1 : ℚ) / 2) ^ i < (1 / 2) ^ n := by
  have hsub : B ⊆ Ioc n (n + B.sup id) := by
    intro i hi
    rw [mem_Ioc]
    have : i ≤ B.sup id := Finset.le_sup (f := id) hi
    exact ⟨hB i hi, by omega⟩
  have hpos : (0 : ℚ) < (1 / 2) ^ (n + B.sup id) := by positivity
  calc ∑ i ∈ B, ((1 : ℚ) / 2) ^ i ≤ ∑ i ∈ Ioc n (n + B.sup id), ((1 : ℚ) / 2) ^ i :=
        sum_le_sum_of_subset_of_nonneg hsub (fun i _ _ => by positivity)
    _ = (1 / 2) ^ n - (1 / 2) ^ (n + B.sup id) := geom_Ioc n _
    _ < (1 / 2) ^ n := by linarith

/-- If some layer of `C_d` lies past `L_n`, then `(1 - g d) · 2 ^ n` is not an integer, so it is not the
cardinality of any set. -/
theorem not_fits_not_nat (n d : ℕ) (hnf : ¬ Fits n d) (N : ℕ) : (N : ℚ) ≠ (1 - g d) * 2 ^ n := by
  intro hN
  have hsplit := (sum_filter_add_sum_filter_not (idx d) (fun i => i ≤ n)
    (fun i => ((1 : ℚ) / 2) ^ i)).symm
  have hA : (∑ i ∈ (idx d).filter (fun i => i ≤ n), ((1 : ℚ) / 2) ^ i) * 2 ^ n =
      ((∑ i ∈ (idx d).filter (fun i => i ≤ n), 2 ^ (n - i) : ℕ) : ℚ) := by
    rw [sum_mul]
    push_cast
    apply sum_congr rfl
    intro i hi
    have hin : i ≤ n := (mem_filter.mp hi).2
    have h2 : (2 : ℚ) ^ n = 2 ^ (n - i) * 2 ^ i := by rw [← pow_add]; congr 1; omega
    have hi0 : (0 : ℚ) < 2 ^ i := by positivity
    rw [h2, one_div_pow]
    field_simp
  have hBne : ((idx d).filter (fun i => ¬ i ≤ n)).Nonempty := by
    by_contra hemp
    apply hnf
    intro i hi
    by_contra hin
    exact hemp ⟨i, mem_filter.mpr ⟨hi, hin⟩⟩
  have hBpos : 0 < ∑ i ∈ (idx d).filter (fun i => ¬ i ≤ n), ((1 : ℚ) / 2) ^ i :=
    sum_pos (fun i _ => by positivity) hBne
  have hBlt : ∑ i ∈ (idx d).filter (fun i => ¬ i ≤ n), ((1 : ℚ) / 2) ^ i < (1 / 2) ^ n :=
    sum_tail_lt n _ (fun i hi => by have := (mem_filter.mp hi).2; omega)
  have h2n : (0 : ℚ) < 2 ^ n := by positivity
  have hone : ((1 : ℚ) / 2) ^ n * 2 ^ n = 1 := by rw [← mul_pow]; norm_num
  have hr0 := mul_pos hBpos h2n
  have hr1 : (∑ i ∈ (idx d).filter (fun i => ¬ i ≤ n), ((1 : ℚ) / 2) ^ i) * 2 ^ n < 1 := by
    have hmul := mul_lt_mul_of_pos_right hBlt h2n
    rwa [hone] at hmul
  rw [← sum_idx d, hsplit, add_mul, hA] at hN
  rcases Nat.lt_or_ge (∑ i ∈ (idx d).filter (fun i => i ≤ n), 2 ^ (n - i)) N with hlt | hge
  · have : ((∑ i ∈ (idx d).filter (fun i => i ≤ n), 2 ^ (n - i) : ℕ) : ℚ) + 1 ≤ N := by
      exact_mod_cast hlt
    linarith
  · have : (N : ℚ) ≤ ((∑ i ∈ (idx d).filter (fun i => i ≤ n), 2 ^ (n - i) : ℕ) : ℚ) := by
      exact_mod_cast hge
    linarith

/-- **The 'large enough' condition is exact**: `|C_d| = (1 - g d) · 2 ^ n` holds if and only if no layer
past `L_n` is used, i.e. iff `top d ≤ n`. -/
theorem card_C_iff_fits (n d : ℕ) : ((C n d).card : ℚ) = (1 - g d) * 2 ^ n ↔ Fits n d :=
  ⟨fun hc => by_contra fun hnf => not_fits_not_nat n d hnf _ hc, card_C n d⟩

theorem idx_two : idx 2 = {1} := by
  have h2 : Nat.log 2 2 = 1 := Nat.log_eq_of_pow_le_of_lt_pow (by norm_num) (by norm_num)
  rw [idx_of_two_le le_rfl, h2]
  norm_num [idx_of_le_one]

/-- Every layer index of `C_d` is at most `d` (Long and Wagner: "It will always suffice to take e.g.
n ≥ d in general"). -/
theorem idx_le : ∀ d : ℕ, ∀ i ∈ idx d, i ≤ d := by
  intro d
  induction d using Nat.strong_induction_on with
  | _ d ih =>
    intro i hi
    rcases Nat.lt_or_ge d 2 with hd | hd
    · rw [idx_of_le_one (by omega)] at hi; simp at hi
    · have hl : 1 ≤ Nat.log 2 d := Nat.log_pos (by norm_num) hd
      have hle : 2 ^ Nat.log 2 d ≤ d := Nat.pow_log_le_self 2 (by omega)
      have hlt : d < 2 ^ (Nat.log 2 d + 1) := Nat.lt_pow_succ_log_self (by norm_num) d
      have hself : Nat.log 2 d < 2 ^ Nat.log 2 d := Nat.lt_two_pow_self
      rw [idx_of_two_le hd, mem_union, mem_image] at hi
      rcases hi with hi | ⟨j, hj, rfl⟩
      · have := (mem_Icc.mp hi).2; omega
      · rcases Nat.lt_or_ge (Nat.log 2 d) 2 with hL2 | hL2
        · have hL1 : Nat.log 2 d = 1 := by omega
          rw [hL1] at hj hle hlt ⊢
          norm_num at hle hlt
          have hm : d - 2 ^ 1 + 1 = 1 ∨ d - 2 ^ 1 + 1 = 2 := by omega
          rcases hm with hm | hm
          · rw [hm, idx_of_le_one le_rfl] at hj; simp at hj
          · rw [hm, idx_two] at hj
            have : j = 1 := by simpa using hj
            omega
        · have ihj := ih _ (sub_lt_self_of_two_le hd) j hj
          have hpow : Nat.log 2 d + 2 ≤ 2 ^ Nat.log 2 d := by
            obtain ⟨k, hk⟩ : ∃ k, Nat.log 2 d = k + 2 := ⟨Nat.log 2 d - 2, by omega⟩
            have hk2 : k < 2 ^ k := Nat.lt_two_pow_self
            rw [hk, pow_succ, pow_succ]; omega
          omega

theorem fits_of_le {n d : ℕ} (hdn : d ≤ n) : Fits n d := fun i hi => (idx_le d i hi).trans hdn

/-- `|C_d| = (1 - g d) · 2 ^ n` for every `n ≥ d`. -/
theorem card_C_of_le (n d : ℕ) (hdn : d ≤ n) : ((C n d).card : ℚ) = (1 - g d) * 2 ^ n :=
  card_C n d (fits_of_le hdn)

/-! ### Parts A and B together -/

/-- For `d ≥ 2` and fitting `n`: `|C_d| > ((d - 1)/d) · 2 ^ n` iff `d` is not `2^k`, `2^k - 1`, `2^k - 2`. -/
theorem card_C_gt_iff (n d : ℕ) (hd : 2 ≤ d) (hfit : Fits n d) :
    ((d : ℚ) - 1) / d * 2 ^ n < ((C n d).card : ℚ) ↔ ¬ Exceptional d := by
  have h2n : (0 : ℚ) < 2 ^ n := by positivity
  rw [card_C n d hfit, ← density_gt_iff d hd]
  constructor
  · intro hh; exact lt_of_mul_lt_mul_right hh h2n.le
  · intro hh; exact mul_lt_mul_of_pos_right hh h2n

/-- For `d ≥ 2` and fitting `n`: `|C_d| = ((d - 1)/d) · 2 ^ n` iff `d` is a power of two. -/
theorem card_C_eq_iff (n d : ℕ) (hd : 2 ≤ d) (hfit : Fits n d) :
    ((C n d).card : ℚ) = ((d : ℚ) - 1) / d * 2 ^ n ↔ IsPowTwo d := by
  have h2n : (0 : ℚ) < 2 ^ n := by positivity
  rw [card_C n d hfit, ← density_eq_iff d hd]
  constructor
  · intro hh; exact mul_right_cancel₀ h2n.ne' hh
  · intro hh; rw [hh]

/-! ### Spot checks of the definitions against Long and Wagner's text -/

/-- Their Table 1: `C_5 = L_1 ∪ L_2 ∪ L_4`. -/
theorem idx_five : idx 5 = {1, 2, 4} := by
  have h5 : Nat.log 2 5 = 2 := Nat.log_eq_of_pow_le_of_lt_pow (by norm_num) (by norm_num)
  rw [idx_of_two_le (by norm_num), h5, show 5 - 2 ^ 2 + 1 = 2 by norm_num, idx_two]
  decide

/-- Their Section 3.1: "e.g. `C_10 = L_1 ∪ L_2 ∪ L_3 ∪ L_5 ∪ L_7`". -/
theorem idx_ten : idx 10 = {1, 2, 3, 5, 7} := by
  have h10 : Nat.log 2 10 = 3 := Nat.log_eq_of_pow_le_of_lt_pow (by norm_num) (by norm_num)
  have h3 : Nat.log 2 3 = 1 := Nat.log_eq_of_pow_le_of_lt_pow (by norm_num) (by norm_num)
  rw [idx_of_two_le (by norm_num), h10, show 10 - 2 ^ 3 + 1 = 3 by norm_num,
    idx_of_two_le (by norm_num), h3, show 3 - 2 ^ 1 + 1 = 2 by norm_num, idx_two]
  decide

/-- In `Z_16`, `C_5` is the complement of `{0, 4, 12}` (the set used for d = 5 in the paper). -/
theorem C_five_mod_sixteen : C 4 5 = (range 16).filter fun x => x ≠ 0 ∧ x ≠ 4 ∧ x ≠ 12 := by
  have hfit : Fits 4 5 := by
    intro i hi
    rw [idx_five] at hi
    simp at hi
    omega
  rw [C_eq_layers 4 5 hfit, idx_five]
  decide

end LongWagner

#print axioms LongWagner.mem_layer_iff_exactly_divides
#print axioms LongWagner.image_mul_layer
#print axioms LongWagner.C_eq_layers
#print axioms LongWagner.sum_idx
#print axioms LongWagner.card_C
#print axioms LongWagner.card_C_of_top_le
#print axioms LongWagner.card_C_iff_fits
#print axioms LongWagner.card_C_of_le
#print axioms LongWagner.card_C_gt_iff
#print axioms LongWagner.card_C_eq_iff
#print axioms LongWagner.idx_five
#print axioms LongWagner.idx_ten
#print axioms LongWagner.C_five_mod_sixteen

/-!
## Addendum after the adversarial review (must-fix item 1): the sharper bound of case (iii)

Both written proofs bound case (iii) by `h (2P - 2) ≤ 1 + 1/(8P)`. The review found that this inequality
had no Lean theorem. It is added here, without changing anything above: the closed form
`h (2P - 2) = 1 + (Q - 1)/(4 Q ^ 3)` with `P = 2Q` (`h_iii_closed`), the bound in the indexing of
`case_iii` (`h_iii_le`) and in the indexing of `prop_iii` (`prop_iii_sharp`). The inequality reduces to
`4 Q (Q - 2) ^ 2 ≥ 0`, with equality exactly at `Q = 2`, that is `d = 6`.
-/

namespace LayeredBoundary

/-- Closed form of case (iii): with `Q = 2 ^ j`, `P = 2Q`, `d = 2P - 2`. -/
theorem h_iii_closed (j : ℕ) (hj : 1 ≤ j) :
    h (2 ^ (j + 1) + (2 ^ (j + 1) - 1) - 1) = 1 + ((2 : ℚ) ^ j - 1) / (4 * ((2 : ℚ) ^ j) ^ 3) := by
  have hQ : 2 ≤ 2 ^ j := two_le_two_pow hj
  have hm1 : 1 ≤ 2 ^ (j + 1) - 1 := by rw [pow_succ]; omega
  have hs := h_step (j + 1) (2 ^ (j + 1) - 1) (by omega) hm1 (by omega)
  have em : 2 ^ (j + 1) - 1 = 2 ^ j + 2 ^ j - 1 := by rw [pow_succ]; omega
  have hg : g (2 ^ (j + 1) - 1) = (1 + 1 / 2 ^ j) / (2 * 2 ^ j) := by
    rw [em]; exact g_two_pow_sub_one j hj
  have hmc : ((2 ^ (j + 1) - 1 : ℕ) : ℚ) = 2 * (2 : ℚ) ^ j - 1 := by
    have : 2 ^ (j + 1) - 1 + 1 = 2 * 2 ^ j := by rw [pow_succ]; omega
    have h2 : (((2 ^ (j + 1) - 1 : ℕ) : ℚ) + 1) = 2 * (2 : ℚ) ^ j := by exact_mod_cast this
    linarith
  have hc := cast_d (j + 1) (2 ^ (j + 1) - 1) hm1
  rw [hmc] at hc
  rw [hg, hmc] at hs
  have hp : (2 : ℚ) ^ (j + 1) = 2 * 2 ^ j := by rw [pow_succ]; ring
  rw [hp] at hs hc
  rw [hs]
  exact (val_iii ((2 : ℚ) ^ j) (two_pow_cast_ge j hj)).1

/-- The written proof's bound in case (iii): `h (2P - 2) ≤ 1 + 1/(8P)` with `P = 2 ^ (j + 1)`. -/
theorem h_iii_le (j : ℕ) (hj : 1 ≤ j) :
    h (2 ^ (j + 1) + (2 ^ (j + 1) - 1) - 1) ≤ 1 + 1 / (8 * (2 : ℚ) ^ (j + 1)) := by
  rw [h_iii_closed j hj]
  have hQ : (2 : ℚ) ≤ (2 : ℚ) ^ j := two_pow_cast_ge j hj
  have hp : (2 : ℚ) ^ (j + 1) = 2 * 2 ^ j := by rw [pow_succ]; ring
  rw [hp]
  generalize (2 : ℚ) ^ j = Q at hQ ⊢
  have hQ0 : 0 < Q := by linarith
  have key : (Q - 1) / (4 * Q ^ 3) ≤ 1 / (8 * (2 * Q)) := by
    rw [div_le_div_iff₀ (by positivity) (by positivity)]
    nlinarith [mul_nonneg hQ0.le (sq_nonneg (Q - 2))]
  linarith

/-- The same bound in the indexing of `prop_iii`: for `l ≥ 3`, `h (2 ^ l - 2) ≤ 1 + 1/(8 * 2 ^ (l - 1))`. -/
theorem prop_iii_sharp (l : ℕ) (hl : 3 ≤ l) :
    h (2 ^ l - 2) ≤ 1 + 1 / (8 * (2 : ℚ) ^ (l - 1)) := by
  obtain ⟨j, rfl⟩ : ∃ j, l = j + 2 := ⟨l - 2, by omega⟩
  have hQ : 2 ≤ 2 ^ j := two_le_two_pow (by omega)
  have e : 2 ^ (j + 2) - 2 = 2 ^ (j + 1) + (2 ^ (j + 1) - 1) - 1 := by
    rw [pow_succ, pow_succ]; omega
  have e' : j + 2 - 1 = j + 1 := by omega
  rw [e, e']
  exact h_iii_le j (by omega)

/-- The bound is attained at `d = 6` (`P = 4`): `h 6 = 1 + 1/32`. -/
theorem h_six : h 6 = 1 + 1 / 32 := by
  have := h_iii_closed 1 (le_refl 1)
  norm_num at this
  rw [this]
  norm_num

end LayeredBoundary

#print axioms LayeredBoundary.h_iii_closed
#print axioms LayeredBoundary.h_iii_le
#print axioms LayeredBoundary.prop_iii_sharp
#print axioms LayeredBoundary.h_six
