/-!
# Kernel certificate: the q-rious unimodality conjecture fails at a = (2,3,5,12), b = (1,1,1,4,6,9) (2026-09-19)

NEW dated artifact, outside the frozen 285-record release. Core Lean only; no Mathlib, no `sorry`,
no `native_decide`.

Target: Conjecture 5 of S. Ole Warnaar and Wadim Zudilin, "q-rious unimodality",
arXiv:2502.03993v2. With [n] = (1 - q^n)/(1 - q), [n]! = [1][2]...[n], tuples of positive integers
a = (a_1..a_r), b = (b_1..b_s) satisfying Landau's criterion

  (1)  sum_i floor(a_i x) - sum_j floor(b_j x) >= 0  for all x >= 0,

and D(a,b;q) = [a_1]!...[a_r]! / ([b_1]!...[b_s]!), the conjecture says (1+q) D(a,b;q) is unimodal.

Witness: a = (2,3,5,12), b = (1,1,1,4,6,9). D = [10][11](1 - q^2 + q^4) and (1+q)D has the valley
c_10 = 16 > c_11 = 15 > c_12 = 14 < c_13 = 15 < c_14 = 16.

Core Lean has no real numbers. Landau's criterion is certified for every FLOOR PROFILE, a function
fl : Nat -> Int with  fl n * m < (fl m + 1) * n  for all positive n, m.  For every real x the function
n |-> floor(n x) is a floor profile, because m floor(n x) <= m n x < n (floor(m x) + 1); this is also
proved here inside any ordered structure with a floor (`FloorModel`), and for every rational
x = p/n >= 0 with floor computed by natural-number division (`ratProfile`, `landau_rational`).
That the real numbers form such a structure is standard and is NOT kernel-checked (no real-number
type exists in core Lean); this is the one step of the refutation that stays in prose.

Contents: `coeff_mulP` (the list product is the convolution product), `quotient_unique`,
`coeff_qint` and `one_sub_q_mul_qint` ((1-q)[n] = 1 - q^n for all n >= 1), `division` (the exact
division in Z[q]), `D_is_the_quotient`, `factorisation`, `landau_profile` (criterion (1)),
`profile_on_grid` / `landau_cells` (the Landau function on its 22 breakpoint cells),
`C_not_unimodal`, `C_not_symUnimodal`, and the headlines `refutes_conjecture5`,
`not_conjecture5`, `not_conjecture5Sym`.
-/
namespace QriousUnimodality

/-! ### Z[q] as ascending coefficient lists -/
abbrev Poly := List Int

/-- Coefficient of q^k (zero beyond the end of the list). -/
def coeff : Poly → Nat → Int
  | [], _ => 0
  | x :: _, 0 => x
  | _ :: p, k + 1 => coeff p k

def addP : Poly → Poly → Poly
  | [], q => q
  | x :: p, [] => x :: p
  | x :: p, y :: q => (x + y) :: addP p q

/-- Product: (x + q p') * r = x r + q (p' r). -/
def mulP : Poly → Poly → Poly
  | [], _ => []
  | x :: p, r => addP (r.map (x * ·)) (0 :: mulP p r)

/-- sum_{i < n} f i -/
def sumTo (f : Nat → Int) : Nat → Int
  | 0 => 0
  | n + 1 => sumTo f n + f n

/-! #### `mulP` is the convolution product, for all polynomials -/
theorem coeff_addP : ∀ (p r : Poly) (k : Nat), coeff (addP p r) k = coeff p k + coeff r k
  | [], r, k => by simp [addP, coeff]
  | x :: p, [], k => by simp [addP, coeff]
  | x :: p, y :: r, 0 => by simp [addP, coeff]
  | x :: p, y :: r, k + 1 => by simp [addP, coeff, coeff_addP p r k]

theorem coeff_map (x : Int) : ∀ (r : Poly) (k : Nat), coeff (r.map (x * ·)) k = x * coeff r k
  | [], k => by simp [coeff]
  | y :: r, 0 => by simp [coeff]
  | y :: r, k + 1 => by simp [coeff, coeff_map x r k]

theorem coeff_mulP_cons_zero (x : Int) (p r : Poly) :
    coeff (mulP (x :: p) r) 0 = x * coeff r 0 := by
  show coeff (addP (r.map (x * ·)) (0 :: mulP p r)) 0 = _
  rw [coeff_addP, coeff_map]; simp [coeff]

theorem coeff_mulP_cons_succ (x : Int) (p r : Poly) (k : Nat) :
    coeff (mulP (x :: p) r) (k + 1) = x * coeff r (k + 1) + coeff (mulP p r) k := by
  show coeff (addP (r.map (x * ·)) (0 :: mulP p r)) (k + 1) = _
  rw [coeff_addP, coeff_map]; simp [coeff]

theorem sumTo_zero (f : Nat → Int) (hf : ∀ i, f i = 0) : ∀ n, sumTo f n = 0
  | 0 => rfl
  | n + 1 => by simp [sumTo, sumTo_zero f hf n, hf n]

theorem sumTo_shift (f : Nat → Int) : ∀ n, sumTo f (n + 1) = f 0 + sumTo (fun i => f (i + 1)) n
  | 0 => by simp [sumTo]
  | n + 1 => by
      have ih := sumTo_shift f n
      show sumTo f (n + 1) + f (n + 1) = f 0 + (sumTo (fun i => f (i + 1)) n + f (n + 1))
      omega

/-- The coefficient of q^k in `mulP p r` is sum_{i=0}^{k} p_i r_{k-i}. -/
theorem coeff_mulP : ∀ (p r : Poly) (k : Nat),
    coeff (mulP p r) k = sumTo (fun i => coeff p i * coeff r (k - i)) (k + 1)
  | [], r, k => by
      rw [sumTo_zero]
      · simp [mulP, coeff]
      · intro i; simp [coeff]
  | x :: p, r, 0 => by rw [coeff_mulP_cons_zero]; simp [sumTo, coeff]
  | x :: p, r, k + 1 => by
      rw [coeff_mulP_cons_succ, sumTo_shift, coeff_mulP p r k]
      simp [coeff]

/-! #### A quotient by a polynomial with constant term 1 is unique -/
theorem coeff_mulP_congr : ∀ (p X Y : Poly) (k : Nat),
    (∀ j, j ≤ k → coeff X j = coeff Y j) → coeff (mulP p X) k = coeff (mulP p Y) k
  | [], _, _, _, _ => rfl
  | x :: p, X, Y, 0, h => by
      rw [coeff_mulP_cons_zero, coeff_mulP_cons_zero, h 0 (Nat.le_refl 0)]
  | x :: p, X, Y, k + 1, h => by
      rw [coeff_mulP_cons_succ, coeff_mulP_cons_succ, h (k + 1) (Nat.le_refl _),
        coeff_mulP_congr p X Y k (fun j hj => h j (Nat.le_succ_of_le hj))]

theorem quotient_unique_aux (p X Y : Poly)
    (h : ∀ k, coeff (mulP (1 :: p) X) k = coeff (mulP (1 :: p) Y) k) :
    ∀ k j, j ≤ k → coeff X j = coeff Y j
  | 0, j, hj => by
      have h0 := h 0
      rw [coeff_mulP_cons_zero, coeff_mulP_cons_zero] at h0
      have : j = 0 := by omega
      subst this; omega
  | k + 1, j, hj => by
      have ih := quotient_unique_aux p X Y h k
      by_cases hjk : j ≤ k
      · exact ih j hjk
      · have hj' : j = k + 1 := by omega
        subst hj'
        have hk := h (k + 1)
        rw [coeff_mulP_cons_succ, coeff_mulP_cons_succ, coeff_mulP_congr p X Y k ih] at hk
        omega

/-- If den has constant term 1 and den * X = den * Y then X and Y have the same coefficients. -/
theorem quotient_unique (den X Y : Poly) (h1 : coeff den 0 = 1)
    (h : mulP den X = mulP den Y) : ∀ k, coeff X k = coeff Y k := by
  intro k
  cases den with
  | nil => simp [coeff] at h1
  | cons d p =>
      have hd : d = 1 := h1
      subst hd
      exact quotient_unique_aux p X Y (fun k => by rw [h]) k k (Nat.le_refl k)

/-! ### q-integers and q-factorials -/
/-- [n] = 1 + q + ... + q^(n-1). -/
def qint (n : Nat) : Poly := List.replicate n 1

/-- [n]! = [1][2]...[n], with [0]! = 1. -/
def qfact : Nat → Poly
  | 0 => [1]
  | n + 1 => mulP (qfact n) (qint (n + 1))

/-- [l_1]! [l_2]! ... (empty product 1). -/
def qfactProd : List Nat → Poly
  | [] => [1]
  | n :: l => mulP (qfact n) (qfactProd l)

/-- Every coefficient of [n] : 1 below n, 0 from n on. -/
theorem coeff_qint : ∀ (n k : Nat), coeff (qint n) k = if k < n then 1 else 0
  | 0, k => by simp [qint, coeff]
  | n + 1, 0 => by simp [qint, List.replicate, coeff]
  | n + 1, k + 1 => by
      have ih := coeff_qint n k
      simp only [qint, List.replicate, coeff] at ih ⊢
      rw [ih]; simp

theorem coeff_mulP_single (x : Int) (r : Poly) : ∀ k, coeff (mulP [x] r) k = x * coeff r k
  | 0 => coeff_mulP_cons_zero x [] r
  | k + 1 => by rw [coeff_mulP_cons_succ]; simp [mulP, coeff]

/-- The source writes [n] = (1 - q^n)/(1 - q). For every n >= 1: (1 - q)[n] = 1 - q^n,
coefficient by coefficient. -/
theorem one_sub_q_mul_qint (n : Nat) (hn : 0 < n) : ∀ k,
    coeff (mulP [1, -1] (qint n)) k = if k = 0 then 1 else if k = n then -1 else 0
  | 0 => by rw [coeff_mulP_cons_zero, coeff_qint]; simp [hn]
  | k + 1 => by
      rw [coeff_mulP_cons_succ, coeff_mulP_single, coeff_qint, coeff_qint]
      by_cases h1 : k + 1 < n
      · have h2 : k < n := by omega
        have h3 : ¬ (k + 1 = n) := by omega
        simp [h1, h2, h3]
      · by_cases h2 : k < n
        · have h3 : k + 1 = n := by omega
          subst h3
          simp
        · have h3 : ¬ (k + 1 = n) := by omega
          simp [h1, h2, h3]

/-- The same as a list identity for every q-integer that occurs in the witness (n = 1..12). -/
theorem qint_source_form : ∀ n : Nat, n < 12 →
    mulP [1, -1] (qint (n + 1)) = (1 :: List.replicate n 0) ++ [-1] := by decide +kernel

/-! ### The witness -/
def a : List Nat := [2, 3, 5, 12]
def b : List Nat := [1, 1, 1, 4, 6, 9]

/-- The quotient D(a,b;q), degree 23. -/
def D : Poly := [1, 2, 2, 2, 3, 4, 5, 6, 7, 8, 8, 7, 7, 8, 8, 7, 6, 5, 4, 3, 2, 2, 2, 1]

/-- (1+q) D(a,b;q), degree 24. -/
def C : Poly :=
  [1, 3, 4, 4, 5, 7, 9, 11, 13, 15, 16, 15, 14, 15, 16, 15, 13, 11, 9, 7, 5, 4, 4, 3, 1]

/-- THE DIVISION: [1]!^3 [4]! [6]! [9]! * D = [2]! [3]! [5]! [12]!  in Z[q] (degrees 57 + 23 = 80). -/
theorem division : mulP (qfactProd b) D = qfactProd a := by decide +kernel

theorem denominator_constant_term : coeff (qfactProd b) 0 = 1 := by decide +kernel

/-- D is the only quotient: any X with [b]! * X = [a]! has the coefficients of D. -/
theorem D_is_the_quotient (X : Poly) (h : mulP (qfactProd b) X = qfactProd a) :
    ∀ k, coeff X k = coeff D k :=
  quotient_unique (qfactProd b) X D denominator_constant_term (h.trans division.symm)

theorem one_plus_q_times_D : mulP [1, 1] D = C := by decide +kernel

/-- D = [10][11](1 - q^2 + q^4); the last factor is the 12th cyclotomic polynomial. -/
theorem factorisation : D = mulP (mulP (qint 10) (qint 11)) [1, 0, -1, 0, 1] := by decide +kernel

/-! ### Landau's criterion (1) -/
/-- What n |-> floor(n x) satisfies for a real x: m floor(n x) <= m n x < n (floor(m x) + 1). -/
def IsFloorProfile (fl : Nat → Int) : Prop :=
  ∀ n m : Nat, 0 < n → 0 < m → fl n * m < (fl m + 1) * n

/-- sum over the tuple of floor(l_i x), with floor(n x) = fl n. -/
def floorSum (fl : Nat → Int) : List Nat → Int
  | [] => 0
  | n :: l => fl n + floorSum fl l

/-- Landau's criterion (1) for the pair (a, b): nonnegativity at every floor profile of an x >= 0
(for x >= 0 every floor(n x) is nonnegative). -/
def LandauCriterion (a b : List Nat) : Prop :=
  ∀ fl : Nat → Int, IsFloorProfile fl → (∀ n, 0 ≤ fl n) → 0 ≤ floorSum fl a - floorSum fl b

/-- The witness, at EVERY floor profile (the sign condition on x is not needed: the pair is
balanced, so the Landau function has period 1). -/
theorem landau_profile (fl : Nat → Int) (h : IsFloorProfile fl) :
    0 ≤ floorSum fl a - floorSum fl b := by
  simp only [floorSum, a, b]
  have h_1_12 := h 1 12 (by decide) (by decide)
  have h_12_1 := h 12 1 (by decide) (by decide)
  have h_2_12 := h 2 12 (by decide) (by decide)
  have h_12_2 := h 12 2 (by decide) (by decide)
  have h_3_12 := h 3 12 (by decide) (by decide)
  have h_12_3 := h 12 3 (by decide) (by decide)
  have h_4_12 := h 4 12 (by decide) (by decide)
  have h_12_4 := h 12 4 (by decide) (by decide)
  have h_6_12 := h 6 12 (by decide) (by decide)
  have h_12_6 := h 12 6 (by decide) (by decide)
  have h_5_12 := h 5 12 (by decide) (by decide)
  have h_12_5 := h 12 5 (by decide) (by decide)
  have h_9_12 := h 9 12 (by decide) (by decide)
  have h_12_9 := h 12 9 (by decide) (by decide)
  have h_5_9 := h 5 9 (by decide) (by decide)
  have h_9_5 := h 9 5 (by decide) (by decide)
  have hr : fl 12 - 12 * fl 1 = 0 ∨ fl 12 - 12 * fl 1 = 1 ∨ fl 12 - 12 * fl 1 = 2 ∨
      fl 12 - 12 * fl 1 = 3 ∨ fl 12 - 12 * fl 1 = 4 ∨ fl 12 - 12 * fl 1 = 5 ∨
      fl 12 - 12 * fl 1 = 6 ∨ fl 12 - 12 * fl 1 = 7 ∨ fl 12 - 12 * fl 1 = 8 ∨
      fl 12 - 12 * fl 1 = 9 ∨ fl 12 - 12 * fl 1 = 10 ∨ fl 12 - 12 * fl 1 = 11 := by omega
  rcases hr with hr | hr | hr | hr | hr | hr | hr | hr | hr | hr | hr | hr <;> omega

/-- Criterion (1) for the witness. -/
theorem landau_criterion : LandauCriterion a b := fun fl h _ => landau_profile fl h

/-! #### The Landau function on one period: 180 grid points, 22 breakpoint cells -/
/-- L(j/180). Every entry of a and b divides 180, so every breakpoint k/n is some j/180. -/
def Lgrid (j : Nat) : Int :=
  floorSum (fun k => ((k * j / 180 : Nat) : Int)) a -
    floorSum (fun k => ((k * j / 180 : Nat) : Int)) b

/-- At EVERY floor profile the Landau function takes one of the 180 values L(j/180):
with f = fl 1 and j = fl 180 - 180 f, each entry n (a divisor of 180) has fl n = n f + floor(n j/180),
and the f-terms cancel because both tuples sum to 22. -/
theorem profile_on_grid (fl : Nat → Int) (h : IsFloorProfile fl) :
    ∃ j : Nat, j < 180 ∧ floorSum fl a - floorSum fl b = Lgrid j := by
  have g_1 := h 1 180 (by decide) (by decide)
  have k_1 := h 180 1 (by decide) (by decide)
  obtain ⟨j, hj⟩ : ∃ j : Nat, (j : Int) = fl 180 - 180 * fl 1 :=
    ⟨(fl 180 - 180 * fl 1).toNat, by omega⟩
  have hj180 : j < 180 := by omega
  have e1 : fl 1 = 1 * fl 1 + ((1 * j / 180 : Nat) : Int) := by omega
  have e2 : fl 2 = 2 * fl 1 + ((2 * j / 180 : Nat) : Int) := by
    have g := h 2 180 (by decide) (by decide)
    have k := h 180 2 (by decide) (by decide)
    omega
  have e3 : fl 3 = 3 * fl 1 + ((3 * j / 180 : Nat) : Int) := by
    have g := h 3 180 (by decide) (by decide)
    have k := h 180 3 (by decide) (by decide)
    omega
  have e4 : fl 4 = 4 * fl 1 + ((4 * j / 180 : Nat) : Int) := by
    have g := h 4 180 (by decide) (by decide)
    have k := h 180 4 (by decide) (by decide)
    omega
  have e5 : fl 5 = 5 * fl 1 + ((5 * j / 180 : Nat) : Int) := by
    have g := h 5 180 (by decide) (by decide)
    have k := h 180 5 (by decide) (by decide)
    omega
  have e6 : fl 6 = 6 * fl 1 + ((6 * j / 180 : Nat) : Int) := by
    have g := h 6 180 (by decide) (by decide)
    have k := h 180 6 (by decide) (by decide)
    omega
  have e9 : fl 9 = 9 * fl 1 + ((9 * j / 180 : Nat) : Int) := by
    have g := h 9 180 (by decide) (by decide)
    have k := h 180 9 (by decide) (by decide)
    omega
  have e12 : fl 12 = 12 * fl 1 + ((12 * j / 180 : Nat) : Int) := by
    have g := h 12 180 (by decide) (by decide)
    have k := h 180 12 (by decide) (by decide)
    omega
  refine ⟨j, hj180, ?_⟩
  simp only [Lgrid, floorSum, a, b]
  rw [e1, e2, e3, e4, e5, e6, e9, e12]
  generalize ((1 * j / 180 : Nat) : Int) = d1
  generalize ((2 * j / 180 : Nat) : Int) = d2
  generalize ((3 * j / 180 : Nat) : Int) = d3
  generalize ((4 * j / 180 : Nat) : Int) = d4
  generalize ((5 * j / 180 : Nat) : Int) = d5
  generalize ((6 * j / 180 : Nat) : Int) = d6
  generalize ((9 * j / 180 : Nat) : Int) = d9
  generalize ((12 * j / 180 : Nat) : Int) = d12
  omega

/-- Numerators j of the 23 breakpoints j/180 = k/n in [0,1] (n an entry of a or b, 0 <= k <= n):
0, 1/12, 1/9, 1/6, 1/5, 2/9, 1/4, 1/3, 2/5, 5/12, 4/9, 1/2, 5/9, 7/12, 3/5, 2/3, 3/4, 7/9, 4/5,
5/6, 8/9, 11/12, 1. -/
def breakpoints : List Nat :=
  [0, 15, 20, 30, 36, 40, 45, 60, 72, 75, 80, 90, 100, 105, 108, 120, 135, 140, 144, 150, 160,
    165, 180]

/-- j/180 is a breakpoint exactly when j/180 = k/n for an entry n, i.e. 180 divides j n. -/
theorem breakpoints_complete : ∀ j : Nat, j < 181 →
    (j ∈ breakpoints ↔ ∃ n, n ∈ a ++ b ∧ (j * n) % 180 = 0) := by decide +kernel

/-- The value of L on each of the 22 half-open cells (and L(1) = 0): minimum 0, maximum 2. -/
theorem landau_cells : breakpoints.map Lgrid =
    [0, 1, 0, 0, 1, 0, 0, 0, 1, 2, 1, 1, 0, 1, 2, 2, 2, 1, 2, 2, 1, 2, 0] := by decide +kernel

/-- L changes only at breakpoints, so it is constant on each cell. -/
theorem landau_constant_on_cells : ∀ j : Nat, j < 180 → j + 1 ∉ breakpoints →
    Lgrid (j + 1) = Lgrid j := by decide +kernel

theorem landau_grid_nonneg : ∀ j : Nat, j < 180 → 0 ≤ Lgrid j := by decide +kernel

/-- Second proof of criterion (1) at every floor profile, through the grid. -/
theorem landau_profile' (fl : Nat → Int) (h : IsFloorProfile fl) :
    0 ≤ floorSum fl a - floorSum fl b := by
  obtain ⟨j, hj, e⟩ := profile_on_grid fl h
  rw [e]; exact landau_grid_nonneg j hj

/-! #### Rational x = p/n >= 0: floor(k x) = k*p/n (natural-number division) is a floor profile -/
theorem ratProfile (p n : Nat) (hn : 0 < n) :
    IsFloorProfile (fun k => ((k * p / n : Nat) : Int)) := by
  intro k m hk _hm
  have h1 : k * p / n * n ≤ k * p := Nat.div_mul_le_self _ _
  have h2 : m * p < (m * p / n + 1) * n := by
    have e := Nat.div_add_mod (m * p) n
    have l := Nat.mod_lt (m * p) hn
    rw [Nat.add_mul, Nat.mul_comm (m * p / n) n]; omega
  have h3 : (k * p / n * m) * n < ((m * p / n + 1) * k) * n := by
    have e1 : (k * p / n * m) * n = (k * p / n * n) * m := Nat.mul_right_comm _ _ _
    have e2 : (k * p) * m = k * (m * p) := by rw [Nat.mul_assoc, Nat.mul_comm p m]
    have e3 : ((m * p / n + 1) * k) * n = k * ((m * p / n + 1) * n) := by
      rw [Nat.mul_comm (m * p / n + 1) k, Nat.mul_assoc]
    have l1 : (k * p / n * n) * m ≤ (k * p) * m := Nat.mul_le_mul_right _ h1
    have l2 : k * (m * p) < k * ((m * p / n + 1) * n) := Nat.mul_lt_mul_of_pos_left h2 hk
    omega
  have h4 : k * p / n * m < (m * p / n + 1) * k := Nat.lt_of_mul_lt_mul_right h3
  show ((k * p / n : Nat) : Int) * (m : Int) < (((m * p / n : Nat) : Int) + 1) * (k : Int)
  exact_mod_cast h4

/-- Criterion (1) at every rational x = p/n >= 0, floors written as natural-number division. -/
theorem landau_rational (p n : Nat) (hn : 0 < n) :
    1 * p / n + 1 * p / n + 1 * p / n + 4 * p / n + 6 * p / n + 9 * p / n ≤
      2 * p / n + 3 * p / n + 5 * p / n + 12 * p / n := by
  have h := landau_profile _ (ratProfile p n hn)
  simp only [floorSum, a, b] at h
  omega

/-- The criterion is not vacuous: it fails for a = (1), b = (2) at x = 1/2. -/
theorem landau_can_fail : ¬ LandauCriterion [1] [2] := by
  intro h
  have := h _ (ratProfile 1 2 (by decide)) (fun n => Int.natCast_nonneg _)
  revert this; decide

/-! #### Any ordered structure with a floor induces floor profiles -/
/-- The properties of (R, <=, <, n • x, Z -> R, floor) used below; the real numbers have them all. -/
structure FloorModel (R : Type) where
  le : R → R → Prop
  lt : R → R → Prop
  smul : Nat → R → R
  ofInt : Int → R
  floor : R → Int
  floor_le : ∀ y, le (ofInt (floor y)) y
  lt_floor_add_one : ∀ y, lt y (ofInt (floor y + 1))
  smul_smul : ∀ m n x, smul m (smul n x) = smul (m * n) x
  smul_le : ∀ m y z, le y z → le (smul m y) (smul m z)
  smul_lt : ∀ m y z, 0 < m → lt y z → lt (smul m y) (smul m z)
  smul_ofInt : ∀ m z, smul m (ofInt z) = ofInt (z * m)
  lt_of_le_of_lt : ∀ x y z, le x y → lt y z → lt x z
  ofInt_lt : ∀ z w, lt (ofInt z) (ofInt w) → z < w

theorem FloorModel.profile {R : Type} (M : FloorModel R) (x : R) :
    IsFloorProfile (fun n => M.floor (M.smul n x)) := by
  intro n m hn _hm
  show M.floor (M.smul n x) * (m : Int) < (M.floor (M.smul m x) + 1) * (n : Int)
  apply M.ofInt_lt
  rw [← M.smul_ofInt m, ← M.smul_ofInt n]
  have l1 := M.smul_le m _ _ (M.floor_le (M.smul n x))
  have l2 := M.smul_lt n _ _ hn (M.lt_floor_add_one (M.smul m x))
  rw [M.smul_smul] at l1 l2
  rw [Nat.mul_comm n m] at l2
  exact M.lt_of_le_of_lt _ _ _ l1 l2

/-- Criterion (1) for the witness at every element x of every such structure. -/
theorem landau_model {R : Type} (M : FloorModel R) (x : R) :
    0 ≤ floorSum (fun n => M.floor (M.smul n x)) a - floorSum (fun n => M.floor (M.smul n x)) b :=
  landau_profile _ (M.profile x)

/-- The structure axioms are consistent: the integers form a model. -/
def intModel : FloorModel Int where
  le := (· ≤ ·)
  lt := (· < ·)
  smul := fun n x => x * n
  ofInt := id
  floor := id
  floor_le := fun y => Int.le_refl y
  lt_floor_add_one := fun y => by show y < y + 1; omega
  smul_smul := fun m n x => by
    show x * (n : Int) * (m : Int) = x * ((m * n : Nat) : Int)
    rw [Int.mul_assoc, Int.natCast_mul, Int.mul_comm (n : Int) (m : Int)]
  smul_le := fun m y z h => Int.mul_le_mul_of_nonneg_right h (Int.natCast_nonneg m)
  smul_lt := fun m y z hm h =>
    Int.mul_lt_mul_of_pos_right h (by omega)
  smul_ofInt := fun _ _ => rfl
  lt_of_le_of_lt := fun _ _ _ => Int.lt_of_le_of_lt
  ofInt_lt := fun _ _ h => h

/-! ### Unimodality -/
/-- c_0 <= c_1 <= ... <= c_h >= c_{h+1} >= ... >= c_d for some h (d = last index of the list). -/
def Unimodal (c : Poly) : Prop :=
  ∃ h : Nat, (∀ i, i < h → coeff c i ≤ coeff c (i + 1)) ∧
    (∀ i, h ≤ i → i + 1 < c.length → coeff c (i + 1) ≤ coeff c i)

/-- The source's wording: c_i = c_{k-i} for all i and c_0 <= c_1 <= ... <= c_{floor(k/2)},
with k = last index. -/
def SymUnimodal (c : Poly) : Prop :=
  (∀ i, i < c.length → coeff c i = coeff c (c.length - 1 - i)) ∧
    (∀ i, i < (c.length - 1) / 2 → coeff c i ≤ coeff c (i + 1))

/-- The source's wording implies the peak wording, for every coefficient list; so `Unimodal` is the
weaker reading and its failure is the stronger refutation. -/
theorem SymUnimodal.unimodal {c : Poly} (h : SymUnimodal c) : Unimodal c := by
  obtain ⟨hs, hup⟩ := h
  refine ⟨(c.length - 1) / 2, hup, ?_⟩
  intro i hi hlt
  have e1 := hs (i + 1) hlt
  have e2 := hs i (by omega)
  by_cases hc : c.length - 1 - (i + 1) < (c.length - 1) / 2
  · have l := hup (c.length - 1 - (i + 1)) hc
    have e3 : c.length - 1 - (i + 1) + 1 = c.length - 1 - i := by omega
    rw [e3] at l; omega
  · have e3 : c.length - 1 - (i + 1) = i := by omega
    rw [e3] at e1; omega

theorem C_not_unimodal : ¬ Unimodal C := by
  intro ⟨h, hup, hdown⟩
  by_cases hh : 10 < h
  · have := hup 10 hh
    revert this; decide
  · have := hdown 12 (by omega) (by decide)
    revert this; decide

theorem C_not_symUnimodal : ¬ SymUnimodal C := by
  intro ⟨_, hup⟩
  have := hup 10 (by decide)
  revert this; decide

/-- C is palindromic with nonzero top coefficient, so its degree is 24 and only the monotone half
of `SymUnimodal` fails. -/
theorem C_symmetric : (∀ i, i < C.length → coeff C i = coeff C (C.length - 1 - i)) ∧
    C.length = 25 ∧ coeff C 24 = 1 := by decide

/-! ### The refutation -/
/-- The witness satisfies every hypothesis of Conjecture 5 and (1+q) D(a,b;q) is not unimodal. -/
theorem refutes_conjecture5 :
    (a ≠ [] ∧ b ≠ [] ∧ (∀ n ∈ a, 0 < n) ∧ (∀ n ∈ b, 0 < n)) ∧
    (a.foldr (· + ·) 0 = 22 ∧ b.foldr (· + ·) 0 = 22 ∧ (∀ n ∈ a, n ∉ b) ∧ 1 ∈ b) ∧
    LandauCriterion a b ∧
    (∀ fl : Nat → Int, IsFloorProfile fl → 0 ≤ floorSum fl a - floorSum fl b) ∧
    (∀ p n : Nat, 0 < n →
      1 * p / n + 1 * p / n + 1 * p / n + 4 * p / n + 6 * p / n + 9 * p / n ≤
        2 * p / n + 3 * p / n + 5 * p / n + 12 * p / n) ∧
    mulP (qfactProd b) D = qfactProd a ∧
    (∀ X : Poly, mulP (qfactProd b) X = qfactProd a → ∀ k, coeff X k = coeff D k) ∧
    mulP [1, 1] D = C ∧
    ¬ Unimodal C ∧ ¬ SymUnimodal C :=
  ⟨⟨by decide, by decide, by decide, by decide⟩, ⟨by decide, by decide, by decide, by decide⟩,
    landau_criterion, landau_profile, landau_rational, division,
    D_is_the_quotient, one_plus_q_times_D, C_not_unimodal, C_not_symUnimodal⟩

/-- Conjecture 5 as a proposition, with the weaker of the two readings of "unimodal". -/
def Conjecture5 : Prop :=
  ∀ (a b : List Nat) (D : Poly), a ≠ [] → b ≠ [] → (∀ n ∈ a, 0 < n) → (∀ n ∈ b, 0 < n) →
    LandauCriterion a b → mulP (qfactProd b) D = qfactProd a → Unimodal (mulP [1, 1] D)

theorem not_conjecture5 : ¬ Conjecture5 := fun hc =>
  C_not_unimodal (one_plus_q_times_D ▸
    hc a b D (by decide) (by decide) (by decide) (by decide) landau_criterion division)

/-- The same with the source's "symmetric and unimodal" wording. -/
def Conjecture5Sym : Prop :=
  ∀ (a b : List Nat) (D : Poly), a ≠ [] → b ≠ [] → (∀ n ∈ a, 0 < n) → (∀ n ∈ b, 0 < n) →
    LandauCriterion a b → mulP (qfactProd b) D = qfactProd a → SymUnimodal (mulP [1, 1] D)

theorem not_conjecture5Sym : ¬ Conjecture5Sym := fun hc =>
  C_not_symUnimodal (one_plus_q_times_D ▸
    hc a b D (by decide) (by decide) (by decide) (by decide) landau_criterion division)

end QriousUnimodality

#print axioms QriousUnimodality.refutes_conjecture5
#print axioms QriousUnimodality.not_conjecture5
#print axioms QriousUnimodality.not_conjecture5Sym
#print axioms QriousUnimodality.division
#print axioms QriousUnimodality.D_is_the_quotient
#print axioms QriousUnimodality.one_plus_q_times_D
#print axioms QriousUnimodality.factorisation
#print axioms QriousUnimodality.landau_profile
#print axioms QriousUnimodality.landau_rational
#print axioms QriousUnimodality.landau_model
#print axioms QriousUnimodality.coeff_mulP
#print axioms QriousUnimodality.coeff_qint
#print axioms QriousUnimodality.one_sub_q_mul_qint
#print axioms QriousUnimodality.SymUnimodal.unimodal
#print axioms QriousUnimodality.quotient_unique
#print axioms QriousUnimodality.ratProfile
#print axioms QriousUnimodality.FloorModel.profile
#print axioms QriousUnimodality.profile_on_grid
#print axioms QriousUnimodality.breakpoints_complete
#print axioms QriousUnimodality.landau_cells
#print axioms QriousUnimodality.landau_constant_on_cells
#print axioms QriousUnimodality.landau_grid_nonneg
#print axioms QriousUnimodality.landau_profile'
#print axioms QriousUnimodality.landau_criterion
#print axioms QriousUnimodality.landau_can_fail
#print axioms QriousUnimodality.qint_source_form
#print axioms QriousUnimodality.C_not_unimodal
#print axioms QriousUnimodality.C_not_symUnimodal
