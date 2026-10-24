import Mathlib.Analysis.SpecificLimits.Basic
import Mathlib.Data.Nat.Choose.Cast
import Mathlib.Data.Real.Sqrt
import Mathlib.Tactic

/-!
# Proposition prop:schur-template-optimum, all clauses in one theorem (composition)

This file only COMPOSES two certificates; it proves no new mathematics beyond uniqueness of limits.

  Part A: a verbatim copy (import lines removed) of the analytic certificate
          astra/weekend_route_20260919/schur_template_kernel/SchurTemplate.lean,
          sha256 of the copied file: b6a3a5b94e3989f6d04a795e86d36b623ccc115fc534af43de52ce817fa0177f.
          It certifies the maximisation and stability of the objective `density`.  It is not this
          worker's product and is unchanged; if that file is revised, this copy is stale.
  Part B: the body of SchurTemplateLimit.lean (this directory): the exact count and the limit.
  Part C: the composition.  `IsLimitingFraction D` says that `D a b` is the limit of the normalised
          rainbow count of the proposition's colouring for every `0 ≤ a ≤ b ≤ 1`.  Such a `D`
          exists (`limiting_fraction_exists`), is unique on the parameter triangle
          (`limiting_fraction_unique`), and every such `D` satisfies all clauses of the proposition
          (`prop_schur_template_optimum`).

No sorry, no native_decide, no axiom declarations.
-/

/-! # Part A: analytic certificate (verbatim copy, imports removed) -/

/-!
# Kernel-checked arithmetic of the two-threshold Schur template

This file formalizes exactly the real-valued objective in equation
`eq:schur-template-objective` of the manuscript's structural-proofs appendix.
It does NOT identify this objective with a limiting combinatorial density.
That source-to-objective counting and convergence argument is a separate obligation.

The domain is `0 ≤ a ≤ b ≤ 1`. The global maximum within this TWO-THRESHOLD
TEMPLATE is `9/22`, achieved uniquely at `(4/11, 10/11)`. No assertion about
unrestricted three-colorings is made.
-/

namespace CoPEER.SchurTemplate

/-- The exact positive-part objective in the manuscript, with `x₊ = max x 0`. -/
noncomputable def density (a b : ℝ) : ℝ :=
  (b - a) * (1 - b + a) + (1 / 2 : ℝ) *
    ((1 - a)^2 - (1 - b)^2 - (max (1 - 2*a) 0)^2 -
      (max (1 - 2*b) 0)^2 + 2 * (max (1 - a - b) 0)^2)

/-- The admissible triangle, including its boundary. -/
def Admissible (a b : ℝ) : Prop := 0 ≤ a ∧ a ≤ b ∧ b ≤ 1

lemma region_one (a b : ℝ) (h : Admissible a b) (hb : b ≤ 1/2) :
    density a b = -(3/2 : ℝ)*a^2 + 4*a*b - (5/2 : ℝ)*b^2 - 2*a + 2*b := by
  rcases h with ⟨ha, hab, hb1⟩
  unfold density
  rw [max_eq_left (by linarith : 0 ≤ 1-2*a),
    max_eq_left (by linarith : 0 ≤ 1-2*b),
    max_eq_left (by linarith : 0 ≤ 1-a-b)]
  ring

lemma region_two (a b : ℝ) (ha : a ≤ 1/2) (hb : 1/2 ≤ b) (hab : a+b ≤ 1) :
    density a b = -(3/2 : ℝ)*a^2 + 4*a*b - (1/2 : ℝ)*b^2 - 2*a + 1/2 := by
  unfold density
  rw [max_eq_left (by linarith : 0 ≤ 1-2*a),
    max_eq_right (by linarith : 1-2*b ≤ 0),
    max_eq_left (by linarith : 0 ≤ 1-a-b)]
  ring

lemma region_three (a b : ℝ) (ha : a ≤ 1/2) (hb : 1/2 ≤ b) (hab : 1 ≤ a+b) :
    density a b = -(5/2 : ℝ)*a^2 + 2*a*b - (3/2 : ℝ)*b^2 + 2*b - 1/2 := by
  unfold density
  rw [max_eq_left (by linarith : 0 ≤ 1-2*a),
    max_eq_right (by linarith : 1-2*b ≤ 0),
    max_eq_right (by linarith : 1-a-b ≤ 0)]
  ring

lemma region_four (a b : ℝ) (h : Admissible a b) (ha : 1/2 ≤ a) :
    density a b = -(1/2 : ℝ)*a^2 + 2*a*b - (3/2 : ℝ)*b^2 - 2*a + 2*b := by
  rcases h with ⟨ha0, hab, hb⟩
  unfold density
  rw [max_eq_right (by linarith : 1-2*a ≤ 0),
    max_eq_right (by linarith : 1-2*b ≤ 0),
    max_eq_right (by linarith : 1-a-b ≤ 0)]
  ring

/-- Exact nonnegative decomposition in the first region. -/
theorem region_one_gap (a b : ℝ) (h : Admissible a b) (hb : b ≤ 1/2) :
    2/5 - density a b = (5/2 : ℝ)*(b-2/5)^2 +
      (3/2 : ℝ)*a^2 + a*(2-4*b) := by
  rw [region_one a b h hb]
  ring

/-- The first region has the sharper upper bound `2/5`. -/
theorem region_one_bound (a b : ℝ) (h : Admissible a b) (hb : b ≤ 1/2) :
    density a b ≤ 2/5 := by
  rw [region_one a b h hb]
  have hp := mul_nonneg h.1 (show 0 ≤ 2-4*b by linarith)
  nlinarith [sq_nonneg a, sq_nonneg (b - 2/5)]

/-- A sum-of-squares certificate removes any need for the informal Hessian argument. -/
theorem region_two_gap (a b : ℝ) (ha : a ≤ 1/2) (hb : 1/2 ≤ b) (hab : a+b ≤ 1) :
    3/8 - density a b = (3/2 : ℝ)*(a-b+1/2)^2 + (b-1/2)*(1-a-b) := by
  rw [region_two a b ha hb hab]
  ring

theorem region_two_bound (a b : ℝ) (ha : a ≤ 1/2) (hb : 1/2 ≤ b)
    (hab : a+b ≤ 1) : density a b ≤ 3/8 := by
  have he := region_two_gap a b ha hb hab
  have hp := mul_nonneg (show 0 ≤ b-1/2 by linarith) (show 0 ≤ 1-a-b by linarith)
  nlinarith [sq_nonneg (a-b+1/2)]

/-- Exact nonnegative decomposition in the fourth region. -/
theorem region_four_gap (a b : ℝ) (h : Admissible a b) (ha : 1/2 ≤ a) :
    3/8 - density a b = (1/2 : ℝ)*(a^2-1/4) +
      (1-b)*(2*a+1/2-(3/2)*b) := by
  rw [region_four a b h ha]
  ring

/-- The fourth region also lies below `3/8`. -/
theorem region_four_bound (a b : ℝ) (h : Admissible a b) (ha : 1/2 ≤ a) :
    density a b ≤ 3/8 := by
  rw [region_four a b h ha]
  have hp := mul_nonneg (show 0 ≤ 1-b by linarith [h.2.2])
    (show 0 ≤ 2*a+1/2-(3/2)*b by linarith [h.2.2])
  have hsq : (1/2 : ℝ)^2 ≤ a^2 := by nlinarith [sq_nonneg (a-1/2)]
  nlinarith


/-- An exact sum-of-squares identity for the spectral gap. -/
theorem quadratic_spectral_identity (u v : ℝ) :
    ((Real.sqrt 5 + 1) / 2) *
      ((5 / 2 : ℝ) * u ^ 2 - 2 * u * v + (3 / 2 : ℝ) * v ^ 2 -
        ((4 - Real.sqrt 5) / 2) * (u ^ 2 + v ^ 2)) =
    (((Real.sqrt 5 + 1) / 2) * u - v) ^ 2 := by
  have hs : (Real.sqrt 5) ^ 2 = (5 : ℝ) := Real.sq_sqrt (by norm_num)
  linear_combination (v ^ 2 / 4) * hs

/-- The least eigenvalue of the quadratic form is `(4 - sqrt 5) / 2`. -/
theorem quadratic_spectral_bound (u v : ℝ) :
    ((4 - Real.sqrt 5) / 2) * (u ^ 2 + v ^ 2) ≤
      (5 / 2 : ℝ) * u ^ 2 - 2 * u * v + (3 / 2 : ℝ) * v ^ 2 := by
  have hp : 0 < (Real.sqrt 5 + 1) / 2 := by positivity
  have hprod : 0 ≤
      ((Real.sqrt 5 + 1) / 2) *
        ((5 / 2 : ℝ) * u ^ 2 - 2 * u * v + (3 / 2 : ℝ) * v ^ 2 -
          ((4 - Real.sqrt 5) / 2) * (u ^ 2 + v ^ 2)) := by
    rw [quadratic_spectral_identity]
    exact sq_nonneg _
  exact sub_nonneg.mp (nonneg_of_mul_nonneg_right hprod hp)

/-- Equality holds precisely along the least-eigenvalue direction. -/
theorem quadratic_spectral_equality_iff (u v : ℝ) :
    ((4 - Real.sqrt 5) / 2) * (u ^ 2 + v ^ 2) =
      (5 / 2 : ℝ) * u ^ 2 - 2 * u * v + (3 / 2 : ℝ) * v ^ 2 ↔
    v = ((Real.sqrt 5 + 1) / 2) * u := by
  have hp : 0 < (Real.sqrt 5 + 1) / 2 := by positivity
  have hi := quadratic_spectral_identity u v
  constructor
  · intro h
    rw [← h, sub_self, mul_zero] at hi
    have hz := sq_eq_zero_iff.mp hi.symm
    linarith
  · intro h
    rw [h, sub_self, zero_pow (by norm_num : 2 ≠ 0)] at hi
    have hz := (mul_eq_zero.mp hi).resolve_left (ne_of_gt hp)
    rw [h]
    linarith

/-- The coefficient `(4 - sqrt 5) / 2` is strictly positive. -/
theorem quadratic_spectral_coefficient_pos : 0 < (4 - Real.sqrt 5) / 2 := by
  have hs : (Real.sqrt 5) ^ 2 = (5 : ℝ) := Real.sq_sqrt (by norm_num)
  nlinarith [Real.sqrt_nonneg (5 : ℝ)]

/-- No larger uniform coefficient can multiply `u² + v²`. -/
theorem quadratic_spectral_coefficient_optimal (c : ℝ)
    (hc : ∀ u v : ℝ, c * (u ^ 2 + v ^ 2) ≤
      (5 / 2 : ℝ) * u ^ 2 - 2 * u * v + (3 / 2 : ℝ) * v ^ 2) :
    c ≤ (4 - Real.sqrt 5) / 2 := by
  have he := (quadratic_spectral_equality_iff 1 ((Real.sqrt 5 + 1) / 2)).mpr
    (by ring)
  have hh := hc 1 ((Real.sqrt 5 + 1) / 2)
  rw [← he] at hh
  exact (mul_le_mul_iff_left₀ (by positivity :
    0 < (1 : ℝ) ^ 2 + ((Real.sqrt 5 + 1) / 2) ^ 2)).mp hh


/-- Exact quadratic stability identity in the region containing the maximizer. -/
theorem stability_identity (a b : ℝ) (ha : a ≤ 1/2) (hb : 1/2 ≤ b)
    (hab : 1 ≤ a+b) :
    9/22 - density a b = (5/2 : ℝ)*(a-4/11)^2 -
      2*(a-4/11)*(b-10/11) + (3/2 : ℝ)*(b-10/11)^2 := by
  rw [region_three a b ha hb hab]
  ring

/-- A second form makes positive definiteness explicit, without eigenvalue machinery. -/
theorem stability_sos (a b : ℝ) (ha : a ≤ 1/2) (hb : 1/2 ≤ b)
    (hab : 1 ≤ a+b) :
    9/22 - density a b = ((a-4/11)-(b-10/11))^2 +
      (3/2 : ℝ)*(a-4/11)^2 + (1/2 : ℝ)*(b-10/11)^2 := by
  rw [stability_identity a b ha hb hab]
  ring

/-- Global bound over the entire closed admissible triangle. -/
theorem global_bound (a b : ℝ) (h : Admissible a b) : density a b ≤ 9/22 := by
  by_cases hblo : b ≤ 1/2
  · linarith [region_one_bound a b h hblo]
  have hb : 1/2 ≤ b := le_of_lt (lt_of_not_ge hblo)
  by_cases halo : a ≤ 1/2
  · by_cases hablo : a+b ≤ 1
    · linarith [region_two_bound a b halo hb hablo]
    · have he := stability_sos a b halo hb (le_of_lt (lt_of_not_ge hablo))
      nlinarith [sq_nonneg ((a-4/11)-(b-10/11)), sq_nonneg (a-4/11),
        sq_nonneg (b-10/11)]
  · linarith [region_four_bound a b h (le_of_lt (lt_of_not_ge halo))]

/-- The optimum is attained at the stated rational thresholds. -/
theorem optimum_value : density (4/11) (10/11) = 9/22 := by
  norm_num [density]

/-- Equality in the global bound is possible only at the unique stated point. -/
theorem equality_iff (a b : ℝ) (h : Admissible a b) :
    density a b = 9/22 ↔ a = 4/11 ∧ b = 10/11 := by
  constructor
  · intro heq
    by_cases hblo : b ≤ 1/2
    · linarith [region_one_bound a b h hblo]
    have hb : 1/2 ≤ b := le_of_lt (lt_of_not_ge hblo)
    by_cases halo : a ≤ 1/2
    · by_cases hablo : a+b ≤ 1
      · linarith [region_two_bound a b halo hb hablo]
      · have hs := stability_sos a b halo hb (le_of_lt (lt_of_not_ge hablo))
        have hzero : (a-4/11)^2 + (b-10/11)^2 = 0 := by
          nlinarith [sq_nonneg ((a-4/11)-(b-10/11)), sq_nonneg (a-4/11),
            sq_nonneg (b-10/11)]
        constructor <;> nlinarith [sq_nonneg (a-4/11), sq_nonneg (b-10/11)]
    · linarith [region_four_bound a b h (le_of_lt (lt_of_not_ge halo))]
  · rintro ⟨rfl, rfl⟩
    exact optimum_value

/-- A complete optimization statement; its domain is the declared template only. -/
theorem unique_global_optimum :
    Admissible (4/11) (10/11) ∧ density (4/11) (10/11) = 9/22 ∧
    ∀ a b : ℝ, Admissible a b →
      density a b ≤ 9/22 ∧ (density a b = 9/22 ↔ a = 4/11 ∧ b = 10/11) := by
  refine ⟨by norm_num [Admissible], optimum_value, ?_⟩
  exact fun a b h => ⟨global_bound a b h, equality_iff a b h⟩

/-- First contiguous odd-block family: its unique optimum is `2/5`. -/
theorem left_boundary_optimum (b : ℝ) (hb0 : 0 ≤ b) (hb1 : b ≤ 1) :
    density 0 b ≤ 2/5 ∧ (density 0 b = 2/5 ↔ b = 2/5) := by
  by_cases hb : b ≤ 1/2
  · have he := region_one 0 b ⟨le_refl 0, hb0, hb1⟩ hb
    constructor
    · exact region_one_bound 0 b ⟨le_refl 0, hb0, hb1⟩ hb
    · constructor
      · intro heq
        nlinarith [sq_nonneg (b-2/5)]
      · intro heq
        rw [heq]
        norm_num [density]
  · have hhalf : 1/2 ≤ b := le_of_lt (lt_of_not_ge hb)
    have hd := region_two_bound 0 b (by norm_num) hhalf (by linarith)
    constructor
    · linarith
    · constructor
      · intro heq
        linarith
      · intro heq
        linarith

/-- Second contiguous odd-block family: the same sharp bound and unique parameter. -/
theorem right_boundary_optimum (a : ℝ) (ha0 : 0 ≤ a) (ha1 : a ≤ 1) :
    density a 1 ≤ 2/5 ∧ (density a 1 = 2/5 ↔ a = 2/5) := by
  by_cases ha : a ≤ 1/2
  · have he := region_three a 1 ha (by norm_num) (by linarith)
    constructor
    · nlinarith [sq_nonneg (a-2/5)]
    · constructor
      · intro heq
        nlinarith [sq_nonneg (a-2/5)]
      · intro heq
        rw [heq]
        norm_num [density]
  · have hd := region_four_bound a 1 ⟨ha0, ha1, le_refl 1⟩
      (le_of_lt (lt_of_not_ge ha))
    constructor
    · linarith
    · constructor
      · intro heq
        linarith
      · intro heq
        linarith

/-- Every parameter pair outperforming the contiguous families lies strictly
inside the region where the exact quadratic stability identity holds, with
both outer odd blocks nonempty. -/
theorem above_contiguous_forces_optimal_region (a b : ℝ) (h : Admissible a b)
    (hd : 2/5 < density a b) :
    0 < a ∧ a < 1/2 ∧ 1/2 < b ∧ b < 1 ∧ 1 < a+b := by
  have hb : 1/2 < b := by
    by_contra hh
    have hx := region_one_bound a b h (le_of_not_gt hh)
    linarith
  have ha : a < 1/2 := by
    by_contra hh
    have hx := region_four_bound a b h (le_of_not_gt hh)
    linarith
  have hab : 1 < a+b := by
    by_contra hh
    have hx := region_two_bound a b (le_of_lt ha) (le_of_lt hb) (le_of_not_gt hh)
    linarith
  have ha0 : 0 < a := by
    by_contra hh
    have heq : a = 0 := by linarith [h.1]
    subst a
    have hx := (left_boundary_optimum b h.2.1 h.2.2).1
    linarith
  have hb1 : b < 1 := by
    by_contra hh
    have heq : b = 1 := by linarith [h.2.2]
    subst b
    have hx := (right_boundary_optimum a h.1 h.2.1).1
    linarith
  exact ⟨ha0, ha, hb, hb1, hab⟩

/-- The gain over the two contiguous subfamilies is exactly `1/110`. -/
theorem strict_template_gain : density (4/11) (10/11) - 2/5 = 1/110 := by
  rw [optimum_value]
  norm_num

/-- The sharp stability coefficient stated in the manuscript, certified for
all thresholds in the region containing the maximizer. -/
theorem sharp_stability (a b : ℝ) (ha : a ≤ 1/2) (hb : 1/2 ≤ b)
    (hab : 1 ≤ a+b) :
    ((4-Real.sqrt 5)/2) * ((a-4/11)^2 + (b-10/11)^2) ≤
      9/22 - density a b := by
  rw [stability_identity a b ha hb hab]
  exact quadratic_spectral_bound (a-4/11) (b-10/11)

/-- All parameters beating the contiguous subfamilies obey sharp stability. -/
theorem above_contiguous_sharp_stability (a b : ℝ) (h : Admissible a b)
    (hd : 2/5 < density a b) :
    ((4-Real.sqrt 5)/2) * ((a-4/11)^2 + (b-10/11)^2) ≤
      9/22 - density a b := by
  obtain ⟨_, ha, hb, _, hab⟩ := above_contiguous_forces_optimal_region a b h hd
  exact sharp_stability a b (le_of_lt ha) (le_of_lt hb) (le_of_lt hab)

#print axioms unique_global_optimum
#print axioms stability_identity
#print axioms stability_sos
#print axioms left_boundary_optimum
#print axioms right_boundary_optimum
#print axioms strict_template_gain
#print axioms above_contiguous_forces_optimal_region
#print axioms sharp_stability
#print axioms above_contiguous_sharp_stability
#print axioms quadratic_spectral_equality_iff
#print axioms quadratic_spectral_coefficient_optimal

end CoPEER.SchurTemplate


/-! # Part B: body of SchurTemplateLimit.lean (verbatim; its Part 1 is the body of SchurTemplateLink.lean) -/

namespace SchurTemplateLink

/-! ## Generic part (verbatim from RainbowSchur.lean) -/


def sumTo (f : Nat → Nat) : Nat → Nat
  | 0 => 0
  | n+1 => sumTo f n + f (n+1)

def rainbowInd (c : Nat → Nat) (x y z : Nat) : Nat :=
  if c x ≠ c y ∧ c x ≠ c z ∧ c y ≠ c z then 1 else 0

def rz (c : Nat → Nat) (z : Nat) : Nat := sumTo (fun x => rainbowInd c x (z - x) z) (z - 1)

def rainbowCount (c : Nat → Nat) (n : Nat) : Nat := sumTo (rz c) n

/-! ## The two-threshold template -/

/-- Even `k`: colour 0.  Odd `k ≤ P` or `k > R`: colour 1.  Odd `P < k ≤ R`: colour 2. -/
def tcol (P R k : Nat) : Nat :=
  if k % 2 = 0 then 0 else if k ≤ P then 1 else if k ≤ R then 2 else 1

theorem tcol_spec (P R k : Nat) :
    (tcol P R k = 0 ∧ k % 2 = 0) ∨ (tcol P R k = 1 ∧ k % 2 = 1 ∧ (k ≤ P ∨ R < k)) ∨
    (tcol P R k = 2 ∧ k % 2 = 1 ∧ P < k ∧ k ≤ R) := by
  unfold tcol; repeat' split
  all_goals omega

theorem sumTo_congr {f g : Nat → Nat} : ∀ n, (∀ k, 1 ≤ k → k ≤ n → f k = g k) → sumTo f n = sumTo g n := by
  intro n
  induction n with
  | zero => intro _; rfl
  | succ n ih =>
    intro h
    simp only [sumTo]
    rw [ih (fun k h1 h2 => h k h1 (by omega)), h (n+1) (by omega) (by omega)]

theorem sumTo_add (f g : Nat → Nat) : ∀ n, sumTo (fun k => f k + g k) n = sumTo f n + sumTo g n := by
  intro n
  induction n with
  | zero => rfl
  | succ n ih => simp only [sumTo]; rw [ih]; omega

def parIn (par lo hi x : Nat) : Nat := if x % 2 = par ∧ lo < x ∧ x ≤ hi then 1 else 0

theorem sum_parIn (par lo hi : Nat) (hp : par ≤ 1) : ∀ t,
    sumTo (parIn par lo hi) t = (min t hi + par)/2 - (lo + par)/2 := by
  intro t
  induction t with
  | zero => simp only [sumTo]; omega
  | succ t ih =>
    simp only [sumTo]; rw [ih]; unfold parIn
    split <;> omega

theorem rainbowInd_spec (c : Nat → Nat) (x y z : Nat) :
    (rainbowInd c x y z = 1 ∧ c x ≠ c y ∧ c x ≠ c z ∧ c y ≠ c z) ∨
    (rainbowInd c x y z = 0 ∧ (c x = c y ∨ c x = c z ∨ c y = c z)) := by
  unfold rainbowInd; split <;> omega

theorem parIn_spec (par lo hi x : Nat) :
    (parIn par lo hi x = 1 ∧ x % 2 = par ∧ lo < x ∧ x ≤ hi) ∨
    (parIn par lo hi x = 0 ∧ (x % 2 ≠ par ∨ x ≤ lo ∨ hi < x)) := by
  unfold parIn; split <;> omega

set_option maxHeartbeats 2000000 in
theorem pt_even (A B k x : Nat) (hAB : A ≤ B) (h1 : 1 ≤ x) (h2 : x ≤ 2*k - 1) :
    rainbowInd (tcol (2*A) (2*B)) x (2*k - x) (2*k) =
      parIn 1 (2*(k-B)) (2*(min A (k-A))) x + parIn 1 (2*(max B (k-B))) (2*(k-A)) x
      + parIn 1 (2*(max A (k-A))) (2*B) x + parIn 1 (2*A) (2*(min B (k-B))) x := by
  have cx := tcol_spec (2*A) (2*B) x
  have cy := tcol_spec (2*A) (2*B) (2*k - x)
  have cz := tcol_spec (2*A) (2*B) (2*k)
  have hr := rainbowInd_spec (tcol (2*A) (2*B)) x (2*k - x) (2*k)
  have p1 := parIn_spec 1 (2*(k-B)) (2*(min A (k-A))) x
  have p2 := parIn_spec 1 (2*(max B (k-B))) (2*(k-A)) x
  have p3 := parIn_spec 1 (2*(max A (k-A))) (2*B) x
  have p4 := parIn_spec 1 (2*A) (2*(min B (k-B))) x
  rcases cx with ⟨cx, px⟩ | ⟨cx, px, qx⟩ | ⟨cx, px, qx, qx'⟩ <;>
  rcases cy with ⟨cy, py⟩ | ⟨cy, py, qy⟩ | ⟨cy, py, qy, qy'⟩ <;>
  rcases cz with ⟨cz, pz⟩ | ⟨cz, pz, qz⟩ | ⟨cz, pz, qz, qz'⟩ <;>
  omega


macro "pt2_tac" P:term "," R:term "," z:term "," x:term "," a:term "," b:term : tactic => `(tactic| (
  have cx := tcol_spec $P $R $x
  have cy := tcol_spec $P $R ($z - $x)
  have cz := tcol_spec $P $R $z
  have hr := rainbowInd_spec (tcol $P $R) $x ($z - $x) $z
  have ha := $a
  have hb := $b
  rcases cx with ⟨cx, px⟩ | ⟨cx, px, qx⟩ | ⟨cx, px, qx, qx'⟩ <;>
  rcases cy with ⟨cy, py⟩ | ⟨cy, py, qy⟩ | ⟨cy, py, qy, qy'⟩ <;>
  rcases cz with ⟨cz, pz⟩ | ⟨cz, pz, qz⟩ | ⟨cz, pz, qz, qz'⟩ <;>
  first
  | omega
  | (rw [cx, cy, cz] at hr
     rcases hr with ⟨hr, _⟩ | ⟨hr, _⟩ <;>
     rcases ha with ⟨ha, _⟩ | ⟨ha, _⟩ <;>
     rcases hb with ⟨hb, _⟩ | ⟨hb, _⟩ <;> omega)))

set_option maxHeartbeats 1000000 in
theorem pt_low (P R z x : Nat) (_h1 : 1 ≤ x) (_h2 : x ≤ z - 1) (hb : z ≤ P) :
    rainbowInd (tcol P R) x (z - x) z = 0 := by
  pt2_tac P, R, z, x, parIn_spec 0 0 0 x, parIn_spec 0 0 0 x

set_option maxHeartbeats 1000000 in
theorem pt_odd_mid (P R z x : Nat) (h1 : 1 ≤ x) (h2 : x ≤ z - 1)
    (hp : z % 2 = 1) (hP : P % 2 = 0) (ha : P < z) (hb : z ≤ R) :
    rainbowInd (tcol P R) x (z - x) z = parIn 0 (z-P-1) (z-1) x + parIn 1 0 P x := by
  pt2_tac P, R, z, x, parIn_spec 0 (z-P-1) (z-1) x, parIn_spec 1 0 P x

set_option maxHeartbeats 1000000 in
theorem pt_odd_high (P R z x : Nat) (_h1 : 1 ≤ x) (_h2 : x ≤ z - 1)
    (hp : z % 2 = 1) (hP : P % 2 = 0) (hR : R % 2 = 0) (hPR : P ≤ R) (ha : R < z) :
    rainbowInd (tcol P R) x (z - x) z = parIn 0 (z-R-1) (z-P-1) x + parIn 1 P R x := by
  pt2_tac P, R, z, x, parIn_spec 0 (z-R-1) (z-P-1) x, parIn_spec 1 P R x

theorem sumTo_zero : ∀ n, sumTo (fun _ => 0) n = 0 := by
  intro n; induction n with
  | zero => rfl
  | succ n ih => simp only [sumTo]; omega

theorem rz_two (c : Nat → Nat) (z a1 a2 a3 b1 b2 b3 : Nat) (ha : a1 ≤ 1) (hb : b1 ≤ 1)
    (h : ∀ x, 1 ≤ x → x ≤ z - 1 →
      rainbowInd c x (z - x) z = parIn a1 a2 a3 x + parIn b1 b2 b3 x) :
    rz c z = ((min (z-1) a3 + a1)/2 - (a2 + a1)/2) + ((min (z-1) b3 + b1)/2 - (b2 + b1)/2) := by
  unfold rz
  rw [sumTo_congr (z-1) h, sumTo_add, sum_parIn a1 a2 a3 ha, sum_parIn b1 b2 b3 hb]

theorem rz_four (c : Nat → Nat) (z a2 a3 b2 b3 c2 c3 d2 d3 : Nat)
    (h : ∀ x, 1 ≤ x → x ≤ z - 1 →
      rainbowInd c x (z - x) z = parIn 1 a2 a3 x + parIn 1 b2 b3 x + parIn 1 c2 c3 x + parIn 1 d2 d3 x) :
    rz c z = ((min (z-1) a3 + 1)/2 - (a2 + 1)/2) + ((min (z-1) b3 + 1)/2 - (b2 + 1)/2)
      + ((min (z-1) c3 + 1)/2 - (c2 + 1)/2) + ((min (z-1) d3 + 1)/2 - (d2 + 1)/2) := by
  unfold rz
  rw [sumTo_congr (z-1) h, sumTo_add, sumTo_add, sumTo_add,
    sum_parIn 1 a2 a3 (by omega), sum_parIn 1 b2 b3 (by omega),
    sum_parIn 1 c2 c3 (by omega), sum_parIn 1 d2 d3 (by omega)]

/-- closed form of r(2k-1) -/
def ro (A B k : Nat) : Nat := if k ≤ A then 0 else if k ≤ B then 2*A else 2*(B-A)

theorem rz_odd (A B k : Nat) (hAB : A ≤ B) (hk : 1 ≤ k) :
    rz (tcol (2*A) (2*B)) (2*k-1) = ro A B k := by
  unfold ro
  by_cases c1 : k ≤ A
  · simp only [c1, ↓reduceIte]
    unfold rz
    rw [sumTo_congr (g := fun _ => 0) (2*k-1-1)
      (fun x h1 h2 => pt_low (2*A) (2*B) (2*k-1) x h1 h2 (by omega))]
    exact sumTo_zero _
  · simp only [c1, ↓reduceIte]
    by_cases c2 : k ≤ B
    · simp only [c2, ↓reduceIte]
      rw [rz_two _ (2*k-1) _ _ _ _ _ _ (by omega) (by omega)
        (fun x h1 h2 => pt_odd_mid (2*A) (2*B) (2*k-1) x h1 h2 (by omega) (by omega) (by omega) (by omega))]
      omega
    · simp only [c2, ↓reduceIte]
      rw [rz_two _ (2*k-1) _ _ _ _ _ _ (by omega) (by omega)
        (fun x h1 h2 => pt_odd_high (2*A) (2*B) (2*k-1) x h1 h2 (by omega) (by omega) (by omega) (by omega) (by omega))]
      omega

/-! The arithmetic of the even case, split into four small identities: one per rectangle of the
(colour-1 addend, colour-2 addend) plane, each an inclusion-exclusion over lower corners.
(A single `omega` call on the combined statement costs over 6 GB; these cost under 1 GB.) -/

theorem half_cnt (k lo hi : Nat) : (min (2*k-1) (2*hi) + 1)/2 - (2*lo + 1)/2 = min k hi - lo := by omega

theorem ea1 (A B k : Nat) (hAB : A ≤ B) :
    (min k (min A (k-A)) - (k-B)) + ((k-B) + (k-2*A)) = (k-A) + (k-(A+B)) := by omega
theorem ea2 (A B k : Nat) (hAB : A ≤ B) :
    (min k (k-A) - max B (k-B)) + (k-2*B) = k-(A+B) := by omega
theorem ea3 (A B k : Nat) (hAB : A ≤ B) :
    (min k B - max A (k-A)) + ((k-B) + (k-2*A)) = (k-A) + (k-(A+B)) := by omega
theorem ea4 (A B k : Nat) (hAB : A ≤ B) :
    (min k (min B (k-B)) - A) + (k-2*B) = k-(A+B) := by omega

theorem even_arith (A B k : Nat) (hAB : A ≤ B) :
    ((min (2*k-1) (2*(min A (k-A))) + 1)/2 - (2*(k-B) + 1)/2)
      + ((min (2*k-1) (2*(k-A)) + 1)/2 - (2*(max B (k-B)) + 1)/2)
      + ((min (2*k-1) (2*B) + 1)/2 - (2*(max A (k-A)) + 1)/2)
      + ((min (2*k-1) (2*(min B (k-B))) + 1)/2 - (2*A + 1)/2)
      + (2*(k-B) + 2*(k-2*A) + 2*(k-2*B)) = 2*(k-A) + 4*(k-(A+B)) := by
  rw [half_cnt, half_cnt, half_cnt, half_cnt]
  have h1 := ea1 A B k hAB
  have h2 := ea2 A B k hAB
  have h3 := ea3 A B k hAB
  have h4 := ea4 A B k hAB
  generalize min k (min A (k-A)) - (k-B) = t1 at *
  generalize min k (k-A) - max B (k-B) = t2 at *
  generalize min k B - max A (k-A) = t3 at *
  generalize min k (min B (k-B)) - A = t4 at *
  omega

/-- `r(2k)` for the template, for EVERY `k` and every `A ≤ B`, written without subtraction. -/
theorem rz_even (A B k : Nat) (hAB : A ≤ B) :
    rz (tcol (2*A) (2*B)) (2*k) + (2*(k-B) + 2*(k-2*A) + 2*(k-2*B)) = 2*(k-A) + 4*(k-(A+B)) := by
  rw [rz_four _ (2*k) _ _ _ _ _ _ _ _ (fun x h1 h2 => pt_even A B k x hAB h1 h2)]
  exact even_arith A B k hAB


/-! ## Outer sum and the uniform exact count -/

theorem sumTo_pairs (g : Nat → Nat) : ∀ K, sumTo g (2*K) = sumTo (fun k => g (2*k-1) + g (2*k)) K := by
  intro K
  induction K with
  | zero => rfl
  | succ K ih =>
    have e2 : 2*(K+1) = (2*K+1)+1 := by omega
    have e1 : 2*(K+1)-1 = 2*K+1 := by omega
    show sumTo g (2*(K+1)) = sumTo (fun k => g (2*k-1) + g (2*k)) K + (g (2*(K+1)-1) + g (2*(K+1)))
    rw [e1, e2]
    show sumTo g (2*K) + g (2*K+1) + g (2*K+1+1) = _
    rw [ih]; omega

theorem sumTo_split (f : Nat → Nat) (a : Nat) : ∀ d, sumTo f (a+d) = sumTo f a + sumTo (fun j => f (a+j)) d := by
  intro d
  induction d with
  | zero => rfl
  | succ d ih =>
    have e : a + (d+1) = (a+d)+1 := by omega
    rw [e]; simp only [sumTo]; rw [ih, e]; omega

theorem sumTo_const (c : Nat) : ∀ n, sumTo (fun _ => c) n = n*c := by
  intro n
  induction n with
  | zero => simp [sumTo]
  | succ n ih => simp only [sumTo]; rw [ih]; grind

/-- `sum_{k=1}^{n} 2 (k ∸ U) = (n ∸ U)(n ∸ U + 1)`: twice a triangular number. -/
theorem sumTo_tsub (U : Nat) : ∀ n, sumTo (fun k => 2*(k-U)) n = (n-U)*(n-U+1) := by
  intro n
  induction n with
  | zero => simp [sumTo]
  | succ n ih =>
    simp only [sumTo]; rw [ih]
    by_cases h : n + 1 ≤ U
    · have e1 : n + 1 - U = 0 := by omega
      have e2 : n - U = 0 := by omega
      rw [e1, e2]
    · obtain ⟨d, rfl⟩ : ∃ d, n = U + d := ⟨n - U, by omega⟩
      have e1 : U + d + 1 - U = d + 1 := by omega
      have e2 : U + d - U = d := by omega
      rw [e1, e2]; grind

theorem sumTo_add_eq {f g h : Nat → Nat} (n : Nat)
    (H : ∀ k, 1 ≤ k → k ≤ n → f k + g k = h k) : sumTo f n + sumTo g n = sumTo h n := by
  rw [← sumTo_add]; exact sumTo_congr n H

theorem sum_ro (A d e : Nat) : sumTo (ro A (A+d)) (A+d+e) = d*(2*A) + e*(2*d) := by
  rw [sumTo_split, sumTo_split]
  have s1 : sumTo (ro A (A+d)) A = 0 := by
    rw [sumTo_congr (g := fun _ => 0) A (fun k _ h2 => by show ro A (A+d) k = 0; unfold ro; simp only [h2, ↓reduceIte])]
    exact sumTo_zero _
  have s2 : sumTo (fun j => ro A (A+d) (A+j)) d = d*(2*A) := by
    rw [sumTo_congr (g := fun _ => 2*A) d (fun j h1 h2 => by
      show ro A (A+d) (A+j) = 2*A
      unfold ro; repeat' split
      all_goals omega)]
    exact sumTo_const _ _
  have s3 : sumTo (fun j => ro A (A+d) (A+d+j)) e = e*(2*d) := by
    rw [sumTo_congr (g := fun _ => 2*d) e (fun j h1 h2 => by
      show ro A (A+d) (A+d+j) = 2*d
      unfold ro; repeat' split
      all_goals omega)]
    exact sumTo_const _ _
  rw [s1, s2, s3]; omega

theorem sum_ro' (A B N : Nat) (hAB : A ≤ B) (hBN : B ≤ N) :
    sumTo (ro A B) N = 2*(B-A)*(N-B+A) := by
  obtain ⟨d, rfl⟩ : ∃ d, B = A + d := ⟨B - A, by omega⟩
  obtain ⟨e, rfl⟩ : ∃ e, N = A + d + e := ⟨N - (A + d), by omega⟩
  rw [sum_ro]
  have e1 : A + d - A = d := by omega
  have e2 : A + d + e - (A + d) + A = e + A := by omega
  rw [e1, e2]; grind

/-- `hh t = t (t+1)`, twice the `t`-th triangular number. -/
def hh (t : Nat) : Nat := t*(t+1)

theorem template_count (A B N : Nat) (hAB : A ≤ B) (hBN : B ≤ N) :
    rainbowCount (tcol (2*A) (2*B)) (2*N) + (hh (N-B) + hh (N-2*A) + hh (N-2*B))
      = 2*(B-A)*(N-B+A) + hh (N-A) + 2*hh (N-(A+B)) := by
  unfold rainbowCount
  rw [sumTo_pairs]
  have key : ∀ k, 1 ≤ k → k ≤ N →
      (rz (tcol (2*A) (2*B)) (2*k-1) + rz (tcol (2*A) (2*B)) (2*k))
        + (2*(k-B) + 2*(k-2*A) + 2*(k-2*B))
      = ro A B k + 2*(k-A) + (2*(k-(A+B)) + 2*(k-(A+B))) := by
    intro k h1 _
    have e1 := rz_odd A B k hAB h1
    have e2 := rz_even A B k hAB
    omega
  have S := sumTo_add_eq N key
  have Sg : sumTo (fun k => 2*(k-B) + 2*(k-2*A) + 2*(k-2*B)) N
      = hh (N-B) + hh (N-2*A) + hh (N-2*B) := by
    rw [sumTo_add, sumTo_add, sumTo_tsub, sumTo_tsub, sumTo_tsub]; rfl
  have Sh : sumTo (fun k => ro A B k + 2*(k-A) + (2*(k-(A+B)) + 2*(k-(A+B)))) N
      = sumTo (ro A B) N + hh (N-A) + (hh (N-(A+B)) + hh (N-(A+B))) := by
    rw [sumTo_add, sumTo_add, sumTo_add, sumTo_tsub, sumTo_tsub]; rfl
  rw [Sg, Sh, sum_ro' A B N hAB hBN] at S
  omega


/-! ## The four polynomial regions -/

theorem region3 (A B N : Nat) (hAB : A ≤ B) (hBN : B ≤ N)
    (h1 : 2*A ≤ N) (h2 : N ≤ 2*B) (h3 : N ≤ A + B) :
    rainbowCount (tcol (2*A) (2*B)) (2*N) + (5*(A*A) + 3*(B*B) + N*N + N)
      = 4*(A*B) + 4*(B*N) + A + B := by
  have S := template_count A B N hAB hBN
  unfold hh at S
  obtain ⟨x, hx1, hx2⟩ : ∃ x, N - B = x ∧ N = B + x := ⟨N - B, rfl, by omega⟩
  obtain ⟨y, hy1, hy2⟩ : ∃ y, N - 2*A = y ∧ N = 2*A + y := ⟨N - 2*A, rfl, by omega⟩
  obtain ⟨z, hz1, hz2⟩ : ∃ z, N - A = z ∧ N = A + z := ⟨N - A, rfl, by omega⟩
  obtain ⟨w, hw1, hw2⟩ : ∃ w, B - A = w ∧ B = A + w := ⟨B - A, rfl, by omega⟩
  have e0 : N - 2*B = 0 := by omega
  have e1 : N - (A+B) = 0 := by omega
  rw [hx1, hy1, hz1, hw1, e0, e1] at S
  grind

theorem region1 (A B N : Nat) (hAB : A ≤ B) (h1 : 2*B ≤ N) :
    rainbowCount (tcol (2*A) (2*B)) (2*N) + (3*(A*A) + 5*(B*B) + 4*(A*N) + A)
      = 8*(A*B) + 4*(B*N) + B := by
  have S := template_count A B N hAB (by omega)
  unfold hh at S
  obtain ⟨x, hx1, hx2⟩ : ∃ x, N - B = x ∧ N = B + x := ⟨N - B, rfl, by omega⟩
  obtain ⟨y, hy1, hy2⟩ : ∃ y, N - 2*A = y ∧ N = 2*A + y := ⟨N - 2*A, rfl, by omega⟩
  obtain ⟨z, hz1, hz2⟩ : ∃ z, N - A = z ∧ N = A + z := ⟨N - A, rfl, by omega⟩
  obtain ⟨w, hw1, hw2⟩ : ∃ w, B - A = w ∧ B = A + w := ⟨B - A, rfl, by omega⟩
  obtain ⟨u, hu1, hu2⟩ : ∃ u, N - 2*B = u ∧ N = 2*B + u := ⟨N - 2*B, rfl, by omega⟩
  obtain ⟨v, hv1, hv2⟩ : ∃ v, N - (A+B) = v ∧ N = A + B + v := ⟨N - (A+B), rfl, by omega⟩
  rw [hx1, hy1, hz1, hw1, hu1, hv1] at S
  grind

theorem region2 (A B N : Nat) (hAB : A ≤ B) (hBN : B ≤ N)
    (h1 : N ≤ 2*B) (h2 : A + B ≤ N) :
    rainbowCount (tcol (2*A) (2*B)) (2*N) + (3*(A*A) + B*B + 4*(A*N) + A + B)
      = 8*(A*B) + N*N + N := by
  have S := template_count A B N hAB hBN
  unfold hh at S
  obtain ⟨x, hx1, hx2⟩ : ∃ x, N - B = x ∧ N = B + x := ⟨N - B, rfl, by omega⟩
  obtain ⟨y, hy1, hy2⟩ : ∃ y, N - 2*A = y ∧ N = 2*A + y := ⟨N - 2*A, rfl, by omega⟩
  obtain ⟨z, hz1, hz2⟩ : ∃ z, N - A = z ∧ N = A + z := ⟨N - A, rfl, by omega⟩
  obtain ⟨w, hw1, hw2⟩ : ∃ w, B - A = w ∧ B = A + w := ⟨B - A, rfl, by omega⟩
  obtain ⟨v, hv1, hv2⟩ : ∃ v, N - (A+B) = v ∧ N = A + B + v := ⟨N - (A+B), rfl, by omega⟩
  have e0 : N - 2*B = 0 := by omega
  rw [hx1, hy1, hz1, hw1, hv1, e0] at S
  grind

theorem region4 (A B N : Nat) (hAB : A ≤ B) (hBN : B ≤ N) (h1 : N ≤ 2*A) :
    rainbowCount (tcol (2*A) (2*B)) (2*N) + (A*A + 3*(B*B) + 4*(A*N) + A)
      = 4*(A*B) + 4*(B*N) + B := by
  have S := template_count A B N hAB hBN
  unfold hh at S
  obtain ⟨x, hx1, hx2⟩ : ∃ x, N - B = x ∧ N = B + x := ⟨N - B, rfl, by omega⟩
  obtain ⟨z, hz1, hz2⟩ : ∃ z, N - A = z ∧ N = A + z := ⟨N - A, rfl, by omega⟩
  obtain ⟨w, hw1, hw2⟩ : ∃ w, B - A = w ∧ B = A + w := ⟨B - A, rfl, by omega⟩
  have e0 : N - 2*B = 0 := by omega
  have e1 : N - (A+B) = 0 := by omega
  have e2 : N - 2*A = 0 := by omega
  rw [hx1, hz1, hw1, e0, e1, e2] at S
  grind

/-! ## Normalisation: the source's equations (1), (2), (3) -/

/-- Source eq. (2): `|S^(z)| = z - 1`; eq. (1): `|S| = binom(n,2)`. Twice the number of ordered
Schur triples in `[n]` is `n (n-1)`. -/
theorem schur_total : ∀ n, 2 * sumTo (fun z => z - 1) n = n * (n - 1) := by
  intro n
  induction n with
  | zero => rfl
  | succ n ih =>
    simp only [sumTo]
    cases n with
    | zero => rfl
    | succ k =>
      have e : k + 1 + 1 - 1 = k + 1 := by omega
      have e' : k + 1 - 1 = k := by omega
      rw [e] at *
      rw [e'] at ih
      grind

theorem rainbowInd_le_one (c : Nat → Nat) (x y z : Nat) : rainbowInd c x y z ≤ 1 := by
  unfold rainbowInd; split <;> omega

theorem sumTo_le {f g : Nat → Nat} (h : ∀ k, f k ≤ g k) : ∀ n, sumTo f n ≤ sumTo g n := by
  intro n
  induction n with
  | zero => exact Nat.le_refl _
  | succ n ih => simp only [sumTo]; have := h (n+1); omega

/-- Source eq. (3): `r(z) ≤ |S^(z)| = z - 1`. -/
theorem rz_le (c : Nat → Nat) (z : Nat) : rz c z ≤ z - 1 := by
  unfold rz
  have h := sumTo_le (f := fun x => rainbowInd c x (z - x) z) (g := fun _ => 1)
    (fun k => rainbowInd_le_one c k (z - k) z) (z - 1)
  rw [sumTo_const] at h; omega

/-- The rainbow count never exceeds the number of Schur triples: the fraction is at most 1. -/
theorem rainbowCount_le (c : Nat → Nat) (n : Nat) : 2 * rainbowCount c n ≤ n * (n - 1) := by
  rw [← schur_total n]
  have := sumTo_le (rz_le c) n
  unfold rainbowCount; omega

/-- Only the colours of `1, ..., n` matter: the count is a function of a colouring of `[n]`. -/
theorem rainbowCount_congr (c c' : Nat → Nat) (n : Nat) (h : ∀ k, 1 ≤ k → k ≤ n → c k = c' k) :
    rainbowCount c n = rainbowCount c' n := by
  unfold rainbowCount
  apply sumTo_congr
  intro z hz1 hz2
  unfold rz
  apply sumTo_congr
  intro x hx1 hx2
  unfold rainbowInd
  rw [h x hx1 (by omega), h (z - x) (by omega) (by omega), h z hz1 hz2]

/-- Monotonicity in `n`: a colouring of `[n+d]` restricted to `[n]` keeps its rainbow triples. -/
theorem rainbowCount_mono (c : Nat → Nat) (n d : Nat) : rainbowCount c n ≤ rainbowCount c (n + d) := by
  unfold rainbowCount; rw [sumTo_split]; omega

/-- A differently shaped definition: filter all pairs `(x,y)` of `[n]²`. -/
def bruteCount (c : Nat → Nat) (n : Nat) : Nat :=
  ((List.range (n+1)).flatMap fun x => (List.range (n+1)).filter fun y =>
    decide (1 ≤ x) && decide (1 ≤ y) && decide (x + y ≤ n) &&
    decide (c x ≠ c y) && decide (c x ≠ c (x+y)) && decide (c y ≠ c (x+y))).length

/-! ## The same count indexed by the summands `(x, y)`, and as the length of a duplicate-free list

`rainbowCount` sums the source's `r(z)` over the largest element `z`.  Below: (i) the same number
summed over the summands `(x, y)` (the form `R_n(c)` used by Hegde, Kumar and Pratibha), for every
colouring and every `n`; (ii) the same number as the length of the rainbow sublist of an explicit
duplicate-free list `schurPairs n` whose members are exactly the pairs `1 ≤ x`, `1 ≤ y`,
`x + y ≤ n`; (iii) that list has `binom(n,2)` elements. -/

/-- Summation over the largest element equals summation over the summands, for any weight `f`. -/
theorem sum_swap (f : Nat → Nat → Nat → Nat) : ∀ n,
    sumTo (fun z => sumTo (fun x => f x (z - x) z) (z - 1)) n
      = sumTo (fun x => sumTo (fun y => f x y (x + y)) (n - x)) n := by
  intro n
  induction n with
  | zero => rfl
  | succ n ih =>
    show sumTo (fun z => sumTo (fun x => f x (z - x) z) (z - 1)) n
        + sumTo (fun x => f x (n + 1 - x) (n + 1)) (n + 1 - 1) =
      sumTo (fun x => sumTo (fun y => f x y (x + y)) (n + 1 - x)) n
        + sumTo (fun y => f (n+1) y (n + 1 + y)) (n + 1 - (n + 1))
    have e0 : n + 1 - (n + 1) = 0 := by omega
    have e3 : n + 1 - 1 = n := by omega
    rw [e0, e3]
    show _ = _ + 0
    have hx : ∀ x, 1 ≤ x → x ≤ n →
        sumTo (fun y => f x y (x + y)) (n + 1 - x)
          = sumTo (fun y => f x y (x + y)) (n - x) + f x (n + 1 - x) (n + 1) := by
      intro x h1 h2
      have e1 : n + 1 - x = (n - x) + 1 := by omega
      have e2 : x + ((n - x) + 1) = n + 1 := by omega
      rw [e1]
      show sumTo (fun y => f x y (x + y)) (n - x) + f x (n - x + 1) (x + (n - x + 1)) = _
      rw [e2]
    rw [sumTo_congr n hx, sumTo_add, ih]; omega

/-- Count indexed by the summands: `#{(x,y) : 1 ≤ x, 1 ≤ y, x + y ≤ n, (x,y,x+y) rainbow}`. -/
def pairCount (c : Nat → Nat) (n : Nat) : Nat :=
  sumTo (fun x => sumTo (fun y => rainbowInd c x y (x + y)) (n - x)) n

theorem rainbowCount_eq_pairCount (c : Nat → Nat) (n : Nat) : rainbowCount c n = pairCount c n :=
  sum_swap (rainbowInd c) n

/-- A sum of indicators is the length of a filtered list. -/
theorem sumTo_ind_eq_length (p : Nat → Bool) : ∀ n,
    sumTo (fun k => if p k then 1 else 0) n = ((List.range' 1 n).filter p).length := by
  intro n
  induction n with
  | zero => rfl
  | succ n ih =>
    simp only [sumTo]
    rw [ih, List.range'_concat, List.filter_append, List.length_append]
    have e : 1 + 1 * n = n + 1 := by omega
    rw [e]
    cases h : p (n+1) <;> simp [List.filter, h]

/-- All ordered pairs `(x, y)` with `1 ≤ x`, `1 ≤ y`, `x + y ≤ n`: the Schur triples `(x, y, x+y)` of `[n]`. -/
def schurPairs (n : Nat) : List (Nat × Nat) :=
  (List.range' 1 n).flatMap fun x => (List.range' 1 (n - x)).map fun y => (x, y)

theorem mem_schurPairs (n x y : Nat) : (x, y) ∈ schurPairs n ↔ 1 ≤ x ∧ 1 ≤ y ∧ x + y ≤ n := by
  unfold schurPairs
  simp only [List.mem_flatMap, List.mem_map, List.mem_range'_1, Prod.mk.injEq]
  constructor
  · rintro ⟨a, ha, b, hb, rfl, rfl⟩; omega
  · intro h; exact ⟨x, by omega, y, by omega, rfl, rfl⟩

theorem nodup_range1 (k : Nat) : (List.range' 1 k).Nodup := List.nodup_range' (step := 1)

theorem nodup_flatMap_range {β : Type} (F : Nat → List β) (h1 : ∀ x, (F x).Nodup)
    (h2 : ∀ x x' b, b ∈ F x → b ∈ F x' → x = x') : ∀ k, ((List.range' 1 k).flatMap F).Nodup := by
  intro k
  induction k with
  | zero => exact List.Pairwise.nil
  | succ k ih =>
    have e : 1 + 1 * k = k + 1 := by omega
    rw [List.range'_concat, List.flatMap_append, e]
    unfold List.Nodup
    rw [List.pairwise_append]
    refine ⟨ih, ?_, ?_⟩
    · have e2 : [k+1].flatMap F = F (k+1) := by simp
      rw [e2]; exact h1 (k+1)
    · intro a ha b hb hab
      rw [List.mem_flatMap] at ha hb
      obtain ⟨x, hx, hax⟩ := ha
      obtain ⟨x', hx', hbx'⟩ := hb
      rw [List.mem_range'_1] at hx
      have hx'' : x' = k + 1 := by simpa using hx'
      subst hab
      have := h2 x x' a hax hbx'
      omega

theorem nodup_schurPairs (n : Nat) : (schurPairs n).Nodup := by
  unfold schurPairs
  apply nodup_flatMap_range
  · intro x
    unfold List.Nodup
    rw [List.pairwise_map]
    have := nodup_range1 (n - x)
    unfold List.Nodup at this
    exact this.imp (fun h h' => h (by simpa using h'))
  · intro x x' b hb hb'
    rw [List.mem_map] at hb hb'
    obtain ⟨y, _, rfl⟩ := hb
    obtain ⟨y', _, h⟩ := hb'
    have := congrArg Prod.fst h
    simpa using this.symm

/-- Boolean rainbow test on a pair `(x, y)`, third element `x + y`. -/
def isRainbowPair (c : Nat → Nat) (p : Nat × Nat) : Bool :=
  decide (c p.1 ≠ c p.2 ∧ c p.1 ≠ c (p.1 + p.2) ∧ c p.2 ≠ c (p.1 + p.2))

theorem length_filter_flatMap_range {β : Type} (F : Nat → List β) (p : β → Bool) : ∀ k,
    (((List.range' 1 k).flatMap F).filter p).length = sumTo (fun x => ((F x).filter p).length) k := by
  intro k
  induction k with
  | zero => rfl
  | succ k ih =>
    have e : 1 + 1 * k = k + 1 := by omega
    rw [List.range'_concat, List.flatMap_append, List.filter_append, List.length_append, ih, e]
    simp [sumTo]

theorem pairCount_eq_length (c : Nat → Nat) (n : Nat) :
    pairCount c n = ((schurPairs n).filter (isRainbowPair c)).length := by
  unfold schurPairs pairCount
  rw [length_filter_flatMap_range]
  apply sumTo_congr
  intro x _ _
  rw [List.filter_map, List.length_map]
  rw [← sumTo_ind_eq_length]
  apply sumTo_congr
  intro y _ _
  unfold rainbowInd isRainbowPair
  simp

/-- **The count is a cardinality**: `rainbowCount c n` is the number of rainbow members of the
duplicate-free list of all Schur pairs of `[n]`. -/
theorem rainbowCount_eq_length (c : Nat → Nat) (n : Nat) :
    rainbowCount c n = ((schurPairs n).filter (isRainbowPair c)).length := by
  rw [rainbowCount_eq_pairCount, pairCount_eq_length]

theorem length_flatMap_range {β : Type} (F : Nat → List β) : ∀ k,
    ((List.range' 1 k).flatMap F).length = sumTo (fun x => (F x).length) k := by
  intro k
  induction k with
  | zero => rfl
  | succ k ih =>
    have e : 1 + 1 * k = k + 1 := by omega
    rw [List.range'_concat, List.flatMap_append, List.length_append, ih, e]
    simp [sumTo]

/-- The source's eq. (1) for the list: there are exactly `binom(n,2)` Schur pairs. -/
theorem schurPairs_length (n : Nat) : 2 * (schurPairs n).length = n * (n - 1) := by
  unfold schurPairs
  rw [length_flatMap_range]
  have h2 : ∀ x, 1 ≤ x → x ≤ n →
      ((List.range' 1 (n - x)).map fun y => (x, y)).length = sumTo (fun _ => 1) (n - x) := by
    intro x _ _
    rw [List.length_map, List.length_range', sumTo_const, Nat.mul_one]
  rw [sumTo_congr n h2]
  have h3 : sumTo (fun z => sumTo (fun _ => 1) (z - 1)) n
      = sumTo (fun x => sumTo (fun _ => 1) (n - x)) n := sum_swap (fun _ _ _ => 1) n
  rw [← h3]
  have h4 : ∀ z, 1 ≤ z → z ≤ n → sumTo (fun _ => 1) (z - 1) = z - 1 := by
    intro z _ _
    rw [sumTo_const, Nat.mul_one]
  rw [sumTo_congr n h4]
  exact schur_total n

/-! ## Colour names do not matter -/

/-- Renaming colours by an injective map leaves the rainbow count unchanged; in particular the
proposition's colour names `1, 2, 3` and the names `0, 1, 2` used here give the same count. -/
theorem rainbowCount_rename (σ : Nat → Nat) (hσ : ∀ i j, σ i = σ j → i = j) (c : Nat → Nat) (n : Nat) :
    rainbowCount (fun k => σ (c k)) n = rainbowCount c n := by
  have e : ∀ i j, (σ i ≠ σ j) = (i ≠ j) := fun i j =>
    propext ⟨fun h h' => h (h' ▸ rfl), fun h h' => h (hσ i j h')⟩
  unfold rainbowCount
  apply sumTo_congr
  intro z _ _
  unfold rz
  apply sumTo_congr
  intro x _ _
  unfold rainbowInd
  simp only [e]

/-! ## The proposition's colouring with rational thresholds `a = p/q`, `b = r/q` -/

/-- The colouring of Proposition `prop:schur-template-optimum` on `[n]` for `a = p/q`, `b = r/q`:
even `k` get colour 0; odd `k` get colour 1 when `k/n ≤ a` or `k/n > b`, and colour 2 otherwise.
The two comparisons are cross-multiplied by `q n`: `k/n ≤ p/q ↔ k q ≤ p n`, `k/n > r/q ↔ r n < k q`. -/
def propCol (p r q n k : Nat) : Nat :=
  if k % 2 = 0 then 0 else if k * q ≤ p * n ∨ r * n < k * q then 1 else 2

/-- For EVERY `n`, the proposition's colouring is the template with even thresholds
`2 ⌈⌊p n / q⌋ / 2⌉` and `2 ⌈⌊r n / q⌋ / 2⌉`. -/
theorem propCol_eq_tcol (p r q n k : Nat) (hq : 1 ≤ q) (hpr : p ≤ r) :
    propCol p r q n k = tcol (2*((p*n/q + 1)/2)) (2*((r*n/q + 1)/2)) k := by
  have hFG : p*n/q ≤ r*n/q := Nat.div_le_div_right (Nat.mul_le_mul_right n hpr)
  have e1 : k * q ≤ p * n ↔ k ≤ p*n/q := (Nat.le_div_iff_mul_le (by omega)).symm
  have e2 : r * n < k * q ↔ r*n/q < k := (Nat.div_lt_iff_lt_mul (by omega)).symm
  unfold propCol tcol
  generalize p*n/q = F at *
  generalize r*n/q = G at *
  repeat' split
  all_goals omega

theorem threshold_bounds (p r q N : Nat) (hq : 1 ≤ q) (hpr : p ≤ r) (hrq : r ≤ q) :
    (p*(2*N)/q + 1)/2 ≤ (r*(2*N)/q + 1)/2 ∧ (r*(2*N)/q + 1)/2 ≤ N := by
  have hFG : p*(2*N)/q ≤ r*(2*N)/q := Nat.div_le_div_right (Nat.mul_le_mul_right _ hpr)
  have hG : r*(2*N)/q ≤ 2*N := by
    have h1 : r*(2*N)/q ≤ q*(2*N)/q := Nat.div_le_div_right (Nat.mul_le_mul_right _ hrq)
    have h2 : q*(2*N)/q = 2*N := Nat.mul_div_cancel_left _ (by omega)
    omega
  omega

/-- **Exact count for the proposition's colouring at every even `n = 2N`** and all rational
thresholds `0 ≤ p/q ≤ r/q ≤ 1`, with `A = ⌈⌊p n/q⌋/2⌉`, `B = ⌈⌊r n/q⌋/2⌉`. -/
theorem prop_count_even (p r q N : Nat) (hq : 1 ≤ q) (hpr : p ≤ r) (hrq : r ≤ q) :
    rainbowCount (propCol p r q (2*N)) (2*N)
        + (hh (N - (r*(2*N)/q + 1)/2) + hh (N - 2*((p*(2*N)/q + 1)/2)) + hh (N - 2*((r*(2*N)/q + 1)/2)))
      = 2*((r*(2*N)/q + 1)/2 - (p*(2*N)/q + 1)/2)*(N - (r*(2*N)/q + 1)/2 + (p*(2*N)/q + 1)/2)
        + hh (N - (p*(2*N)/q + 1)/2)
        + 2*hh (N - ((p*(2*N)/q + 1)/2 + (r*(2*N)/q + 1)/2)) := by
  have hb := threshold_bounds p r q N hq hpr hrq
  rw [rainbowCount_congr _ _ (2*N) (fun k _ _ => propCol_eq_tcol p r q (2*N) k hq hpr)]
  exact template_count _ _ N hb.1 hb.2

/-- At `n = 2 q m` the thresholds are exactly `2 p m` and `2 r m`: no rounding occurs. -/
theorem propCol_at (p r q m k : Nat) (hq : 1 ≤ q) (hpr : p ≤ r) :
    propCol p r q (2*q*m) k = tcol (2*(p*m)) (2*(r*m)) k := by
  rw [propCol_eq_tcol p r q (2*q*m) k hq hpr]
  have e1 : p*(2*q*m) = (2*(p*m))*q := by grind
  have e2 : r*(2*q*m) = (2*(r*m))*q := by grind
  rw [e1, e2, Nat.mul_div_cancel _ (by omega : 0 < q), Nat.mul_div_cancel _ (by omega : 0 < q)]
  have e3 : (2*(p*m) + 1)/2 = p*m := by omega
  have e4 : (2*(r*m) + 1)/2 = r*m := by omega
  rw [e3, e4]

/-- **Exact count in the stability region**, `a = p/q ≤ 1/2 ≤ b = r/q`, `a + b ≥ 1`, at `n = 2 q m`,
for ALL `m`:  `R = (4pr + 4rq - 5p² - 3r² - q²) m² + (p + r - q) m`, written without subtraction. -/
theorem rational_count (p r q m : Nat) (hq : 1 ≤ q) (hpr : p ≤ r) (hrq : r ≤ q)
    (h1 : 2*p ≤ q) (h2 : q ≤ 2*r) (h3 : q ≤ p + r) :
    rainbowCount (propCol p r q (2*q*m)) (2*q*m) + ((5*(p*p) + 3*(r*r) + q*q)*(m*m) + q*m)
      = (4*(p*r) + 4*(r*q))*(m*m) + (p + r)*m := by
  rw [rainbowCount_congr _ _ (2*q*m) (fun k _ _ => propCol_at p r q m k hq hpr)]
  have e : 2*q*m = 2*(q*m) := by grind
  rw [e]
  have S := region3 (p*m) (r*m) (q*m) (Nat.mul_le_mul_right m hpr) (Nat.mul_le_mul_right m hrq)
    (by have := Nat.mul_le_mul_right m h1; grind)
    (by have := Nat.mul_le_mul_right m h2; grind)
    (by have := Nat.mul_le_mul_right m h3; grind)
  grind

/-- Leading coefficient: `c2 / (2 q²) = D(p/q, r/q)` on the stability region. -/
def c2 (p r q : Int) : Int := 4*p*r + 4*r*q - 5*p*p - 3*r*r - q*q
/-- Linear coefficient. -/
def c1 (p r q : Int) : Int := p + r - q

/-- The same count as a polynomial in `m` with integer coefficients. -/
theorem rational_count_int (p r q m : Nat) (hq : 1 ≤ q) (hpr : p ≤ r) (hrq : r ≤ q)
    (h1 : 2*p ≤ q) (h2 : q ≤ 2*r) (h3 : q ≤ p + r) :
    (rainbowCount (propCol p r q (2*q*m)) (2*q*m) : Int)
      = c2 p r q * ((m:Int)*m) + c1 p r q * m := by
  have S := rational_count p r q m hq hpr hrq h1 h2 h3
  have S' : ((rainbowCount (propCol p r q (2*q*m)) (2*q*m)
      + ((5*(p*p) + 3*(r*r) + q*q)*(m*m) + q*m) : Nat) : Int)
      = (((4*(p*r) + 4*(r*q))*(m*m) + (p + r)*m : Nat) : Int) := by rw [S]
  unfold c2 c1
  push_cast at S'
  grind

/-- Equation `eq:schur-template-stability` cleared of denominators: with `u = p/q - 4/11` and
`v = r/q - 10/11`, `c2/(2q²) = 9/22 - (5/2)u² + 2uv - (3/2)v²`. Multiply by `242 q²`. -/
theorem c2_stability (p r q : Int) :
    121 * c2 p r q = 99*(q*q) - 5*((11*p - 4*q)*(11*p - 4*q))
      + 4*((11*p - 4*q)*(11*r - 10*q)) - 3*((11*r - 10*q)*(11*r - 10*q)) := by
  unfold c2; grind

/-- The fraction, exactly: with `n = 2 q m`, `2 R · q (2qm - 1) = (c2 m + c1) · n (n - 1)`, i.e.
`R / binom(n,2) = (c2 m + c1) / (q (2 q m - 1))`. -/
theorem rational_fraction (p r q m : Nat) (hq : 1 ≤ q) (hpr : p ≤ r) (hrq : r ≤ q)
    (h1 : 2*p ≤ q) (h2 : q ≤ 2*r) (h3 : q ≤ p + r) :
    2 * (rainbowCount (propCol p r q (2*q*m)) (2*q*m) : Int) * (q * (2*q*m - 1))
      = (c2 p r q * m + c1 p r q) * ((2*q*m) * (2*q*m - 1)) := by
  rw [rational_count_int p r q m hq hpr hrq h1 h2 h3]
  grind

/-! ## Consistency with the certified witness `(p, r, q) = (4, 10, 11)` -/

/-- The witness colouring of RainbowSchur.lean (verbatim). -/
def col (m k : Nat) : Nat :=
  if k % 2 = 0 then 0 else if k ≤ 8*m then 1 else if k ≤ 20*m then 2 else 1

theorem col_eq_tcol (m k : Nat) : col m k = tcol (2*(4*m)) (2*(10*m)) k := by
  unfold col tcol
  have e1 : 2*(4*m) = 8*m := by omega
  have e2 : 2*(10*m) = 20*m := by omega
  rw [e1, e2]

/-- `witness_count` of RainbowSchur.lean is the case `A = 4m`, `B = 10m`, `N = 11m`. -/
theorem witness_count_again (m : Nat) : rainbowCount (col m) (22*m) = 99*(m*m) + 3*m := by
  rw [rainbowCount_congr _ _ (22*m) (fun k _ _ => col_eq_tcol m k)]
  have e : 22*m = 2*(11*m) := by omega
  rw [e]
  have S := region3 (4*m) (10*m) (11*m) (by omega) (by omega) (by omega) (by omega) (by omega)
  grind

theorem witness_is_propCol (m k : Nat) : propCol 4 10 11 (2*11*m) k = col m k := by
  rw [propCol_at 4 10 11 m k (by omega) (by omega), col_eq_tcol]

/-! ## Odd `n`: one more summand -/

/-- `R(c, 2N+1) = R(c, 2N) + r(2N+1)` and, for the template, `r(2N+1)` is `0`, `2A` or `2(B-A)`. -/
theorem template_count_odd (A B N : Nat) (hAB : A ≤ B) :
    rainbowCount (tcol (2*A) (2*B)) (2*N+1)
      = rainbowCount (tcol (2*A) (2*B)) (2*N) + ro A B (N+1) := by
  have e : 2*N + 1 = 2*(N+1) - 1 := by omega
  show rainbowCount (tcol (2*A) (2*B)) (2*N) + rz (tcol (2*A) (2*B)) (2*N+1) = _
  rw [e, rz_odd A B (N+1) hAB (by omega)]

/-! ## Kernel cross-checks: one instance in each region, against a differently shaped count -/

set_option maxRecDepth 100000 in
theorem check_regions :
    rainbowCount (tcol 2 4) 10 = 14 ∧ bruteCount (tcol 2 4) 10 = 14 ∧
    rainbowCount (tcol 2 6) 10 = 18 ∧ bruteCount (tcol 2 6) 10 = 18 ∧
    rainbowCount (tcol 4 8) 10 = 20 ∧ bruteCount (tcol 4 8) 10 = 20 ∧
    rainbowCount (tcol 6 8) 10 = 12 ∧ bruteCount (tcol 6 8) 10 = 12 := by
  decide +kernel

set_option maxRecDepth 100000 in
theorem check_propCol : rainbowCount (propCol 4 10 11 22) 22 = 102 ∧
    bruteCount (propCol 4 10 11 22) 22 = 102 ∧ rainbowCount (propCol 1 2 3 12) 12 = 24 := by
  decide +kernel


end SchurTemplateLink

/-! # Part 2: analysis (Mathlib) -/

/-! # Analytic link: the exact count against the proposition's objective `D(a,b)` -/

namespace SchurTemplateLink
open Filter Topology

/-- The proposition's objective, equation `eq:schur-template-objective` of the written proof, with
`x₊ = max x 0`.  The definition is the one used by the analytic certificate (SchurTemplate.lean,
`CoPEER.SchurTemplate.density`), repeated here character for character. -/
noncomputable def density (a b : ℝ) : ℝ :=
  (b - a) * (1 - b + a) + (1 / 2 : ℝ) *
    ((1 - a)^2 - (1 - b)^2 - (max (1 - 2*a) 0)^2 -
      (max (1 - 2*b) 0)^2 + 2 * (max (1 - a - b) 0)^2)

theorem cast_tsub (N U : ℕ) : ((N - U : ℕ) : ℝ) = max ((N:ℝ) - U) 0 := by
  rcases le_total U N with h | h
  · have h' : (U:ℝ) ≤ N := by exact_mod_cast h
    rw [Nat.cast_sub h, max_eq_left (by linarith)]
  · have h' : (N:ℝ) ≤ U := by exact_mod_cast h
    rw [Nat.sub_eq_zero_of_le h, max_eq_right (by linarith)]; simp

theorem max_scale (N u : ℝ) (hN : 0 < N) : max (1 - u/N) 0 = max (N - u) 0 / N := by
  have e : 1 - u/N = (N - u)/N := by field_simp
  rw [e, ← max_div_div_right hN.le, zero_div]

/-- The exact lower-order term: `R = 2 N² D(A/N, B/N) + lin A B N`. -/
noncomputable def lin (A B N : ℕ) : ℝ :=
  ((N:ℝ) - A) + 2 * max ((N:ℝ) - (A + B)) 0 - max ((N:ℝ) - 2*A) 0 - ((N:ℝ) - B)
    - max ((N:ℝ) - 2*B) 0

/-- **Exact link, all four regions at once.** For all `A ≤ B ≤ N`, `N ≥ 1`:
`R(tcol (2A) (2B), 2N) = 2 N² · D(A/N, B/N) + lin A B N`. -/
theorem count_eq_density (A B N : ℕ) (hAB : A ≤ B) (hBN : B ≤ N) (hN : 1 ≤ N) :
    (rainbowCount (tcol (2*A) (2*B)) (2*N) : ℝ)
      = 2 * (N:ℝ)^2 * density ((A:ℝ)/N) ((B:ℝ)/N) + lin A B N := by
  have S := template_count A B N hAB hBN
  have S' : ((rainbowCount (tcol (2*A) (2*B)) (2*N) + (hh (N-B) + hh (N-2*A) + hh (N-2*B)) : ℕ) : ℝ)
      = ((2*(B-A)*(N-B+A) + hh (N-A) + 2*hh (N-(A+B)) : ℕ) : ℝ) := by rw [S]
  have hA : (A:ℝ) ≤ B := by exact_mod_cast hAB
  have hB : (B:ℝ) ≤ N := by exact_mod_cast hBN
  have hNpos : (0:ℝ) < N := by exact_mod_cast hN
  unfold hh at S'
  simp only [Nat.cast_add, Nat.cast_mul, Nat.cast_ofNat, Nat.cast_one, cast_tsub] at S'
  rw [max_eq_left (by linarith : (0:ℝ) ≤ (N:ℝ) - B), max_eq_left (by linarith : (0:ℝ) ≤ (B:ℝ) - A),
    max_eq_left (by linarith : (0:ℝ) ≤ (N:ℝ) - A)] at S'
  unfold density lin
  have e1 : 1 - 2*((A:ℝ)/N) = 1 - (2*A)/N := by ring
  have e2 : 1 - 2*((B:ℝ)/N) = 1 - (2*B)/N := by ring
  have e3 : 1 - (A:ℝ)/N - (B:ℝ)/N = 1 - ((A:ℝ)+B)/N := by ring
  rw [e1, e2, e3, max_scale _ _ hNpos, max_scale _ _ hNpos, max_scale _ _ hNpos]
  generalize max ((N:ℝ) - 2*A) 0 = x1 at *
  generalize max ((N:ℝ) - 2*B) 0 = x2 at *
  generalize max ((N:ℝ) - (A+B)) 0 = x3 at *
  field_simp
  linear_combination S'

theorem lin_abs_le (A B N : ℕ) (hAB : A ≤ B) (hBN : B ≤ N) : |lin A B N| ≤ 3 * N := by
  have hA : (A:ℝ) ≤ B := by exact_mod_cast hAB
  have hB : (B:ℝ) ≤ N := by exact_mod_cast hBN
  have hA0 : (0:ℝ) ≤ A := Nat.cast_nonneg A
  have hB0 : (0:ℝ) ≤ B := Nat.cast_nonneg B
  unfold lin
  have m1 : max ((N:ℝ) - (A + B)) 0 ≤ N := max_le (by linarith) (by linarith)
  have m2 : max ((N:ℝ) - 2*A) 0 ≤ N := max_le (by linarith) (by linarith)
  have m3 : max ((N:ℝ) - 2*B) 0 ≤ N := max_le (by linarith) (by linarith)
  have n1 : 0 ≤ max ((N:ℝ) - (A + B)) 0 := le_max_right _ _
  have n2 : 0 ≤ max ((N:ℝ) - 2*A) 0 := le_max_right _ _
  have n3 : 0 ≤ max ((N:ℝ) - 2*B) 0 := le_max_right _ _
  rw [abs_le]; constructor <;> linarith

end SchurTemplateLink

/-! # Real thresholds, every `n`, and the limit -/

namespace SchurTemplateLink
open Filter Topology

/-- The colouring of Proposition `prop:schur-template-optimum` on `[n]` for REAL thresholds
`a, b`: even `k` get colour 0; odd `k` get colour 1 when `k/n ≤ a` or `k/n > b` (written
`k ≤ a n`, `b n < k`), and colour 2 otherwise. -/
noncomputable def realCol (a b : ℝ) (n k : ℕ) : ℕ :=
  if k % 2 = 0 then 0 else if (k:ℝ) ≤ a * n ∨ b * n < (k:ℝ) then 1 else 2

/-- For rational thresholds the real colouring is the cross-multiplied `propCol` of the core part. -/
theorem realCol_rat (p r q n k : ℕ) (hq : 1 ≤ q) :
    realCol ((p:ℝ)/q) ((r:ℝ)/q) n k = propCol p r q n k := by
  have hq' : (0:ℝ) < q := by exact_mod_cast hq
  have e1 : (k:ℝ) ≤ (p:ℝ)/q * n ↔ k * q ≤ p * n := by
    rw [div_mul_eq_mul_div, le_div_iff₀ hq']; exact_mod_cast Iff.rfl
  have e2 : (r:ℝ)/q * n < k ↔ r * n < k * q := by
    rw [div_mul_eq_mul_div, div_lt_iff₀ hq']; exact_mod_cast Iff.rfl
  unfold realCol propCol; simp only [e1, e2]

theorem realCol_eq_tcol (a b : ℝ) (h0 : 0 ≤ a) (hab : a ≤ b) (n k : ℕ) :
    realCol a b n k = tcol (2*((⌊a*n⌋₊ + 1)/2)) (2*((⌊b*n⌋₊ + 1)/2)) k := by
  have hn : (0:ℝ) ≤ n := Nat.cast_nonneg n
  have e1 : (k:ℝ) ≤ a*n ↔ k ≤ ⌊a*n⌋₊ := (Nat.le_floor_iff (mul_nonneg h0 hn)).symm
  have e2 : b*n < (k:ℝ) ↔ ⌊b*n⌋₊ < k := (Nat.floor_lt (mul_nonneg (h0.trans hab) hn)).symm
  have hFG : ⌊a*n⌋₊ ≤ ⌊b*n⌋₊ := Nat.floor_mono (mul_le_mul_of_nonneg_right hab hn)
  unfold realCol tcol
  simp only [e1, e2]
  generalize ⌊a*n⌋₊ = F at *
  generalize ⌊b*n⌋₊ = G at *
  split_ifs <;> omega

theorem tcol_clip (A B N k : ℕ) (hk : k ≤ 2*N) :
    tcol (2*A) (2*B) k = tcol (2*(min A N)) (2*(min B N)) k := by
  unfold tcol; split_ifs <;> omega

theorem count_even_odd (c : ℕ → ℕ) (n : ℕ) :
    rainbowCount c (2*(n/2)) ≤ rainbowCount c n ∧
      rainbowCount c n ≤ rainbowCount c (2*(n/2)) + n := by
  rcases Nat.even_or_odd' n with ⟨N, rfl | rfl⟩
  · have e : 2*N/2 = N := by omega
    rw [e]; omega
  · have e : (2*N+1)/2 = N := by omega
    rw [e]
    have h1 : rainbowCount c (2*N+1) = rainbowCount c (2*N) + rz c (2*N+1) := rfl
    have h2 := rz_le c (2*N+1)
    omega

/-- The clipped even threshold index: `min ⌈⌊a n⌋/2⌉ ⌊n/2⌋`. -/
noncomputable def thr (a : ℝ) (n : ℕ) : ℕ := min ((⌊a*n⌋₊ + 1)/2) (n/2)

theorem thr_mono (a b : ℝ) (hab : a ≤ b) (n : ℕ) : thr a n ≤ thr b n := by
  have hn : (0:ℝ) ≤ n := Nat.cast_nonneg n
  have hFG : ⌊a*n⌋₊ ≤ ⌊b*n⌋₊ := Nat.floor_mono (mul_le_mul_of_nonneg_right hab hn)
  unfold thr; omega

theorem thr_le (b : ℝ) (n : ℕ) : thr b n ≤ n/2 := by unfold thr; omega

/-- The count on `[n]` differs from the template count on `[2⌊n/2⌋]` by at most `n`. -/
theorem count_bounds (a b : ℝ) (h0 : 0 ≤ a) (hab : a ≤ b) (n : ℕ) :
    rainbowCount (tcol (2*thr a n) (2*thr b n)) (2*(n/2)) ≤ rainbowCount (realCol a b n) n ∧
    rainbowCount (realCol a b n) n ≤ rainbowCount (tcol (2*thr a n) (2*thr b n)) (2*(n/2)) + n := by
  have h := count_even_odd (realCol a b n) n
  have e : rainbowCount (realCol a b n) (2*(n/2))
      = rainbowCount (tcol (2*thr a n) (2*thr b n)) (2*(n/2)) := by
    apply rainbowCount_congr
    intro k _ hk
    rw [realCol_eq_tcol a b h0 hab n k]
    exact tcol_clip _ _ (n/2) k hk
  rw [e] at h; exact h

theorem thr_close (a : ℝ) (h0 : 0 ≤ a) (h1 : a ≤ 1) (n : ℕ) :
    |(thr a n : ℝ) - a * ((n/2 : ℕ) : ℝ)| ≤ 1 := by
  unfold thr
  have hn : (0:ℝ) ≤ n := Nat.cast_nonneg n
  have hF1 : (⌊a*n⌋₊ : ℝ) ≤ a*n := Nat.floor_le (mul_nonneg h0 hn)
  have hF2 : a*n < (⌊a*n⌋₊ : ℝ) + 1 := Nat.lt_floor_add_one _
  generalize ⌊a*n⌋₊ = F at *
  have q1 : ((((F+1)/2 : ℕ)) : ℝ) * 2 ≤ F + 1 := by
    have : ((F+1)/2)*2 ≤ F + 1 := by omega
    exact_mod_cast this
  have q2 : (F:ℝ) ≤ ((((F+1)/2 : ℕ)) : ℝ) * 2 := by
    have : F ≤ ((F+1)/2)*2 := by omega
    exact_mod_cast this
  have n1 : (((n/2 : ℕ)) : ℝ) * 2 ≤ n := by
    have : (n/2)*2 ≤ n := by omega
    exact_mod_cast this
  have n2 : (n:ℝ) ≤ (((n/2 : ℕ)) : ℝ) * 2 + 1 := by
    have : n ≤ (n/2)*2 + 1 := by omega
    exact_mod_cast this
  have hN0 : (0:ℝ) ≤ ((n/2 : ℕ) : ℝ) := Nat.cast_nonneg _
  have p1 : a * ((((n/2 : ℕ)) : ℝ) * 2) ≤ a * n := mul_le_mul_of_nonneg_left n1 h0
  have p2 : a * n ≤ a * ((((n/2 : ℕ)) : ℝ) * 2 + 1) := mul_le_mul_of_nonneg_left n2 h0
  have p3 : a * ((n/2 : ℕ) : ℝ) ≤ ((n/2 : ℕ) : ℝ) := by nlinarith
  rcases le_total ((F+1)/2) (n/2) with h | h
  · rw [min_eq_left h, abs_le]; constructor <;> nlinarith
  · have h' : (((n/2 : ℕ)) : ℝ) ≤ ((((F+1)/2 : ℕ)) : ℝ) := by exact_mod_cast h
    rw [min_eq_right h, abs_le]; constructor <;> nlinarith

theorem tendsto_of_abs_le (u : ℕ → ℝ) (L K : ℝ) (h : ∀ n : ℕ, 2 ≤ n → |u n - L| ≤ K / n) :
    Tendsto u atTop (𝓝 L) := by
  rw [tendsto_iff_dist_tendsto_zero]
  refine squeeze_zero' (Eventually.of_forall fun n => dist_nonneg) ?_
    (tendsto_const_div_atTop_nhds_zero_nat K)
  filter_upwards [eventually_ge_atTop 2] with n hn
  rw [Real.dist_eq]; exact h n hn

theorem half_facts (n : ℕ) (hn : 2 ≤ n) :
    (1:ℝ) ≤ ((n/2 : ℕ) : ℝ) ∧ (((n/2 : ℕ)) : ℝ) * 2 ≤ n ∧ (n:ℝ) ≤ (((n/2 : ℕ)) : ℝ) * 2 + 1 := by
  refine ⟨?_, ?_, ?_⟩
  · have : 1 ≤ n/2 := by omega
    exact_mod_cast this
  · have : (n/2)*2 ≤ n := by omega
    exact_mod_cast this
  · have : n ≤ (n/2)*2 + 1 := by omega
    exact_mod_cast this

theorem thr_ratio_tendsto (a : ℝ) (h0 : 0 ≤ a) (h1 : a ≤ 1) :
    Tendsto (fun n : ℕ => (thr a n : ℝ) / ((n/2 : ℕ) : ℝ)) atTop (𝓝 a) := by
  apply tendsto_of_abs_le _ _ 4
  intro n hn
  obtain ⟨hN1, hN2, hN3⟩ := half_facts n hn
  have hNpos : (0:ℝ) < ((n/2 : ℕ) : ℝ) := by linarith
  have hnpos : (0:ℝ) < n := by linarith
  have hc := thr_close a h0 h1 n
  have e : (thr a n : ℝ) / ((n/2 : ℕ) : ℝ) - a
      = ((thr a n : ℝ) - a * ((n/2 : ℕ) : ℝ)) / ((n/2 : ℕ) : ℝ) := by field_simp
  rw [e, abs_div, abs_of_pos hNpos, div_le_div_iff₀ hNpos hnpos]
  nlinarith [abs_nonneg ((thr a n : ℝ) - a * ((n/2 : ℕ) : ℝ))]

end SchurTemplateLink

namespace SchurTemplateLink
open Filter Topology

theorem choose_two_facts (n : ℕ) (hn : 2 ≤ n) :
    ((n.choose 2 : ℕ) : ℝ) = (n:ℝ) * ((n:ℝ) - 1) / 2 ∧ (0:ℝ) < ((n.choose 2 : ℕ) : ℝ) := by
  have h2 : (2:ℝ) ≤ n := by exact_mod_cast hn
  have e := Nat.cast_choose_two ℝ n
  refine ⟨e, ?_⟩
  rw [e]; nlinarith

/-- `2 ⌊n/2⌋² / binom(n,2) → 1`. -/
theorem ratio_tendsto :
    Tendsto (fun n : ℕ => 2 * (((n/2 : ℕ)) : ℝ)^2 / ((n.choose 2 : ℕ) : ℝ)) atTop (𝓝 1) := by
  apply tendsto_of_abs_le _ _ 4
  intro n hn
  obtain ⟨hN1, hN2, hN3⟩ := half_facts n hn
  obtain ⟨hC, hCpos⟩ := choose_two_facts n hn
  have h2 : (2:ℝ) ≤ n := by exact_mod_cast hn
  have hnpos : (0:ℝ) < n := by linarith
  have e : 2 * (((n/2 : ℕ)) : ℝ)^2 / ((n.choose 2 : ℕ) : ℝ) - 1
      = (2 * (((n/2 : ℕ)) : ℝ)^2 - ((n.choose 2 : ℕ) : ℝ)) / ((n.choose 2 : ℕ) : ℝ) := by
    field_simp
  rw [e, abs_div, abs_of_pos hCpos, div_le_div_iff₀ hCpos hnpos, hC]
  generalize (((n/2 : ℕ)) : ℝ) = N at *
  have hd : 0 ≤ (n:ℝ) - N*2 := by linarith
  have hd1 : (n:ℝ) - N*2 ≤ 1 := by linarith
  have key : |2 * N^2 - (n:ℝ) * ((n:ℝ) - 1) / 2| ≤ (n:ℝ) := by
    rw [abs_le]; constructor <;> nlinarith
  have h3 : |2 * N^2 - (n:ℝ) * ((n:ℝ) - 1) / 2| * (n:ℝ) ≤ (n:ℝ) * n :=
    mul_le_mul_of_nonneg_right key hnpos.le
  have h4 : (n:ℝ) * n ≤ 4 * ((n:ℝ) * ((n:ℝ) - 1) / 2) := by nlinarith
  linarith

theorem density_continuous : Continuous (fun p : ℝ × ℝ => density p.1 p.2) := by
  unfold density; fun_prop

/-- **The limiting fraction exists and equals `D(a,b)`**, for all real `0 ≤ a ≤ b ≤ 1`, along ALL `n`:
`R(realCol a b n, n) / binom(n,2) → density a b`. -/
theorem template_limit (a b : ℝ) (h0 : 0 ≤ a) (hab : a ≤ b) (hb1 : b ≤ 1) :
    Tendsto (fun n : ℕ => (rainbowCount (realCol a b n) n : ℝ) / ((n.choose 2 : ℕ) : ℝ))
      atTop (𝓝 (density a b)) := by
  have hx := thr_ratio_tendsto a h0 (hab.trans hb1)
  have hy := thr_ratio_tendsto b (h0.trans hab) hb1
  have hd : Tendsto (fun n : ℕ => density ((thr a n : ℝ) / ((n/2 : ℕ) : ℝ))
      ((thr b n : ℝ) / ((n/2 : ℕ) : ℝ))) atTop (𝓝 (density a b)) :=
    (density_continuous.tendsto (a, b)).comp (hx.prodMk_nhds hy)
  -- the error term
  have he : Tendsto (fun n : ℕ => ((rainbowCount (realCol a b n) n : ℝ)
      - 2 * (((n/2 : ℕ)) : ℝ)^2 * density ((thr a n : ℝ) / ((n/2 : ℕ) : ℝ))
          ((thr b n : ℝ) / ((n/2 : ℕ) : ℝ))) / ((n.choose 2 : ℕ) : ℝ)) atTop (𝓝 0) := by
    apply tendsto_of_abs_le _ _ 10
    intro n hn
    obtain ⟨hN1, hN2, hN3⟩ := half_facts n hn
    obtain ⟨hC, hCpos⟩ := choose_two_facts n hn
    have h2 : (2:ℝ) ≤ n := by exact_mod_cast hn
    have hnpos : (0:ℝ) < n := by linarith
    have hAB := thr_mono a b hab n
    have hBN := thr_le b n
    have hcount := count_eq_density (thr a n) (thr b n) (n/2) hAB hBN (by omega)
    have hlin := lin_abs_le (thr a n) (thr b n) (n/2) hAB hBN
    obtain ⟨hlo, hhi⟩ := count_bounds a b h0 hab n
    have hlo' : (rainbowCount (tcol (2*thr a n) (2*thr b n)) (2*(n/2)) : ℝ)
        ≤ (rainbowCount (realCol a b n) n : ℝ) := by exact_mod_cast hlo
    have hhi' : (rainbowCount (realCol a b n) n : ℝ)
        ≤ (rainbowCount (tcol (2*thr a n) (2*thr b n)) (2*(n/2)) : ℝ) + n := by exact_mod_cast hhi
    rw [sub_zero, abs_div, abs_of_pos hCpos, div_le_div_iff₀ hCpos hnpos, hC]
    rw [hcount] at hlo' hhi'
    rw [abs_le] at hlin
    have key : |(rainbowCount (realCol a b n) n : ℝ)
        - 2 * (((n/2 : ℕ)) : ℝ)^2 * density ((thr a n : ℝ) / ((n/2 : ℕ) : ℝ))
            ((thr b n : ℝ) / ((n/2 : ℕ) : ℝ))| ≤ 5 * (n:ℝ) / 2 := by
      rw [abs_le]; constructor <;> linarith
    nlinarith [abs_nonneg ((rainbowCount (realCol a b n) n : ℝ)
        - 2 * (((n/2 : ℕ)) : ℝ)^2 * density ((thr a n : ℝ) / ((n/2 : ℕ) : ℝ))
            ((thr b n : ℝ) / ((n/2 : ℕ) : ℝ)))]
  have hsum := (ratio_tendsto.mul hd).add he
  rw [one_mul, add_zero] at hsum
  refine hsum.congr' ?_
  filter_upwards [eventually_ge_atTop 2] with n hn
  obtain ⟨_, hCpos⟩ := choose_two_facts n hn
  field_simp
  ring

/-- The same for rational thresholds in the cross-multiplied form of the core part. -/
theorem template_limit_rat (p r q : ℕ) (hq : 1 ≤ q) (hpr : p ≤ r) (hrq : r ≤ q) :
    Tendsto (fun n : ℕ => (rainbowCount (propCol p r q n) n : ℝ) / ((n.choose 2 : ℕ) : ℝ))
      atTop (𝓝 (density ((p:ℝ)/q) ((r:ℝ)/q))) := by
  have hq' : (0:ℝ) < q := by exact_mod_cast hq
  have hp' : (p:ℝ) ≤ r := by exact_mod_cast hpr
  have hr' : (r:ℝ) ≤ q := by exact_mod_cast hrq
  have h := template_limit ((p:ℝ)/q) ((r:ℝ)/q) (by positivity)
    (div_le_div_of_nonneg_right hp' hq'.le) ((div_le_one hq').mpr hr')
  refine h.congr ?_
  intro n
  rw [rainbowCount_congr _ _ n (fun k _ _ => realCol_rat p r q n k hq)]

end SchurTemplateLink

/-! # The proposition's colouring, literally, and the exact fraction along `n = 2 q m` -/

namespace SchurTemplateLink
open Filter Topology

/-- The colouring of Proposition `prop:schur-template-optimum`, literally: every even integer gets
colour 1; an odd integer `k` gets colour 2 when `k/n ≤ a` or `k/n > b`, and colour 3 otherwise. -/
noncomputable def paperCol (a b : ℝ) (n k : ℕ) : ℕ :=
  if k % 2 = 0 then 1 else if (k:ℝ)/n ≤ a ∨ b < (k:ℝ)/n then 2 else 3

theorem paperCol_eq (a b : ℝ) (n k : ℕ) (hn : 1 ≤ n) :
    paperCol a b n k = realCol a b n k + 1 := by
  have hn' : (0:ℝ) < n := by exact_mod_cast hn
  have e1 : (k:ℝ)/n ≤ a ↔ (k:ℝ) ≤ a*n := div_le_iff₀ hn'
  have e2 : b < (k:ℝ)/n ↔ b*n < (k:ℝ) := lt_div_iff₀ hn'
  unfold paperCol realCol
  simp only [e1, e2]
  split_ifs <;> rfl

theorem paper_count (a b : ℝ) (n : ℕ) (hn : 1 ≤ n) :
    rainbowCount (paperCol a b n) n = rainbowCount (realCol a b n) n := by
  rw [rainbowCount_congr _ (fun k => realCol a b n k + 1) n (fun k _ _ => paperCol_eq a b n k hn)]
  exact rainbowCount_rename (fun i => i + 1) (fun i j h => Nat.add_right_cancel h) _ n

/-- **Headline.** For all real `0 ≤ a ≤ b ≤ 1`, the fraction of rainbow ordered Schur triples of the
proposition's colouring of `[n]`, normalised by `binom(n,2)`, converges to `D(a,b)` as `n → ∞`
(along all `n`, not a subsequence). -/
theorem paper_limit (a b : ℝ) (h0 : 0 ≤ a) (hab : a ≤ b) (hb1 : b ≤ 1) :
    Tendsto (fun n : ℕ => (rainbowCount (paperCol a b n) n : ℝ) / ((n.choose 2 : ℕ) : ℝ))
      atTop (𝓝 (density a b)) := by
  refine (template_limit a b h0 hab hb1).congr' ?_
  filter_upwards [eventually_ge_atTop 1] with n hn
  rw [paper_count a b n hn]

/-- The normaliser is a cardinality: the list of all ordered Schur pairs of `[n]` has `binom(n,2)`
members. -/
theorem schurPairs_length_choose (n : ℕ) : (schurPairs n).length = n.choose 2 := by
  have h := schurPairs_length n
  rw [Nat.choose_two_right]
  omega

/-- **Headline, as a ratio of cardinalities.** The proportion of ordered Schur pairs `(x, y)` of `[n]`
(`1 ≤ x`, `1 ≤ y`, `x + y ≤ n`) for which `x`, `y`, `x + y` receive three different colours under the
proposition's colouring tends to `D(a,b)`. -/
theorem paper_limit_card (a b : ℝ) (h0 : 0 ≤ a) (hab : a ≤ b) (hb1 : b ≤ 1) :
    Tendsto (fun n : ℕ =>
        ((((schurPairs n).filter (isRainbowPair (paperCol a b n))).length : ℕ) : ℝ)
          / (((schurPairs n).length : ℕ) : ℝ))
      atTop (𝓝 (density a b)) := by
  refine (paper_limit a b h0 hab hb1).congr ?_
  intro n
  rw [rainbowCount_eq_length, schurPairs_length_choose]


/-- The exact fraction on the stability region at `n = 2 q m`:
`R / binom(n,2) = D(p/q, r/q) + (2 q c1 + c2) / (2 q² (2 q m - 1))`. -/
theorem rational_fraction_real (p r q m : ℕ) (hq : 1 ≤ q) (hpr : p ≤ r) (hrq : r ≤ q)
    (h1 : 2*p ≤ q) (h2 : q ≤ 2*r) (h3 : q ≤ p + r) (hm : 1 ≤ m) :
    (rainbowCount (propCol p r q (2*q*m)) (2*q*m) : ℝ) / (((2*q*m).choose 2 : ℕ) : ℝ)
      = density ((p:ℝ)/q) ((r:ℝ)/q)
        + (2*(q:ℝ)*((p:ℝ) + r - q) + (4*(p:ℝ)*r + 4*r*q - 5*p*p - 3*r*r - q*q))
            / (2*(q:ℝ)^2*(2*q*m - 1)) := by
  have S := rational_count p r q m hq hpr hrq h1 h2 h3
  have S' : ((rainbowCount (propCol p r q (2*q*m)) (2*q*m)
      + ((5*(p*p) + 3*(r*r) + q*q)*(m*m) + q*m) : ℕ) : ℝ)
      = (((4*(p*r) + 4*(r*q))*(m*m) + (p + r)*m : ℕ) : ℝ) := by rw [S]
  push_cast at S'
  have hq' : (0:ℝ) < q := by exact_mod_cast hq
  have hm' : (1:ℝ) ≤ m := by exact_mod_cast hm
  have hq1 : (1:ℝ) ≤ q := by exact_mod_cast hq
  have g1 : (2:ℝ)*p ≤ q := by exact_mod_cast h1
  have g2 : (q:ℝ) ≤ 2*r := by exact_mod_cast h2
  have g3 : (q:ℝ) ≤ p + r := by exact_mod_cast h3
  have hden : (2*(q:ℝ)*m - 1) ≠ 0 := by nlinarith
  have d1 : (0:ℝ) ≤ 1 - 2*((p:ℝ)/q) := by
    rw [sub_nonneg, ← mul_div_assoc, div_le_one hq']; exact g1
  have d2 : 1 - 2*((r:ℝ)/q) ≤ 0 := by
    rw [sub_nonpos, ← mul_div_assoc, one_le_div hq']; exact g2
  have d3 : 1 - (p:ℝ)/q - (r:ℝ)/q ≤ 0 := by
    have : (1:ℝ) ≤ ((p:ℝ) + r)/q := by rw [one_le_div hq']; exact g3
    have e : ((p:ℝ) + r)/q = (p:ℝ)/q + (r:ℝ)/q := by ring
    linarith
  have hdens : density ((p:ℝ)/q) ((r:ℝ)/q)
      = (4*(p:ℝ)*r + 4*r*q - 5*p*p - 3*r*r - q*q) / (2*(q:ℝ)^2) := by
    unfold density
    rw [max_eq_left d1, max_eq_right d2, max_eq_right d3]
    field_simp
    ring
  have hc : (rainbowCount (propCol p r q (2*q*m)) (2*q*m) : ℝ)
      = (4*(p:ℝ)*r + 4*r*q - 5*p*p - 3*r*r - q*q)*((m:ℝ)*m) + ((p:ℝ) + r - q)*m := by linarith
  have hq2 : (2*(q:ℝ)^2) ≠ 0 := by positivity
  have hq2d : (2*(q:ℝ)^2*(2*q*m - 1)) ≠ 0 := mul_ne_zero hq2 hden
  have hC : (2*(q:ℝ)*m * (2*q*m - 1) / 2) ≠ 0 := by
    have : (2*(q:ℝ)*m) ≠ 0 := by positivity
    exact div_ne_zero (mul_ne_zero this hden) (by norm_num)
  rw [hdens, hc, Nat.cast_choose_two]
  push_cast
  rw [div_add_div _ _ hq2 hq2d, div_eq_div_iff hC (mul_ne_zero hq2 hq2d)]
  ring

end SchurTemplateLink

namespace SchurTemplateLink
#print axioms template_count
#print axioms region3
#print axioms rational_count
#print axioms rational_count_int
#print axioms c2_stability
#print axioms propCol_eq_tcol
#print axioms rainbowCount_eq_length
#print axioms schurPairs_length
#print axioms rainbowCount_rename
#print axioms count_eq_density
#print axioms lin_abs_le
#print axioms realCol_rat
#print axioms realCol_eq_tcol
#print axioms count_bounds
#print axioms thr_ratio_tendsto
#print axioms ratio_tendsto
#print axioms density_continuous
#print axioms template_limit
#print axioms template_limit_rat
#print axioms paperCol_eq
#print axioms paper_count
#print axioms paper_limit
#print axioms schurPairs_length_choose
#print axioms paper_limit_card
#print axioms rational_fraction_real
end SchurTemplateLink

/-! # Part C: composition -/

namespace SchurTemplateComposed
open Filter Topology

/-- The two certificates optimise and count the same function. -/
theorem density_same : SchurTemplateLink.density = CoPEER.SchurTemplate.density := rfl

/-- The proposition's normalised count: rainbow ordered Schur triples of the colouring of `[n]`
with thresholds `a, b`, divided by `binom(n,2)`. -/
noncomputable def fraction (a b : ℝ) (n : ℕ) : ℝ :=
  (SchurTemplateLink.rainbowCount (SchurTemplateLink.paperCol a b n) n : ℝ) / ((n.choose 2 : ℕ) : ℝ)

/-- `D` is "the limiting rainbow ordered-Schur-triple fraction" on the parameter triangle. -/
def IsLimitingFraction (D : ℝ → ℝ → ℝ) : Prop :=
  ∀ a b : ℝ, 0 ≤ a → a ≤ b → b ≤ 1 → Tendsto (fraction a b) atTop (𝓝 (D a b))

/-- The limit exists for every admissible pair, and it is the written proof's objective. -/
theorem limiting_fraction_exists : IsLimitingFraction CoPEER.SchurTemplate.density :=
  fun a b h0 hab hb1 => SchurTemplateLink.paper_limit a b h0 hab hb1

/-- Limits are unique: any limiting fraction agrees with the objective on the triangle. -/
theorem limiting_fraction_unique (D : ℝ → ℝ → ℝ) (hD : IsLimitingFraction D)
    (a b : ℝ) (h0 : 0 ≤ a) (hab : a ≤ b) (hb1 : b ≤ 1) :
    D a b = CoPEER.SchurTemplate.density a b :=
  tendsto_nhds_unique (hD a b h0 hab hb1) (SchurTemplateLink.paper_limit a b h0 hab hb1)

/-- **Proposition `prop:schur-template-optimum`, every clause**, for the limiting fraction `D`:
(1) unique maximum `9/22` at `(4/11, 10/11)` over `0 ≤ a ≤ b ≤ 1`;
(2) on `a ≤ 1/2 ≤ b`, `a + b ≥ 1`: `D = 9/22 − (5/2)u² + 2uv − (3/2)v²`, `u = a − 4/11`, `v = b − 10/11`;
(3) the subfamilies `a = 0` and `b = 1` have maximum `2/5` (attained at the other threshold `2/5`). -/
theorem prop_schur_template_optimum (D : ℝ → ℝ → ℝ) (hD : IsLimitingFraction D) :
    (D (4/11) (10/11) = 9/22 ∧
      ∀ a b : ℝ, 0 ≤ a → a ≤ b → b ≤ 1 →
        D a b ≤ 9/22 ∧ (D a b = 9/22 ↔ a = 4/11 ∧ b = 10/11)) ∧
    (∀ a b : ℝ, 0 ≤ a → a ≤ b → b ≤ 1 → a ≤ 1/2 → 1/2 ≤ b → 1 ≤ a + b →
        D a b = 9/22 - (5/2)*(a - 4/11)^2 + 2*(a - 4/11)*(b - 10/11) - (3/2)*(b - 10/11)^2) ∧
    ((∀ b : ℝ, 0 ≤ b → b ≤ 1 → D 0 b ≤ 2/5 ∧ (D 0 b = 2/5 ↔ b = 2/5)) ∧
      (∀ a : ℝ, 0 ≤ a → a ≤ 1 → D a 1 ≤ 2/5 ∧ (D a 1 = 2/5 ↔ a = 2/5))) := by
  obtain ⟨_, hopt, hglob⟩ := CoPEER.SchurTemplate.unique_global_optimum
  refine ⟨⟨?_, ?_⟩, ?_, ?_, ?_⟩
  · rw [limiting_fraction_unique D hD (4/11) (10/11) (by norm_num) (by norm_num) (by norm_num)]
    exact hopt
  · intro a b h0 hab hb1
    rw [limiting_fraction_unique D hD a b h0 hab hb1]
    exact hglob a b ⟨h0, hab, hb1⟩
  · intro a b h0 hab hb1 ha hb hsum
    rw [limiting_fraction_unique D hD a b h0 hab hb1]
    have h := CoPEER.SchurTemplate.stability_identity a b ha hb hsum
    linarith
  · intro b hb0 hb1
    rw [limiting_fraction_unique D hD 0 b (le_refl 0) hb0 hb1]
    exact CoPEER.SchurTemplate.left_boundary_optimum b hb0 hb1
  · intro a ha0 ha1
    rw [limiting_fraction_unique D hD a 1 ha0 ha1 (le_refl 1)]
    exact CoPEER.SchurTemplate.right_boundary_optimum a ha0 ha1

#print axioms density_same
#print axioms limiting_fraction_exists
#print axioms limiting_fraction_unique
#print axioms prop_schur_template_optimum

end SchurTemplateComposed
