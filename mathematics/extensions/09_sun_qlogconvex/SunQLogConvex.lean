/-!
# Kernel certificate: Sun's binomial q-log-convexity assertion fails at m = 11 (2026-09-19)

NEW dated artifact, outside the frozen 285-record release. Core Lean only; no Mathlib, no `sorry`,
no `native_decide`.

Source: Zhi-Wei Sun, "A family of polynomials and related congruences and series",
arXiv:2505.02767v4 (text layer of the arXiv PDF read on 2026-09-19; quotes in BINDING.md).
Definition (Section 1): "A sequence (P_n(q))_{n>=0} of polynomials with integer coefficients is said
to be q-log-convex if for each positive integer n all the coefficients of the polynomial
P_{n-1}(q)P_{n+1}(q) - P_n(q)^2 in Z[q] are nonnegative."
Conjecture 1.1(i), second sentence: "Also, for each integer m >= 2, the sequence
(sum_{k=0}^n binom(n+k,k)^m q^k)_{n>=0} is q-log-convex."

Certified (`second_assertion_false`): that sentence is false. For m = 11 and the positive integer
n = 3, the coefficient of q^2 in V_2(q)V_4(q) - V_3(q)^2 is -492311528610 < 0, where
V_n(q) = sum_{k=0}^n binom(n+k,k)^11 q^k. The sentence is a universal statement over m >= 2 and
over positive n, so this single instance refutes it.

Scope. Conjecture 1.1 bundles four assertions (two in (i), two in (ii)). ONLY the second one is
refuted here. `conjecture_1_1_false` records the purely logical consequence that the conjunction of
the four fails; nothing is proved about the other three (binom(n,k)^3 from n = 8, S^(2), S^(3)).

A polynomial is represented by its coefficient sequence `Nat -> Int`; the coefficient of q^d in a
product is the Cauchy convolution `mulCoeff`. A second representation by coefficient lists with
schoolbook multiplication is proved equivalent for every m (`coeffL_mulL`, `qlogconvexL_iff`).

Extension, NOT part of the recorded case (found while formalising, labelled as such in
BINDING.md): `not_qlogconvex_of_four_le` shows the sequence fails to be q-log-convex for EVERY
m >= 4 (n = 23 for 4 <= m <= 10, n = 3 for m >= 11, always at q^2).
-/
namespace SunQLogConvex

/-! ### Binomial coefficients (Pascal's rule) and their factorial formula -/

/-- Binomial coefficient binom(n, k), by Pascal's rule. -/
def binom : Nat → Nat → Nat
  | _, 0 => 1
  | 0, _ + 1 => 0
  | n + 1, k + 1 => binom n k + binom n (k + 1)

def fact : Nat → Nat
  | 0 => 1
  | n + 1 => (n + 1) * fact n

theorem binom_eq_zero : ∀ n k : Nat, n < k → binom n k = 0
  | _, 0, h => by omega
  | 0, _ + 1, _ => rfl
  | n + 1, k + 1, h => by
    show binom n k + binom n (k + 1) = 0
    rw [binom_eq_zero n k (by omega), binom_eq_zero n (k + 1) (by omega)]

theorem binom_self : ∀ n : Nat, binom n n = 1
  | 0 => rfl
  | n + 1 => by
    show binom n n + binom n (n + 1) = 1
    rw [binom_self n, binom_eq_zero n (n + 1) (by omega)]

theorem binom_fact_aux : ∀ s a b : Nat, a + b = s →
    binom (a + b) b * fact a * fact b = fact (a + b) := by
  intro s
  induction s with
  | zero =>
    intro a b h
    have ha : a = 0 := by omega
    have hb : b = 0 := by omega
    subst ha; subst hb; rfl
  | succ s ih =>
    intro a b h
    cases a with
    | zero => simp only [Nat.zero_add, binom_self, fact, Nat.one_mul]
    | succ a =>
      cases b with
      | zero => simp [binom, fact]
      | succ b =>
        have e1 : a + 1 + (b + 1) = (a + 1 + b) + 1 := by omega
        have h1 := ih (a + 1) b (by omega)
        have h2 := ih a (b + 1) (by omega)
        have e2 : a + (b + 1) = a + 1 + b := by omega
        rw [e2] at h2
        rw [e1]
        show (binom (a + 1 + b) b + binom (a + 1 + b) (b + 1)) * fact (a + 1) * fact (b + 1)
          = (a + 1 + b + 1) * fact (a + 1 + b)
        have f1 : fact (b + 1) = (b + 1) * fact b := rfl
        have f2 : fact (a + 1) = (a + 1) * fact a := rfl
        grind

/-- `binom` is the ordinary binomial coefficient: binom(n+k, k) * (n! * k!) = (n+k)!. -/
theorem binom_factorial (n k : Nat) : binom (n + k) k * (fact n * fact k) = fact (n + k) := by
  rw [← Nat.mul_assoc]; exact binom_fact_aux (n + k) n k rfl

/-- The same in the form binom(n, k) * (k! * (n-k)!) = n! for k <= n. -/
theorem binom_factorial' (n k : Nat) (h : k ≤ n) : binom n k * (fact k * fact (n - k)) = fact n := by
  have e := binom_factorial (n - k) k
  rw [Nat.sub_add_cancel h] at e
  rw [Nat.mul_comm (fact k)]; exact e

/-! ### Polynomials as coefficient sequences, Cauchy product, q-log-convexity -/

/-- sum_{i=0}^{d} f i. -/
def sumTo (f : Nat → Int) : Nat → Int
  | 0 => f 0
  | d + 1 => sumTo f d + f (d + 1)

/-- Coefficient of q^d in the product of the polynomials with coefficient sequences a and b:
sum_{i=0}^{d} a_i * b_{d-i}. -/
def mulCoeff (a b : Nat → Int) (d : Nat) : Int := sumTo (fun i => a i * b (d - i)) d

/-- Coefficient of q^d in P_{n-1}(q) P_{n+1}(q) - P_n(q)^2. -/
def diffCoeff (P : Nat → Nat → Int) (n d : Nat) : Int :=
  mulCoeff (P (n - 1)) (P (n + 1)) d - mulCoeff (P n) (P n) d

/-- The source's definition for a sequence (P_n(q))_{n>=0}: for each positive integer n all the
coefficients of P_{n-1}(q) P_{n+1}(q) - P_n(q)^2 are nonnegative. -/
def QLogConvex (P : Nat → Nat → Int) : Prop :=
  ∀ n : Nat, 1 ≤ n → ∀ d : Nat, 0 ≤ diffCoeff P n d

/-- The same for a sequence (P_n(q))_{n>=a}: central indices n >= a + 1. -/
def QLogConvexFrom (a : Nat) (P : Nat → Nat → Int) : Prop :=
  ∀ n : Nat, a + 1 ≤ n → ∀ d : Nat, 0 ≤ diffCoeff P n d

theorem qLogConvexFrom_zero (P : Nat → Nat → Int) : QLogConvexFrom 0 P ↔ QLogConvex P := by
  unfold QLogConvexFrom QLogConvex
  constructor
  · intro h n hn d; exact h n (by omega) d
  · intro h n hn d; exact h n (by omega) d

/-- Coefficient of q^k in V_{n,m}(q) = sum_{k=0}^{n} binom(n+k, k)^m q^k. -/
def V (n m : Nat) (k : Nat) : Int := if k ≤ n then ((binom (n + k) k : Nat) : Int) ^ m else 0

theorem V_of_le (n m k : Nat) (h : k ≤ n) : V n m k = ((binom (n + k) k : Nat) : Int) ^ m := by
  unfold V; split
  · rfl
  · contradiction

/-- V_{n,m} is a polynomial of degree at most n. -/
theorem V_of_gt (n m k : Nat) (h : n < k) : V n m k = 0 := by
  unfold V; split
  · omega
  · rfl

/-! ### The recorded refutation: m = 11, central index n = 3, coefficient of q^2 -/

theorem witness_bases :
    (List.range 3).map (fun k => binom (2 + k) k) = [1, 3, 6] ∧
    (List.range 4).map (fun k => binom (3 + k) k) = [1, 4, 10, 20] ∧
    (List.range 5).map (fun k => binom (4 + k) k) = [1, 5, 15, 35, 70] := by decide +kernel

theorem witness_products :
    mulCoeff (V 2 11) (V 4 11) 2 = 2 * 15 ^ 11 + 6 ^ 11 ∧
    mulCoeff (V 2 11) (V 4 11) 2 = 17299874515806 ∧
    mulCoeff (V 3 11) (V 3 11) 2 = 2 * 10 ^ 11 + 16 ^ 11 ∧
    mulCoeff (V 3 11) (V 3 11) 2 = 17792186044416 := by decide +kernel

/-- [q^2] (V_{2,11} V_{4,11} - V_{3,11}^2) = -492311528610. -/
theorem witness_value : diffCoeff (fun n => V n 11) 3 2 = -492311528610 := by decide +kernel

/-- HEADLINE. The second assertion of Conjecture 1.1(i) is false: it is not the case that for each
integer m >= 2 the sequence (sum_{k=0}^n binom(n+k,k)^m q^k)_{n>=0} is q-log-convex. -/
theorem second_assertion_false : ¬ (∀ m : Nat, 2 ≤ m → QLogConvex (fun n => V n m)) := by
  intro h
  have h1 := h 11 (by decide) 3 (by decide) 2
  rw [witness_value] at h1
  exact absurd h1 (by decide)

/-- The same with the witness displayed: an admissible exponent m >= 2, a positive central index n
and a degree d whose coefficient is negative. -/
theorem second_assertion_false_explicit :
    ∃ m n d : Nat, 2 ≤ m ∧ 1 ≤ n ∧ diffCoeff (fun n => V n m) n d < 0 :=
  ⟨11, 3, 2, by decide, by decide, by rw [witness_value]; decide⟩

/-! ### Conjecture 1.1 as a whole (four assertions); only the second is touched -/

/-- Coefficient of q^k in sum_{k=0}^{n} binom(n, k)^3 q^k. -/
def U (n : Nat) (k : Nat) : Int := if k ≤ n then ((binom n k : Nat) : Int) ^ 3 else 0

/-- Coefficient of x^d in S_n^{(m)}(x) = sum_{i,j=0}^{n} binom(n,i)^m binom(n,j)^m binom(i+j,i) x^{i+j}. -/
def S (m n : Nat) (d : Nat) : Int :=
  sumTo (fun i => if i ≤ n ∧ d - i ≤ n then
    ((binom n i ^ m * binom n (d - i) ^ m * binom d i : Nat) : Int) else 0) d

/-- Sanity values: S_1^{(2)}(x) = 1 + 2x + 2x^2, and S_n^{(2)}(1) = 1, 5, 73 for n = 0, 1, 2
(the Apery numbers, as the source's Remark 1.1 says). -/
theorem S_sanity :
    (S 2 1 0 = 1 ∧ S 2 1 1 = 2 ∧ S 2 1 2 = 2 ∧ S 2 1 3 = 0) ∧
    S 2 0 0 = 1 ∧ sumTo (S 2 1) 2 = 5 ∧ sumTo (S 2 2) 4 = 73 := by decide +kernel

theorem U_sanity : (List.range 5).map (U 3) = [1, 27, 27, 1, 0] := by decide +kernel

/-- Conjecture 1.1 of the source: (i) first sentence, (i) second sentence, (ii) first sequence,
(ii) second sequence. -/
def Conjecture_1_1 : Prop :=
  QLogConvexFrom 8 U ∧
  (∀ m : Nat, 2 ≤ m → QLogConvex (fun n => V n m)) ∧
  QLogConvex (S 2) ∧
  QLogConvexFrom 2 (S 3)

/-- The conjunction fails because its second conjunct fails. Nothing is proved about the first,
third and fourth conjuncts; this theorem does not depend on how `U` and `S` are defined. -/
theorem conjecture_1_1_false : ¬ Conjecture_1_1 := fun h => second_assertion_false h.2.1

/-! ### Non-vacuity: the definition is not trivially violated -/

/-- For m = 2 every coefficient is nonnegative at the central indices 1, ..., 6 (degrees 0..14 cover
the whole polynomial, whose degree is 2n <= 12). -/
theorem sanity_m2 : ∀ n : Nat, n < 7 → 1 ≤ n → ∀ d : Nat, d < 15 →
    0 ≤ diffCoeff (fun n => V n 2) n d := by decide +kernel

theorem sanity_m3 : ∀ n : Nat, n < 7 → 1 ≤ n → ∀ d : Nat, d < 15 →
    0 ≤ diffCoeff (fun n => V n 3) n d := by decide +kernel

/-! ### Cross-check: polynomials as coefficient lists with schoolbook multiplication -/

def coeffL (p : List Int) (d : Nat) : Int := p.getD d 0

def addL : List Int → List Int → List Int
  | [], q => q
  | a :: p, [] => a :: p
  | a :: p, b :: q => (a + b) :: addL p q

def smulL (c : Int) : List Int → List Int
  | [] => []
  | b :: q => (c * b) :: smulL c q

def mulL : List Int → List Int → List Int
  | [], _ => []
  | a :: p, q => addL (smulL a q) (0 :: mulL p q)

def subL (p q : List Int) : List Int := addL p (smulL (-1) q)

/-- V_{n,m}(q) as the list of its n + 1 coefficients. -/
def VL (n m : Nat) : List Int :=
  (List.range (n + 1)).map fun k => ((binom (n + k) k : Nat) : Int) ^ m

def QLogConvexL (P : Nat → List Int) : Prop :=
  ∀ n : Nat, 1 ≤ n → ∀ d : Nat,
    0 ≤ coeffL (subL (mulL (P (n - 1)) (P (n + 1))) (mulL (P n) (P n))) d

theorem coeffL_nil (d : Nat) : coeffL [] d = 0 := by simp [coeffL]
theorem coeffL_cons_zero (a : Int) (p : List Int) : coeffL (a :: p) 0 = a := by simp [coeffL]
theorem coeffL_cons_succ (a : Int) (p : List Int) (d : Nat) :
    coeffL (a :: p) (d + 1) = coeffL p d := by simp [coeffL]

theorem coeffL_addL : ∀ (p q : List Int) (d : Nat), coeffL (addL p q) d = coeffL p d + coeffL q d
  | [], q, d => by simp [addL, coeffL_nil]
  | a :: p, [], d => by simp [addL, coeffL_nil]
  | a :: p, b :: q, 0 => by simp [addL, coeffL_cons_zero]
  | a :: p, b :: q, d + 1 => by simp [addL, coeffL_cons_succ, coeffL_addL p q d]

theorem coeffL_smulL (c : Int) : ∀ (p : List Int) (d : Nat), coeffL (smulL c p) d = c * coeffL p d
  | [], d => by simp [smulL, coeffL_nil]
  | b :: q, 0 => by simp [smulL, coeffL_cons_zero]
  | b :: q, d + 1 => by simp [smulL, coeffL_cons_succ, coeffL_smulL c q d]

theorem coeffL_subL (p q : List Int) (d : Nat) : coeffL (subL p q) d = coeffL p d - coeffL q d := by
  unfold subL; rw [coeffL_addL, coeffL_smulL]; omega

theorem sumTo_shift (f : Nat → Int) :
    ∀ e : Nat, sumTo f (e + 1) = f 0 + sumTo (fun i => f (i + 1)) e
  | 0 => rfl
  | e + 1 => by
    show sumTo f (e + 1) + f (e + 1 + 1) = f 0 + (sumTo (fun i => f (i + 1)) e + f (e + 1 + 1))
    rw [sumTo_shift f e]; omega

theorem sumTo_zero_fun : ∀ e : Nat, sumTo (fun _ => 0) e = 0
  | 0 => rfl
  | e + 1 => by show sumTo (fun _ => 0) e + 0 = 0; rw [sumTo_zero_fun e]; rfl

/-- Schoolbook list multiplication computes the Cauchy product, for all lists and all degrees. -/
theorem coeffL_mulL : ∀ (p q : List Int) (d : Nat),
    coeffL (mulL p q) d = mulCoeff (coeffL p) (coeffL q) d
  | [], q, d => by
    have : (fun i => coeffL [] i * coeffL q (d - i)) = fun _ => 0 := by
      funext i; rw [coeffL_nil, Int.zero_mul]
    show coeffL [] d = sumTo (fun i => coeffL [] i * coeffL q (d - i)) d
    rw [this, sumTo_zero_fun, coeffL_nil]
  | a :: p, q, 0 => by
    show coeffL (addL (smulL a q) (0 :: mulL p q)) 0 = coeffL (a :: p) 0 * coeffL q (0 - 0)
    rw [coeffL_addL, coeffL_smulL, coeffL_cons_zero, coeffL_cons_zero]; simp
  | a :: p, q, e + 1 => by
    show coeffL (addL (smulL a q) (0 :: mulL p q)) (e + 1) =
      sumTo (fun i => coeffL (a :: p) i * coeffL q (e + 1 - i)) (e + 1)
    rw [coeffL_addL, coeffL_smulL, coeffL_cons_succ, coeffL_mulL p q e, sumTo_shift]
    have : (fun i => coeffL (a :: p) (i + 1) * coeffL q (e + 1 - (i + 1))) =
        fun i => coeffL p i * coeffL q (e - i) := by
      funext i; rw [coeffL_cons_succ, Nat.add_sub_add_right]
    rw [this, coeffL_cons_zero]; rfl

/-- Value of the polynomial with coefficient list p at the integer x (Horner). -/
def evalL (p : List Int) (x : Int) : Int :=
  match p with
  | [] => 0
  | a :: p => a + x * evalL p x

theorem evalL_addL (x : Int) : ∀ p q : List Int, evalL (addL p q) x = evalL p x + evalL q x
  | [], q => by simp [addL, evalL]
  | a :: p, [] => by simp [addL, evalL]
  | a :: p, b :: q => by
    show (a + b) + x * evalL (addL p q) x = (a + x * evalL p x) + (b + x * evalL q x)
    rw [evalL_addL x p q, Int.mul_add]; omega

theorem evalL_smulL (c x : Int) : ∀ p : List Int, evalL (smulL c p) x = c * evalL p x
  | [] => by simp [smulL, evalL]
  | b :: q => by
    show c * b + x * evalL (smulL c q) x = c * (b + x * evalL q x)
    rw [evalL_smulL c x q, Int.mul_add, Int.mul_left_comm]

/-- Semantic check of `mulL`: the list product evaluates to the product of the values, at every
integer point. -/
theorem evalL_mulL (x : Int) : ∀ p q : List Int, evalL (mulL p q) x = evalL p x * evalL q x
  | [], q => by simp [mulL, evalL]
  | a :: p, q => by
    show evalL (addL (smulL a q) (0 :: mulL p q)) x = (a + x * evalL p x) * evalL q x
    rw [evalL_addL, evalL_smulL]
    show a * evalL q x + (0 + x * evalL (mulL p q) x) = (a + x * evalL p x) * evalL q x
    rw [evalL_mulL x p q, Int.add_mul, Int.mul_assoc, Int.zero_add]

/-- The list `VL n m` has exactly the coefficients `V n m`. -/
theorem coeffL_VL (n m k : Nat) : coeffL (VL n m) k = V n m k := by
  unfold coeffL VL V
  rw [List.getD_eq_getElem?_getD, List.getElem?_map]
  by_cases h : k ≤ n
  · have hk : k < n + 1 := by omega
    rw [List.getElem?_range hk]
    simp [h]
  · have hn : (List.range (n + 1))[k]? = none := by
      apply List.getElem?_eq_none
      rw [List.length_range]; omega
    rw [hn]
    simp [h]

/-- The two formalisations of q-log-convexity agree on V, for every m. -/
theorem qlogconvexL_iff (m : Nat) :
    QLogConvexL (fun n => VL n m) ↔ QLogConvex (fun n => V n m) := by
  have key : ∀ n d : Nat,
      coeffL (subL (mulL (VL (n - 1) m) (VL (n + 1) m)) (mulL (VL n m) (VL n m))) d =
        diffCoeff (fun n => V n m) n d := by
    intro n d
    have f : ∀ j : Nat, coeffL (VL j m) = V j m := fun j => funext (coeffL_VL j m)
    rw [coeffL_subL, coeffL_mulL, coeffL_mulL, f, f, f]
    rfl
  constructor
  · intro h n hn d; rw [← key]; exact h n hn d
  · intro h n hn d; show 0 ≤ coeffL _ d; rw [key]; exact h n hn d

/-- The whole polynomial V_{2,11} V_{4,11} - V_{3,11}^2, by list arithmetic. Exactly one
coefficient, that of q^2, is negative. -/
theorem full_difference :
    subL (mulL (VL 2 11) (VL 4 11)) (mulL (VL 3 11) (VL 3 11)) =
      [0, 40616664, -492311528610, 807271758593750000, 8721245297963134765625,
        29095500108444200000000000, 29793792111046860800000000000] := by decide +kernel

/-- HEADLINE, list form. -/
theorem second_assertion_false_lists :
    ¬ (∀ m : Nat, 2 ≤ m → QLogConvexL (fun n => VL n m)) := by
  intro h
  have h1 := h 11 (by decide) 3 (by decide) 2
  have e : coeffL (subL (mulL (VL (3 - 1) 11) (VL (3 + 1) 11)) (mulL (VL 3 11) (VL 3 11))) 2 =
      -492311528610 := by decide +kernel
  rw [e] at h1
  exact absurd h1 (by decide)

/-! ### Extension (not part of the recorded case): failure for every m >= 4 -/

theorem pow_gap : ∀ k : Nat, 2 * 15 ^ (11 + k) + 6 ^ (11 + k) < 16 ^ (11 + k) := by
  intro k
  induction k with
  | zero => decide +kernel
  | succ k ih =>
    have e : 11 + (k + 1) = (11 + k) + 1 := rfl
    rw [e, Nat.pow_succ, Nat.pow_succ, Nat.pow_succ]
    omega

theorem V_eq (n m k : Nat) (c : Int) (hk : k ≤ n) (hc : ((binom (n + k) k : Nat) : Int) = c) :
    V n m k = c ^ m := by
  rw [V_of_le n m k hk, hc]

/-- For every m: [q^2] (V_{2,m} V_{4,m} - V_{3,m}^2) = 2 * 15^m + 6^m - 2 * 10^m - 16^m. -/
theorem coeff_formula (m : Nat) :
    diffCoeff (fun n => V n m) 3 2 = (2 * 15 ^ m + 6 ^ m : Int) - (2 * 10 ^ m + 16 ^ m) := by
  show (V 2 m 0 * V 4 m 2 + V 2 m 1 * V 4 m 1 + V 2 m 2 * V 4 m 0)
      - (V 3 m 0 * V 3 m 2 + V 3 m 1 * V 3 m 1 + V 3 m 2 * V 3 m 0) = _
  rw [V_eq 2 m 0 1 (by decide) (by decide), V_eq 2 m 1 3 (by decide) (by decide),
    V_eq 2 m 2 6 (by decide) (by decide), V_eq 4 m 0 1 (by decide) (by decide),
    V_eq 4 m 1 5 (by decide) (by decide), V_eq 4 m 2 15 (by decide) (by decide),
    V_eq 3 m 0 1 (by decide) (by decide), V_eq 3 m 1 4 (by decide) (by decide),
    V_eq 3 m 2 10 (by decide) (by decide)]
  have e1 : (3 : Int) ^ m * 5 ^ m = 15 ^ m :=
    Int.mul_pow.symm.trans (congrArg (· ^ m) (by decide : (3 : Int) * 5 = 15))
  have e2 : (4 : Int) ^ m * 4 ^ m = 16 ^ m :=
    Int.mul_pow.symm.trans (congrArg (· ^ m) (by decide : (4 : Int) * 4 = 16))
  rw [e1, e2, Int.one_pow, Int.one_mul, Int.one_mul, Int.mul_one, Int.mul_one]
  omega

theorem fails_at_three (m : Nat) (hm : 11 ≤ m) : diffCoeff (fun n => V n m) 3 2 < 0 := by
  obtain ⟨k, rfl⟩ : ∃ k, m = 11 + k := ⟨m - 11, by omega⟩
  rw [coeff_formula]
  have h := pow_gap k
  have h' : (2 * (15 : Int) ^ (11 + k) + 6 ^ (11 + k) < 16 ^ (11 + k)) := by exact_mod_cast h
  have h10 : (0 : Int) ≤ 10 ^ (11 + k) := Int.pow_nonneg (by decide)
  omega

theorem fails_small : ∀ m : Nat, m < 11 → 4 ≤ m → diffCoeff (fun n => V n m) 23 2 < 0 := by
  decide +kernel

/-- EXTENSION. For every m >= 4 the sequence (V_{n,m}(q))_{n>=0} is not q-log-convex. -/
theorem not_qlogconvex_of_four_le (m : Nat) (hm : 4 ≤ m) : ¬ QLogConvex (fun n => V n m) := by
  intro h
  by_cases h11 : 11 ≤ m
  · have h1 := h 3 (by decide) 2
    have h2 := fails_at_three m h11
    omega
  · have h1 := h 23 (by decide) 2
    have h2 := fails_small m (by omega) hm
    omega

end SunQLogConvex

#print axioms SunQLogConvex.witness_value
#print axioms SunQLogConvex.second_assertion_false
#print axioms SunQLogConvex.second_assertion_false_explicit
#print axioms SunQLogConvex.conjecture_1_1_false
#print axioms SunQLogConvex.second_assertion_false_lists
#print axioms SunQLogConvex.qlogconvexL_iff
#print axioms SunQLogConvex.coeffL_mulL
#print axioms SunQLogConvex.full_difference
#print axioms SunQLogConvex.binom_factorial
#print axioms SunQLogConvex.binom_factorial'
#print axioms SunQLogConvex.evalL_mulL
#print axioms SunQLogConvex.S_sanity
#print axioms SunQLogConvex.U_sanity
#print axioms SunQLogConvex.sanity_m3
#print axioms SunQLogConvex.sanity_m2
#print axioms SunQLogConvex.not_qlogconvex_of_four_le
