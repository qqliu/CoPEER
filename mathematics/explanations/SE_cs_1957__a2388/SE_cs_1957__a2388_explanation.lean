import Mathlib
/- Explanation census, record SE_cs_1957__a2388 (cs.stackexchange answer 2388, "Lemma A").
Model-written; no human review. The released certificate
  validation/human_review_20260915/lean/SE_cs_1957__a2388.lean
is NOT modified; its definitions are restated verbatim below in a new namespace.
Mathlib is used because the released definitions are Mathlib's (Nat.log, Finset.sum, Real.logb).

Headline theorems:
  claim_refuted, claim_refuted_real, real_log_source_counterexample (released witness, verbatim)
  repair            (universal)  drivingSum b (b^p) p k L = trueRHS b p k L            for b >= 2
  repair_intermediate, upper_limit_literal : the dossier's intermediate form; the printed upper limit
  family            (universal)  k >= 1, L >= 2  ->  drivingSum < claimedRHS
  exact             (iff)        drivingSum = claimedRHS  <->  k = 0 or L <= 1
  second_equality   (universal)  middleTerm = claimedRHS (the chain's second equality is fine)
  first_equality_exact (iff)     drivingSum = middleTerm  <->  k = 0 or L <= 1
  theta_version, theta_sharp (universal)  g <= claimed <= (k+1) * g, and (k+1) * g + n^p <= n^p * (L+1)^(k+1)
  real_repair, real_family, real_exact : the same three over the reals with Real.logb and rpow
  repair_needs_a_eq_b_pow_p, repair_needs_b_ge_two : the hypotheses of the Nat-model repair are needed
  real_repair_rk, real_family_rk, real_exact_rk, real_family_half : real exponent k (the source says only k >= 0)
-/

set_option maxRecDepth 10000
set_option maxHeartbeats 4000000

namespace SE_cs_1957_a2388_Census

/-! ### Released definitions, restated verbatim -/

def lgbAux (b : Nat) (_fuel : Nat) (x : Nat) : Nat := Nat.log b x

def lgb (b x : Nat) : Nat := Nat.log b x

def h (b p k x : Nat) : Nat := x ^ p * (lgb b x) ^ k

def drivingSumAux (b a p k L m : Nat) : Nat := ∑ j ∈ Finset.range m, a ^ j * h b p k (b ^ (L-j))

def drivingSum (b a p k L : Nat) : Nat := drivingSumAux b a p k L L

def geoSumAux (r m : Nat) : Nat := ∑ j ∈ Finset.range m, r ^ j

def middleTerm (b a p k L : Nat) : Nat :=
  (b ^ L) ^ p * L ^ k * geoSumAux (a / b ^ p) L

def claimedRHS (b p k L : Nat) : Nat := (b ^ L) ^ p * L ^ (k + 1)

def powerSumAux (k m : Nat) : Nat := ∑ j ∈ Finset.range m, (j+1) ^ k

def trueRHS (b p k L : Nat) : Nat := (b ^ L) ^ p * powerSumAux k L

def lemmaAFailsAt (b a p k L : Nat) : Bool :=
  ! (drivingSum b a p k L == claimedRHS b p k L)

noncomputable def sourceH (x : ℝ) : ℝ := x ^ (Real.logb 2 2) * Real.logb 2 x

/-- The released selected declaration, statement and proof verbatim. -/
theorem real_log_source_counterexample :
    (∑ j ∈ Finset.range 2, (2 : ℝ)^j * sourceH (4 / 2^j)) = 12 ∧
    (4 : ℝ)^(Real.logb 2 2) * (Real.logb 2 4)^2 = 16 ∧ (12 : ℝ) ≠ 16 := by
 have hlog : Real.logb 2 (4 : ℝ) = 2 := by
   have h : (4 : ℝ) = 2 ^ 2 := by norm_num
   rw [h, Real.logb_pow]
   norm_num
 norm_num [sourceH, Finset.sum_range_succ, hlog]

/-! ### New definition (not in the release): the source's h for general b, a, k over the reals -/

/-- h(x) = x^{log_b a} * (log_b x)^k, the source's function, with Mathlib's Real.logb and rpow. -/
noncomputable def sourceHgen (b a : ℝ) (k : ℕ) (x : ℝ) : ℝ :=
  x ^ (Real.logb b a) * (Real.logb b x) ^ k

/-- The released `sourceH` is the instance b = a = 2, k = 1. -/
theorem sourceH_eq_gen : sourceH = sourceHgen 2 2 1 := by
  funext x
  simp [sourceH, sourceHgen]

/-! ### Power sums: sum_{i=1}^{L} i^k versus L^(k+1) -/

theorem powerSumAux_succ (k m : Nat) :
    powerSumAux k (m+1) = powerSumAux k m + (m+1) ^ k := by
  unfold powerSumAux
  exact Finset.sum_range_succ _ _

theorem powerSum_le (k L : Nat) : powerSumAux k L ≤ L ^ (k+1) := by
  induction L with
  | zero => simp [powerSumAux]
  | succ m ih =>
    rw [powerSumAux_succ]
    have h1 : m ^ k ≤ (m+1) ^ k := Nat.pow_le_pow_left (Nat.le_succ m) k
    calc powerSumAux k m + (m+1) ^ k
        ≤ m ^ (k+1) + (m+1) ^ k := Nat.add_le_add_right ih _
      _ = m * m ^ k + (m+1) ^ k := by ring
      _ ≤ m * (m+1) ^ k + (m+1) ^ k := Nat.add_le_add_right (Nat.mul_le_mul_left m h1) _
      _ = (m+1) ^ (k+1) := by ring

/-- Documented strict inequality: for k >= 1 and L >= 2, sum_{i=1}^{L} i^k < L^(k+1). -/
theorem powerSum_lt (k L : Nat) (hk : 1 ≤ k) (hL : 2 ≤ L) : powerSumAux k L < L ^ (k+1) := by
  obtain ⟨m, rfl⟩ : ∃ m, L = m + 1 := ⟨L - 1, by omega⟩
  rw [powerSumAux_succ]
  have h0 := powerSum_le k m
  have h1 : m ^ k < (m+1) ^ k := Nat.pow_lt_pow_left (Nat.lt_succ_self m) (by omega)
  have h2 : m * m ^ k < m * (m+1) ^ k := mul_lt_mul_of_pos_left h1 (by omega)
  calc powerSumAux k m + (m+1) ^ k
      ≤ m ^ (k+1) + (m+1) ^ k := Nat.add_le_add_right h0 _
    _ = m * m ^ k + (m+1) ^ k := by ring
    _ < m * (m+1) ^ k + (m+1) ^ k := Nat.add_lt_add_right h2 _
    _ = (m+1) ^ (k+1) := by ring

/-- Exactness at the level of power sums. -/
theorem powerSum_eq_iff (k L : Nat) : powerSumAux k L = L ^ (k+1) ↔ (k = 0 ∨ L ≤ 1) := by
  constructor
  · intro heq
    by_contra hne
    have hk : 1 ≤ k := by omega
    have hL : 2 ≤ L := by omega
    exact absurd heq (Nat.ne_of_lt (powerSum_lt k L hk hL))
  · rintro (rfl | hL)
    · simp [powerSumAux]
    · have : L = 0 ∨ L = 1 := by omega
      rcases this with rfl | rfl
      · simp [powerSumAux]
      · simp [powerSumAux]

theorem bern_up (j k : Nat) : (j+1) ^ (k+1) ≤ j ^ (k+1) + (k+1) * (j+1) ^ k := by
  induction k with
  | zero => simp
  | succ k ih =>
    have h1 : j ^ (k+1) ≤ (j+1) ^ (k+1) := Nat.pow_le_pow_left (Nat.le_succ j) _
    calc (j+1) ^ (k+1+1) = (j+1) * (j+1) ^ (k+1) := by ring
      _ ≤ (j+1) * (j ^ (k+1) + (k+1) * (j+1) ^ k) := Nat.mul_le_mul_left _ ih
      _ = j ^ (k+1+1) + j ^ (k+1) + (k+1) * (j+1) ^ (k+1) := by ring
      _ ≤ j ^ (k+1+1) + (j+1) ^ (k+1) + (k+1) * (j+1) ^ (k+1) :=
          Nat.add_le_add_right (Nat.add_le_add_left h1 _) _
      _ = j ^ (k+1+1) + (k+1+1) * (j+1) ^ (k+1) := by ring

theorem bern_low (j k : Nat) : j ^ (k+1) + (k+1) * j ^ k ≤ (j+1) ^ (k+1) := by
  induction k with
  | zero => simp
  | succ k ih =>
    calc j ^ (k+1+1) + (k+1+1) * j ^ (k+1)
        ≤ j ^ (k+1+1) + (k+1+1) * j ^ (k+1) + (k+1) * j ^ k := Nat.le_add_right _ _
      _ = (j+1) * (j ^ (k+1) + (k+1) * j ^ k) := by ring
      _ ≤ (j+1) * (j+1) ^ (k+1) := Nat.mul_le_mul_left _ ih
      _ = (j+1) ^ (k+1+1) := by ring

/-- L^(k+1) <= (k+1) * sum_{i=1}^{L} i^k  (the constant of the surviving Theta bound). -/
theorem powerSum_lower (k L : Nat) : L ^ (k+1) ≤ (k+1) * powerSumAux k L := by
  induction L with
  | zero => simp
  | succ m ih =>
    rw [powerSumAux_succ, Nat.mul_add]
    exact le_trans (bern_up m k) (Nat.add_le_add_right ih _)

/-- (k+1) * sum_{i=1}^{L} i^k + 1 <= (L+1)^(k+1): with `powerSum_lower` this squeezes
(k+1) * sum / L^(k+1) into [1, ((L+1)/L)^(k+1)], the documented "factor tending to k+1". -/
theorem powerSum_upper_sharp (k L : Nat) : (k+1) * powerSumAux k L + 1 ≤ (L+1) ^ (k+1) := by
  induction L with
  | zero => simp [powerSumAux]
  | succ m ih =>
    rw [powerSumAux_succ, Nat.mul_add]
    calc (k+1) * powerSumAux k m + (k+1) * (m+1) ^ k + 1
        = ((k+1) * powerSumAux k m + 1) + (k+1) * (m+1) ^ k := by ring
      _ ≤ (m+1) ^ (k+1) + (k+1) * (m+1) ^ k := Nat.add_le_add_right ih _
      _ ≤ (m+1+1) ^ (k+1) := bern_low (m+1) k

/-! ### The documented repair (Nat model): g(n) = n^{log_b a} * sum_{i=1}^{L} i^k -/

theorem term_eq (b p k L j : Nat) (hb : 2 ≤ b) (hj : j < L) :
    (b ^ p) ^ j * h b p k (b ^ (L-j)) = (b ^ L) ^ p * (L-j) ^ k := by
  unfold h lgb
  rw [Nat.log_pow (by omega)]
  have e : b ^ L = b ^ j * b ^ (L-j) := by
    rw [← pow_add]
    congr 1
    omega
  rw [e]
  ring

/-- REPAIR (universal). With a = b^p (p = log_b a), b >= 2, n = b^L:
the driving sum equals n^p * sum_{i=1}^{L} i^k, for every k and L. -/
theorem repair (b p k L : Nat) (hb : 2 ≤ b) :
    drivingSum b (b ^ p) p k L = trueRHS b p k L := by
  unfold drivingSum drivingSumAux trueRHS powerSumAux
  have key : ∑ j ∈ Finset.range L, (b ^ p) ^ j * h b p k (b ^ (L-j))
      = ∑ j ∈ Finset.range L, (b ^ L) ^ p * (L - 1 - j + 1) ^ k := by
    apply Finset.sum_congr rfl
    intro j hj
    rw [Finset.mem_range] at hj
    rw [term_eq b p k L j hb hj]
    have e : L - j = L - 1 - j + 1 := by omega
    rw [e]
  rw [key, Finset.sum_range_reflect (fun j => (b ^ L) ^ p * (j + 1) ^ k) L, Finset.mul_sum]

/-- The dossier's intermediate form: g(n) = n^{log_b a} * sum_{j=0}^{L-1} (L-j)^k. -/
theorem repair_intermediate (b p k L : Nat) (hb : 2 ≤ b) :
    drivingSum b (b ^ p) p k L = (b ^ L) ^ p * ∑ j ∈ Finset.range L, (L - j) ^ k := by
  unfold drivingSum drivingSumAux
  rw [Finset.mul_sum]
  apply Finset.sum_congr rfl
  intro j hj
  rw [Finset.mem_range] at hj
  exact term_eq b p k L j hb hj

/-- The source prints the upper limit as log_b{n-1}. Read literally with a floor logarithm,
log_b(n - 1) = L - 1 at n = b^L (L >= 1), so the literal and the intended index sets coincide. -/
theorem upper_limit_literal (b L : Nat) (hb : 2 ≤ b) (hL : 1 ≤ L) :
    Nat.log b (b ^ L - 1) + 1 = L := by
  obtain ⟨m, rfl⟩ : ∃ m, L = m + 1 := ⟨L - 1, by omega⟩
  have hp : 0 < b ^ m := pow_pos (by omega) m
  have e : b ^ (m+1) = b ^ m * b := pow_succ b m
  have h2 : b ^ m * 2 ≤ b ^ m * b := Nat.mul_le_mul_left _ hb
  have h1 : b ^ m ≤ b ^ (m+1) - 1 := by omega
  have h3 : b ^ (m+1) - 1 < b ^ (m+1) := by omega
  rw [Nat.log_eq_of_pow_le_of_lt_pow h1 h3]

theorem scale_pos (b p L : Nat) (hb : 2 ≤ b) : 0 < (b ^ L) ^ p :=
  pow_pos (pow_pos (by omega) L) p

/-! ### The documented family and exactness (Nat model) -/

/-- FAMILY (universal). For every b >= 2, p, k >= 1, L >= 2 (a = b^p, n = b^L) the asserted
identity fails, with the driving sum strictly smaller than the claimed value. -/
theorem family (b p k L : Nat) (hb : 2 ≤ b) (hk : 1 ≤ k) (hL : 2 ≤ L) :
    drivingSum b (b ^ p) p k L < claimedRHS b p k L
    ∧ drivingSum b (b ^ p) p k L ≠ claimedRHS b p k L := by
  have hlt : drivingSum b (b ^ p) p k L < claimedRHS b p k L := by
    rw [repair b p k L hb]
    unfold trueRHS claimedRHS
    exact mul_lt_mul_of_pos_left (powerSum_lt k L hk hL) (scale_pos b p L hb)
  exact ⟨hlt, Nat.ne_of_lt hlt⟩

/-- EXACT (iff). On the source's domain (b >= 2, a = b^p, n = b^L) the asserted identity
g(n) = n^{log_b a} log_b^{k+1} n holds iff k = 0 or L <= 1 (n = 1 or n = b). -/
theorem exact (b p k L : Nat) (hb : 2 ≤ b) :
    drivingSum b (b ^ p) p k L = claimedRHS b p k L ↔ (k = 0 ∨ L ≤ 1) := by
  rw [repair b p k L hb]
  unfold trueRHS claimedRHS
  constructor
  · intro heq
    exact (powerSum_eq_iff k L).mp (Nat.eq_of_mul_eq_mul_left (scale_pos b p L hb) heq)
  · intro hcase
    rw [(powerSum_eq_iff k L).mpr hcase]

/-- The refuted local claim, as a universal statement over the source's domain, is false. -/
theorem claim_refuted :
    ¬ (∀ b p k L : Nat, 2 ≤ b → drivingSum b (b ^ p) p k L = claimedRHS b p k L) := by
  intro hall
  exact (family 2 1 1 2 (by omega) (by omega) (by omega)).2 (hall 2 1 1 2 (by omega))

/-- The two released Nat witnesses (b=a=2, k=1, n=4: 12 vs 16; b=2, a=1, k=1, n=4: 3 vs 4). -/
theorem claim_refuted_witnesses :
    drivingSum 2 2 1 1 2 = 12 ∧ claimedRHS 2 1 1 2 = 16 ∧ trueRHS 2 1 1 2 = 12
    ∧ drivingSum 2 1 0 1 2 = 3 ∧ claimedRHS 2 0 1 2 = 4 ∧ trueRHS 2 0 1 2 = 3 := by decide

/-! ### The two equalities of the chain, separately -/

/-- The SECOND equality of the chain is fine, universally (dossier: "The SECOND one is fine"). -/
theorem second_equality (b p k L : Nat) (hb : 1 ≤ b) :
    middleTerm b (b ^ p) p k L = claimedRHS b p k L := by
  unfold middleTerm geoSumAux claimedRHS
  rw [Nat.div_self (pow_pos (by omega) p)]
  simp
  ring

/-- The FIRST equality is the error, exactly on the family. -/
theorem first_equality_exact (b p k L : Nat) (hb : 2 ≤ b) :
    drivingSum b (b ^ p) p k L = middleTerm b (b ^ p) p k L ↔ (k = 0 ∨ L ≤ 1) := by
  rw [second_equality b p k L (by omega)]
  exact exact b p k L hb

/-! ### "Only the Theta-version survives" -/

/-- claimed/(k+1) <= g <= claimed: the Theta-version of Lemma A with explicit constants. -/
theorem theta_version (b p k L : Nat) (hb : 2 ≤ b) :
    drivingSum b (b ^ p) p k L ≤ claimedRHS b p k L
    ∧ claimedRHS b p k L ≤ (k+1) * drivingSum b (b ^ p) p k L := by
  rw [repair b p k L hb]
  unfold trueRHS claimedRHS
  refine ⟨Nat.mul_le_mul_left _ (powerSum_le k L), ?_⟩
  calc (b ^ L) ^ p * L ^ (k+1) ≤ (b ^ L) ^ p * ((k+1) * powerSumAux k L) :=
        Nat.mul_le_mul_left _ (powerSum_lower k L)
    _ = (k+1) * ((b ^ L) ^ p * powerSumAux k L) := by ring

/-- Sharp upper bound: (k+1) * g(n) + n^p <= n^p * (L+1)^(k+1). With `theta_version` this
squeezes claimed / g into [ (k+1) * (L/(L+1))^(k+1), k+1 ], the documented factor "tending to k+1". -/
theorem theta_sharp (b p k L : Nat) (hb : 2 ≤ b) :
    (k+1) * drivingSum b (b ^ p) p k L + (b ^ L) ^ p ≤ (b ^ L) ^ p * (L+1) ^ (k+1) := by
  rw [repair b p k L hb]
  unfold trueRHS
  calc (k+1) * ((b ^ L) ^ p * powerSumAux k L) + (b ^ L) ^ p
      = (b ^ L) ^ p * ((k+1) * powerSumAux k L + 1) := by ring
    _ ≤ (b ^ L) ^ p * (L+1) ^ (k+1) := Nat.mul_le_mul_left _ (powerSum_upper_sharp k L)

/-! ### The hypotheses of the Nat-model repair are needed -/

theorem repair_needs_a_eq_b_pow_p : drivingSum 2 3 1 1 2 = 14 ∧ trueRHS 2 1 1 2 = 12 := by decide

theorem repair_needs_b_ge_two : drivingSum 1 (1 ^ 0) 0 1 2 = 0 ∧ trueRHS 1 0 1 2 = 3 := by decide

/-! ### The same three statements over the reals (Real.logb, rpow), for every real b > 1, a > 0 -/

theorem real_pow_rpow (b a : ℝ) (hb : 1 < b) (ha : 0 < a) (m : ℕ) :
    (b ^ m : ℝ) ^ (Real.logb b a) = a ^ m := by
  have hb0 : 0 < b := by linarith
  rw [← Real.rpow_natCast b m, ← Real.rpow_mul hb0.le, mul_comm, Real.rpow_mul hb0.le,
    Real.rpow_logb hb0 (ne_of_gt hb) ha, Real.rpow_natCast]

theorem real_logb_pow (b : ℝ) (hb : 1 < b) (m : ℕ) : Real.logb b (b ^ m) = m := by
  rw [Real.logb_pow, Real.logb_self_eq_one hb, mul_one]

theorem real_term (b a : ℝ) (hb : 1 < b) (ha : 0 < a) (k m : ℕ) :
    sourceHgen b a k (b ^ m) = a ^ m * (m : ℝ) ^ k := by
  unfold sourceHgen
  rw [real_logb_pow b hb m, real_pow_rpow b a hb ha m]

theorem real_powerSum_cast (k L : ℕ) :
    ∑ i ∈ Finset.range L, ((i : ℝ) + 1) ^ k = ((powerSumAux k L : ℕ) : ℝ) := by
  unfold powerSumAux
  push_cast
  rfl

/-- REPAIR over the reals: g(b^L) = (b^L)^{log_b a} * sum_{i=1}^{L} i^k. -/
theorem real_repair (b a : ℝ) (hb : 1 < b) (ha : 0 < a) (k L : ℕ) :
    ∑ j ∈ Finset.range L, a ^ j * sourceHgen b a k (b ^ L / b ^ j)
      = (b ^ L : ℝ) ^ (Real.logb b a) * ∑ i ∈ Finset.range L, ((i : ℝ) + 1) ^ k := by
  have hb0 : 0 < b := by linarith
  have key : ∀ j ∈ Finset.range L, a ^ j * sourceHgen b a k (b ^ L / b ^ j)
      = a ^ L * (((L - 1 - j : ℕ) : ℝ) + 1) ^ k := by
    intro j hj
    rw [Finset.mem_range] at hj
    have e : b ^ L / b ^ j = b ^ (L - j) := by
      rw [eq_comm, eq_div_iff (pow_ne_zero j (ne_of_gt hb0)), ← pow_add]
      congr 1
      omega
    have e2 : j + (L - j) = L := by omega
    have e3 : ((L - j : ℕ) : ℝ) = ((L - 1 - j : ℕ) : ℝ) + 1 := by
      have e4 : L - j = L - 1 - j + 1 := by omega
      rw [e4, Nat.cast_add, Nat.cast_one]
    rw [e, real_term b a hb ha, ← mul_assoc, ← pow_add, e2, e3]
  rw [Finset.sum_congr rfl key, ← Finset.mul_sum,
    Finset.sum_range_reflect (fun i => ((i : ℝ) + 1) ^ k) L, real_pow_rpow b a hb ha L]

/-- FAMILY over the reals: for every real b > 1, a > 0, and naturals k >= 1, L >= 2,
g(n) < n^{log_b a} * (log_b n)^{k+1} at n = b^L. -/
theorem real_family (b a : ℝ) (hb : 1 < b) (ha : 0 < a) (k L : ℕ) (hk : 1 ≤ k) (hL : 2 ≤ L) :
    ∑ j ∈ Finset.range L, a ^ j * sourceHgen b a k (b ^ L / b ^ j)
      < (b ^ L : ℝ) ^ (Real.logb b a) * (Real.logb b (b ^ L)) ^ (k+1) := by
  have hb0 : 0 < b := by linarith
  rw [real_repair b a hb ha, real_logb_pow b hb L, real_powerSum_cast]
  have hlt : ((powerSumAux k L : ℕ) : ℝ) < (L : ℝ) ^ (k+1) := by
    exact_mod_cast powerSum_lt k L hk hL
  exact mul_lt_mul_of_pos_left hlt (Real.rpow_pos_of_pos (pow_pos hb0 L) _)

/-- EXACT over the reals. -/
theorem real_exact (b a : ℝ) (hb : 1 < b) (ha : 0 < a) (k L : ℕ) :
    ∑ j ∈ Finset.range L, a ^ j * sourceHgen b a k (b ^ L / b ^ j)
      = (b ^ L : ℝ) ^ (Real.logb b a) * (Real.logb b (b ^ L)) ^ (k+1) ↔ (k = 0 ∨ L ≤ 1) := by
  have hb0 : 0 < b := by linarith
  have hpos : 0 < (b ^ L : ℝ) ^ (Real.logb b a) := Real.rpow_pos_of_pos (pow_pos hb0 L) _
  constructor
  · intro heq
    by_contra hne
    have hk : 1 ≤ k := by omega
    have hL : 2 ≤ L := by omega
    exact absurd heq (ne_of_lt (real_family b a hb ha k L hk hL))
  · intro hcase
    rw [real_repair b a hb ha, real_logb_pow b hb L, real_powerSum_cast,
      (powerSum_eq_iff k L).mpr hcase]
    push_cast
    rfl

/-- The refuted claim over the reals, as a universal statement, is false; the instance used is
the released witness b = a = 2, k = 1, n = 2^2 = 4. -/
theorem claim_refuted_real :
    ¬ (∀ (b a : ℝ) (k L : ℕ), 1 < b → 0 < a →
        ∑ j ∈ Finset.range L, a ^ j * sourceHgen b a k (b ^ L / b ^ j)
          = (b ^ L : ℝ) ^ (Real.logb b a) * (Real.logb b (b ^ L)) ^ (k+1)) := by
  intro hall
  have h1 := hall 2 2 1 2 (by norm_num) (by norm_num)
  have h2 := real_family 2 2 (by norm_num) (by norm_num) 1 2 (by omega) (by omega)
  exact absurd h1 (ne_of_lt h2)

/-! ### Real exponent k. The source says only "for some k >= 0"; the dossier's case split
(k = 0 agrees, k >= 1 fails) presumes an integer k. For a REAL exponent the identity fails for
every k > 0 (including 0 < k < 1) as soon as L >= 2. -/

/-- h(x) = x^{log_b a} * (log_b x)^k with a real exponent k (rpow). Not in the release. -/
noncomputable def sourceHr (b a k x : ℝ) : ℝ :=
  x ^ (Real.logb b a) * (Real.logb b x) ^ k

theorem real_term_rk (b a k : ℝ) (hb : 1 < b) (ha : 0 < a) (m : ℕ) :
    sourceHr b a k (b ^ m) = a ^ m * (m : ℝ) ^ k := by
  unfold sourceHr
  rw [real_logb_pow b hb m, real_pow_rpow b a hb ha m]

/-- REPAIR, real exponent. -/
theorem real_repair_rk (b a k : ℝ) (hb : 1 < b) (ha : 0 < a) (L : ℕ) :
    ∑ j ∈ Finset.range L, a ^ j * sourceHr b a k (b ^ L / b ^ j)
      = (b ^ L : ℝ) ^ (Real.logb b a) * ∑ i ∈ Finset.range L, ((i : ℝ) + 1) ^ k := by
  have hb0 : 0 < b := by linarith
  have key : ∀ j ∈ Finset.range L, a ^ j * sourceHr b a k (b ^ L / b ^ j)
      = a ^ L * (((L - 1 - j : ℕ) : ℝ) + 1) ^ k := by
    intro j hj
    rw [Finset.mem_range] at hj
    have e : b ^ L / b ^ j = b ^ (L - j) := by
      rw [eq_comm, eq_div_iff (pow_ne_zero j (ne_of_gt hb0)), ← pow_add]
      congr 1
      omega
    have e2 : j + (L - j) = L := by omega
    have e3 : ((L - j : ℕ) : ℝ) = ((L - 1 - j : ℕ) : ℝ) + 1 := by
      have e4 : L - j = L - 1 - j + 1 := by omega
      rw [e4, Nat.cast_add, Nat.cast_one]
    rw [e, real_term_rk b a k hb ha, ← mul_assoc, ← pow_add, e2, e3]
  rw [Finset.sum_congr rfl key, ← Finset.mul_sum,
    Finset.sum_range_reflect (fun i => ((i : ℝ) + 1) ^ k) L, real_pow_rpow b a hb ha L]

theorem rpow_sum_lt (k : ℝ) (hk : 0 < k) (L : ℕ) (hL : 2 ≤ L) :
    ∑ i ∈ Finset.range L, ((i : ℝ) + 1) ^ k < (L : ℝ) ^ (k + 1) := by
  have hLpos : (0 : ℝ) < L := by exact_mod_cast (by omega : 0 < L)
  have e : (L : ℝ) ^ (k + 1) = ∑ _i ∈ Finset.range L, (L : ℝ) ^ k := by
    rw [Finset.sum_const, Finset.card_range, nsmul_eq_mul, Real.rpow_add hLpos, Real.rpow_one,
      mul_comm]
  rw [e]
  apply Finset.sum_lt_sum
  · intro i hi
    rw [Finset.mem_range] at hi
    apply Real.rpow_le_rpow (by positivity) _ hk.le
    exact_mod_cast (by omega : i + 1 ≤ L)
  · refine ⟨0, Finset.mem_range.mpr (by omega), ?_⟩
    simp only [Nat.cast_zero, zero_add, Real.one_rpow]
    exact Real.one_lt_rpow (by exact_mod_cast (by omega : 1 < L)) hk

/-- FAMILY, real exponent: every real k > 0 and every L >= 2. -/
theorem real_family_rk (b a k : ℝ) (hb : 1 < b) (ha : 0 < a) (hk : 0 < k) (L : ℕ) (hL : 2 ≤ L) :
    ∑ j ∈ Finset.range L, a ^ j * sourceHr b a k (b ^ L / b ^ j)
      < (b ^ L : ℝ) ^ (Real.logb b a) * (Real.logb b (b ^ L)) ^ (k + 1) := by
  have hb0 : 0 < b := by linarith
  rw [real_repair_rk b a k hb ha, real_logb_pow b hb L]
  exact mul_lt_mul_of_pos_left (rpow_sum_lt k hk L hL) (Real.rpow_pos_of_pos (pow_pos hb0 L) _)

/-- EXACT, real exponent k >= 0: the identity holds iff k = 0 or L <= 1. -/
theorem real_exact_rk (b a k : ℝ) (hb : 1 < b) (ha : 0 < a) (hk0 : 0 ≤ k) (L : ℕ) :
    ∑ j ∈ Finset.range L, a ^ j * sourceHr b a k (b ^ L / b ^ j)
      = (b ^ L : ℝ) ^ (Real.logb b a) * (Real.logb b (b ^ L)) ^ (k + 1) ↔ (k = 0 ∨ L ≤ 1) := by
  constructor
  · intro heq
    by_contra hne
    rw [not_or] at hne
    obtain ⟨h1, h2⟩ := hne
    have hk : 0 < k := lt_of_le_of_ne hk0 (Ne.symm h1)
    have hL : 2 ≤ L := by omega
    exact absurd heq (ne_of_lt (real_family_rk b a k hb ha hk L hL))
  · intro hcase
    rw [real_repair_rk b a k hb ha, real_logb_pow b hb L]
    congr 1
    rcases hcase with rfl | hL
    · simp
    · have hk1 : k + 1 ≠ 0 := by linarith
      have : L = 0 ∨ L = 1 := by omega
      rcases this with rfl | rfl
      · simp [Real.zero_rpow hk1]
      · simp

/-- A member of the failure set that the dossier's integer case split does not cover:
k = 1/2, b = a = 2, n = 4. -/
theorem real_family_half :
    ∑ j ∈ Finset.range 2, (2 : ℝ) ^ j * sourceHr 2 2 (1/2) ((2 : ℝ) ^ 2 / 2 ^ j)
      < ((2 : ℝ) ^ 2) ^ (Real.logb 2 2) * (Real.logb 2 ((2 : ℝ) ^ 2)) ^ ((1/2 : ℝ) + 1) :=
  real_family_rk 2 2 (1/2) (by norm_num) (by norm_num) (by norm_num) 2 (by omega)

end SE_cs_1957_a2388_Census

#print axioms SE_cs_1957_a2388_Census.real_log_source_counterexample
#print axioms SE_cs_1957_a2388_Census.sourceH_eq_gen
#print axioms SE_cs_1957_a2388_Census.claim_refuted
#print axioms SE_cs_1957_a2388_Census.claim_refuted_witnesses
#print axioms SE_cs_1957_a2388_Census.claim_refuted_real
#print axioms SE_cs_1957_a2388_Census.repair
#print axioms SE_cs_1957_a2388_Census.repair_intermediate
#print axioms SE_cs_1957_a2388_Census.upper_limit_literal
#print axioms SE_cs_1957_a2388_Census.family
#print axioms SE_cs_1957_a2388_Census.exact
#print axioms SE_cs_1957_a2388_Census.powerSum_lt
#print axioms SE_cs_1957_a2388_Census.powerSum_eq_iff
#print axioms SE_cs_1957_a2388_Census.powerSum_lower
#print axioms SE_cs_1957_a2388_Census.powerSum_upper_sharp
#print axioms SE_cs_1957_a2388_Census.second_equality
#print axioms SE_cs_1957_a2388_Census.first_equality_exact
#print axioms SE_cs_1957_a2388_Census.theta_version
#print axioms SE_cs_1957_a2388_Census.theta_sharp
#print axioms SE_cs_1957_a2388_Census.repair_needs_a_eq_b_pow_p
#print axioms SE_cs_1957_a2388_Census.repair_needs_b_ge_two
#print axioms SE_cs_1957_a2388_Census.real_repair
#print axioms SE_cs_1957_a2388_Census.real_family
#print axioms SE_cs_1957_a2388_Census.real_exact
#print axioms SE_cs_1957_a2388_Census.real_repair_rk
#print axioms SE_cs_1957_a2388_Census.real_family_rk
#print axioms SE_cs_1957_a2388_Census.real_exact_rk
#print axioms SE_cs_1957_a2388_Census.real_family_half
