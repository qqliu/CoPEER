/-!
# Kernel certificate: Conjecture 4 of Gatzweiler and Krattenthaler fails at n = 21, m = 22 (2026-09-19)

NEW dated artifact, outside the frozen 285-record release. Core Lean only; no Mathlib, no `sorry`,
no `native_decide`.

Source: M. Gatzweiler and C. Krattenthaler, "A positivity conjecture for a quotient of q-binomial
coefficients", arXiv:2502.06032v3 (text layer of the arXiv PDF read on 2026-09-19; quotes in
BINDING.md). Expression (2) of the source is
  prod_{i=1}^{n} (1 - q^(m+i))^(a_i) / (1 - q^i)^(a_i),
and Conjecture 4 reads: "Let m and n be given positive integers with m >= n, and let
(a_1, a_2, ..., a_n) be a sequence of non-negative integers. If the expression (2) is a polynomial
(in q) then it has non-negative coefficients."

Certified (`not_conjecture4`): that statement is false. For n = 21, m = 22 and
a_6 = 1, a_14 = a_18 = a_20 = 2, a_21 = 1 (all other a_i = 0), expression (2) equals the explicit
polynomial `Fw` of degree 176 (`witness_division`: Fw * denominator = numerator, as an identity of
integer coefficient lists), and the coefficient of q^43 in `Fw` is -1 (`witness_coeff_43`).
The statement is universal over (m, n, a) with no asymptotic clause, so one admissible triple refutes
it.

Polynomials are lists of integer coefficients (constant term first) with schoolbook multiplication
`mulL`, proved to compute the Cauchy product (`coeffL_mulL`) and to be multiplicative under
evaluation at every integer (`evalL_mulL`). The numerator and the denominator are built from the
lists of 1 - q^k exactly as the source writes the product; `evalL_num` and `evalL_den` show that
they evaluate to prod (1 - x^(m+i))^(a_i) and prod (1 - x^i)^(a_i) at every integer x.
"Expression (2) is a polynomial" is: there is a polynomial P with P * den = num. Such a P is unique
(`quotient_unique`), so "its coefficients" is well defined.

Sanity checks: a Gaussian polynomial (`sanity_gaussian`); the source's own example with m = 1,
n = 17 and the term -q^7 (`sanity_source_example`; there m < n, which is why the source imposes
m >= n); a parameter choice for which expression (2) is not a polynomial (`sanity_not_polynomial`).

NOT refuted here: Conjecture 1 (quotients of q-binomial coefficients), Conjecture 3 (symmetric
sequences; the witness is not symmetric, `aw_not_symmetric`), and the conjecture of Stanton that
the source quotes (polynomiality for all m).
-/
set_option maxRecDepth 100000

namespace FakeGaussian

/-! ### Polynomials as coefficient lists -/

/-- Coefficient of q^d in the polynomial with coefficient list p (constant term first). -/
def coeffL : List Int → Nat → Int
  | [], _ => 0
  | a :: _, 0 => a
  | _ :: p, d + 1 => coeffL p d

def addL : List Int → List Int → List Int
  | [], q => q
  | a :: p, [] => a :: p
  | a :: p, b :: q => (a + b) :: addL p q

def smulL (c : Int) : List Int → List Int
  | [] => []
  | b :: q => (c * b) :: smulL c q

/-- Schoolbook multiplication. -/
def mulL : List Int → List Int → List Int
  | [], _ => []
  | a :: p, q => addL (smulL a q) (0 :: mulL p q)

/-- Two coefficient lists denote the same polynomial (equality up to trailing zeros). -/
def PolyEq (p q : List Int) : Prop := ∀ d : Nat, coeffL p d = coeffL q d

/-- The list of -q^k. -/
def negMono : Nat → List Int
  | 0 => [-1]
  | k + 1 => 0 :: negMono k

/-- The list of 1 - q^k. For k = 0 this is the zero polynomial. -/
def oneMinus : Nat → List Int
  | 0 => []
  | k + 1 => 1 :: negMono k

/-- p^e. -/
def powL (p : List Int) : Nat → List Int
  | 0 => [1]
  | e + 1 => mulL p (powL p e)

/-- prod_{i=1}^{n} f(i). -/
def prodTo (f : Nat → List Int) : Nat → List Int
  | 0 => [1]
  | n + 1 => mulL (prodTo f n) (f (n + 1))

/-- Numerator of expression (2): prod_{i=1}^{n} (1 - q^(m+i))^(a_i). -/
def num (m n : Nat) (a : Nat → Nat) : List Int := prodTo (fun i => powL (oneMinus (m + i)) (a i)) n

/-- Denominator of expression (2): prod_{i=1}^{n} (1 - q^i)^(a_i). -/
def den (n : Nat) (a : Nat → Nat) : List Int := prodTo (fun i => powL (oneMinus i) (a i)) n

/-- "The expression (2) is a polynomial (in q)": the rational function num/den equals a
polynomial P, that is P * den = num. -/
def IsPolynomial (m n : Nat) (a : Nat → Nat) : Prop :=
  ∃ P : List Int, PolyEq (mulL P (den n a)) (num m n a)

/-- Conjecture 4 of the source. "Let m and n be given positive integers with m >= n, and let
(a_1, ..., a_n) be a sequence of non-negative integers. If the expression (2) is a polynomial
(in q) then it has non-negative coefficients." Only a 1, ..., a n enter `num` and `den`. By
`expression2_coefficients_unique` all P with P * den = num have the same coefficients. -/
def Conjecture4 : Prop :=
  ∀ (m n : Nat) (a : Nat → Nat), 1 ≤ m → 1 ≤ n → n ≤ m →
    ∀ P : List Int, PolyEq (mulL P (den n a)) (num m n a) → ∀ d : Nat, 0 ≤ coeffL P d

/-- The same with the sequence (a_1, ..., a_n) given as a list of length n. -/
def nthD : List Nat → Nat → Nat
  | [], _ => 0
  | a :: _, 0 => a
  | _ :: l, i + 1 => nthD l i

/-- a_i for the 1-based index i of the list (a_1, ..., a_n). -/
def aOf (l : List Nat) : Nat → Nat
  | 0 => 0
  | i + 1 => nthD l i

def Conjecture4List : Prop :=
  ∀ (m : Nat) (l : List Nat), 1 ≤ m → 1 ≤ l.length → l.length ≤ m →
    ∀ P : List Int, PolyEq (mulL P (den l.length (aOf l))) (num m l.length (aOf l)) →
      ∀ d : Nat, 0 ≤ coeffL P d

theorem conjecture4List_of_conjecture4 : Conjecture4 → Conjecture4List :=
  fun h m l hm hn hnm => h m l.length (aOf l) hm hn hnm

/-! ### The witness -/

/-- a_6 = 1, a_14 = a_18 = a_20 = 2, a_21 = 1, all other a_i = 0. -/
def aw : Nat → Nat
  | 6 => 1
  | 14 => 2
  | 18 => 2
  | 20 => 2
  | 21 => 1
  | _ => 0

/-- The same sequence as the list (a_1, ..., a_21). -/
def lw : List Nat := [0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 2, 0, 2, 1]

theorem lw_spec : lw.length = 21 ∧ ∀ i : Nat, i < 30 → aOf lw i = aw i := by decide +kernel

/-- The quotient, 177 coefficients, degree 176. -/
def Fw : List Int := [
  1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 2, 0, 0, 0, 3, 0, 4, 1, 0, 0, 3, 0, 4, 1, 2, 0, 3,
  0, 8, 1, 6, 2, 4, 0, 12, 3, 7, 4, 5, -1, 12, 3, 11, 4, 9, 1, 14, 3, 19, 8, 11, 5, 16, 2, 21,
  12, 13, 4, 18, 1, 22, 12, 21, 8, 20, 5, 26, 12, 25, 16, 20, 3, 27, 10, 24, 17, 24, 1, 26, 11,
  26, 18, 28, 9, 26, 9, 28, 18, 26, 11, 26, 1, 24, 17, 24, 10, 27, 3, 20, 16, 25, 12, 26, 5,
  20, 8, 21, 12, 22, 1, 18, 4, 13, 12, 21, 2, 16, 5, 11, 8, 19, 3, 14, 1, 9, 4, 11, 3, 12, -1,
  5, 4, 7, 3, 12, 0, 4, 2, 6, 1, 8, 0, 3, 0, 2, 1, 4, 0, 3, 0, 0, 1, 4, 0, 3, 0, 0, 0, 2, 0, 1,
  0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1]

/-- The hypotheses on (m, n, a): m = 22 and n = 21 are positive, m >= n (indeed m > n), and
a_21 = 1 is non-zero, so n = 21 is the true length of the sequence. -/
theorem witness_hypotheses : 1 ≤ 22 ∧ 1 ≤ 21 ∧ 21 ≤ 22 ∧ 21 < 22 ∧ aw 21 = 1 := by decide

/-- Exact division: Fw * prod (1 - q^i)^(a_i) = prod (1 - q^(22+i))^(a_i), as lists. -/
theorem witness_division : mulL Fw (den 21 aw) = num 22 21 aw := by decide +kernel

theorem witness_division_list : mulL Fw (den lw.length (aOf lw)) = num 22 lw.length (aOf lw) := by
  decide +kernel

/-- The same identity with the sequence padded by a_22 = 0 (n = 22 = m), so that the refutation
does not depend on reading n as the index of the last non-zero entry. -/
theorem witness_division_padded : aw 22 = 0 ∧ mulL Fw (den 22 aw) = num 22 22 aw := by
  decide +kernel

theorem witness_coeff_43 : coeffL Fw 43 = -1 := by decide +kernel

theorem witness_isPolynomial : IsPolynomial 22 21 aw :=
  ⟨Fw, fun d => by rw [witness_division]⟩

/-- Shape of the witness: 177 coefficients, leading coefficient 1 (degree 176), reciprocal,
value 1376 at q = 1, coefficient -1 at q^43 and q^133 and no other negative coefficient. -/
theorem witness_shape :
    Fw.length = 177 ∧ coeffL Fw 176 = 1 ∧ Fw.reverse = Fw ∧ Fw.foldl (· + ·) 0 = 1376 ∧
    coeffL Fw 43 = -1 ∧ coeffL Fw 133 = -1 ∧
    (∀ d : Nat, d < 177 → d ≠ 43 → d ≠ 133 → 0 ≤ coeffL Fw d) := by decide +kernel

/-- Degrees: the denominator has 132 coefficients (degree 131, leading coefficient 1 = (-1)^8) and
the numerator 308 (degree 307); 131 + 176 = 307. -/
theorem witness_degrees :
    (den 21 aw).length = 132 ∧ coeffL (den 21 aw) 131 = 1 ∧
    (num 22 21 aw).length = 308 ∧ coeffL (num 22 21 aw) 307 = 1 := by decide +kernel

/-- HEADLINE. Conjecture 4 of the source is false. -/
theorem not_conjecture4 : ¬ Conjecture4 := by
  intro h
  have h1 := h 22 21 aw (by decide) (by decide) (by decide) Fw
    (fun d => by rw [witness_division]) 43
  rw [witness_coeff_43] at h1
  exact absurd h1 (by decide)

/-- HEADLINE, list form. -/
theorem not_conjecture4List : ¬ Conjecture4List := by
  intro h
  have h1 := h 22 lw (by decide) (by decide) (by decide) Fw
    (fun d => by rw [witness_division_list]) 43
  rw [witness_coeff_43] at h1
  exact absurd h1 (by decide)

/-- The same with the witness displayed; the inequality m >= n holds strictly. -/
theorem conjecture4_counterexample :
    ∃ (m n : Nat) (a : Nat → Nat) (P : List Int) (d : Nat),
      1 ≤ n ∧ n < m ∧ PolyEq (mulL P (den n a)) (num m n a) ∧ coeffL P d < 0 :=
  ⟨22, 21, aw, Fw, 43, by decide, by decide, fun d => by rw [witness_division],
    by rw [witness_coeff_43]; decide⟩

/-- The witness is not a symmetric sequence, so Conjecture 3 of the source (symmetric sequences,
no condition m >= n) is not touched. -/
theorem aw_not_symmetric : ¬ (∀ i : Nat, 1 ≤ i → i ≤ 21 → aw i = aw (22 - i)) :=
  fun h => absurd (h 21 (by decide) (by decide)) (by decide)

/-! ### Coefficients: list multiplication is the Cauchy product -/

theorem coeffL_nil (d : Nat) : coeffL [] d = 0 := rfl
theorem coeffL_cons_zero (a : Int) (p : List Int) : coeffL (a :: p) 0 = a := rfl
theorem coeffL_cons_succ (a : Int) (p : List Int) (d : Nat) :
    coeffL (a :: p) (d + 1) = coeffL p d := rfl

theorem coeffL_addL : ∀ (p q : List Int) (d : Nat), coeffL (addL p q) d = coeffL p d + coeffL q d
  | [], q, d => by simp [addL, coeffL_nil]
  | a :: p, [], d => by simp [addL, coeffL_nil]
  | a :: p, b :: q, 0 => by simp [addL, coeffL_cons_zero]
  | a :: p, b :: q, d + 1 => by simp [addL, coeffL_cons_succ, coeffL_addL p q d]

theorem coeffL_smulL (c : Int) : ∀ (p : List Int) (d : Nat), coeffL (smulL c p) d = c * coeffL p d
  | [], d => by simp [smulL, coeffL_nil]
  | b :: q, 0 => by simp [smulL, coeffL_cons_zero]
  | b :: q, d + 1 => by simp [smulL, coeffL_cons_succ, coeffL_smulL c q d]

/-- sum_{i=0}^{d} f i. -/
def sumTo (f : Nat → Int) : Nat → Int
  | 0 => f 0
  | d + 1 => sumTo f d + f (d + 1)

/-- Coefficient of q^d in the product of two coefficient sequences: sum_{i=0}^{d} a_i b_{d-i}. -/
def mulCoeff (a b : Nat → Int) (d : Nat) : Int := sumTo (fun i => a i * b (d - i)) d

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

theorem coeffL_negMono_self : ∀ k : Nat, coeffL (negMono k) k = -1
  | 0 => rfl
  | k + 1 => coeffL_negMono_self k

theorem coeffL_negMono_ne : ∀ k d : Nat, d ≠ k → coeffL (negMono k) d = 0
  | 0, 0, h => absurd rfl h
  | 0, _ + 1, _ => rfl
  | _ + 1, 0, _ => rfl
  | k + 1, d + 1, h => coeffL_negMono_ne k d (fun e => h (by rw [e]))

/-- The list `oneMinus k` is 1 - q^k for k >= 1: coefficient -1 at degree k ... -/
theorem coeffL_oneMinus_self (k : Nat) (hk : 1 ≤ k) : coeffL (oneMinus k) k = -1 := by
  cases k with
  | zero => omega
  | succ k => exact coeffL_negMono_self k

/-- ... and 0 at every degree other than 0 and k (the constant term 1 is `coeffL_oneMinus_zero`). -/
theorem coeffL_oneMinus_ne (k d : Nat) (hk : 1 ≤ k) (h0 : d ≠ 0) (hd : d ≠ k) :
    coeffL (oneMinus k) d = 0 := by
  cases k with
  | zero => omega
  | succ k =>
    cases d with
    | zero => exact absurd rfl h0
    | succ d => exact coeffL_negMono_ne k d (fun e => hd (by rw [e]))

/-! ### Evaluation: the lists evaluate to the source's products at every integer -/

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

theorem evalL_mulL (x : Int) : ∀ p q : List Int, evalL (mulL p q) x = evalL p x * evalL q x
  | [], q => by simp [mulL, evalL]
  | a :: p, q => by
    show evalL (addL (smulL a q) (0 :: mulL p q)) x = (a + x * evalL p x) * evalL q x
    rw [evalL_addL, evalL_smulL]
    show a * evalL q x + (0 + x * evalL (mulL p q) x) = (a + x * evalL p x) * evalL q x
    rw [evalL_mulL x p q, Int.add_mul, Int.mul_assoc, Int.zero_add]

theorem evalL_negMono (x : Int) : ∀ k : Nat, evalL (negMono k) x = -(x ^ k)
  | 0 => by
    show (-1 : Int) + x * 0 = -(x ^ 0)
    rw [Int.mul_zero, Int.add_zero, Int.pow_zero]
  | k + 1 => by
    show 0 + x * evalL (negMono k) x = -(x ^ (k + 1))
    rw [evalL_negMono x k, Int.pow_succ, Int.zero_add, Int.mul_neg, Int.mul_comm]

/-- `oneMinus k` evaluates to 1 - x^k, for every k (including k = 0) and every integer x. -/
theorem evalL_oneMinus (x : Int) : ∀ k : Nat, evalL (oneMinus k) x = 1 - x ^ k
  | 0 => by
    show (0 : Int) = 1 - x ^ 0
    rw [Int.pow_zero]; rfl
  | k + 1 => by
    show 1 + x * evalL (negMono k) x = 1 - x ^ (k + 1)
    rw [evalL_negMono, Int.pow_succ, Int.mul_neg, Int.mul_comm, Int.sub_eq_add_neg]

theorem evalL_powL (p : List Int) (x : Int) : ∀ e : Nat, evalL (powL p e) x = evalL p x ^ e
  | 0 => by
    show (1 : Int) + x * 0 = evalL p x ^ 0
    rw [Int.mul_zero, Int.add_zero, Int.pow_zero]
  | e + 1 => by
    show evalL (mulL p (powL p e)) x = evalL p x ^ (e + 1)
    rw [evalL_mulL, evalL_powL p x e, Int.pow_succ, Int.mul_comm]

/-- prod_{i=1}^{n} f(i) over the integers. -/
def prodInt (f : Nat → Int) : Nat → Int
  | 0 => 1
  | n + 1 => prodInt f n * f (n + 1)

theorem evalL_prodTo (f : Nat → List Int) (x : Int) :
    ∀ n : Nat, evalL (prodTo f n) x = prodInt (fun i => evalL (f i) x) n
  | 0 => by
    show (1 : Int) + x * 0 = 1
    rw [Int.mul_zero, Int.add_zero]
  | n + 1 => by
    show evalL (mulL (prodTo f n) (f (n + 1))) x = prodInt (fun i => evalL (f i) x) n * evalL (f (n + 1)) x
    rw [evalL_mulL, evalL_prodTo f x n]

/-- The numerator list evaluates to prod_{i=1}^{n} (1 - x^(m+i))^(a_i) at every integer x. -/
theorem evalL_num (m n : Nat) (a : Nat → Nat) (x : Int) :
    evalL (num m n a) x = prodInt (fun i => (1 - x ^ (m + i)) ^ (a i)) n := by
  have e : (fun i => evalL (powL (oneMinus (m + i)) (a i)) x) =
      fun i => (1 - x ^ (m + i)) ^ (a i) := by
    funext i; rw [evalL_powL, evalL_oneMinus]
  show evalL (prodTo (fun i => powL (oneMinus (m + i)) (a i)) n) x = _
  rw [evalL_prodTo]
  show prodInt (fun i => evalL (powL (oneMinus (m + i)) (a i)) x) n = _
  rw [e]

/-- The denominator list evaluates to prod_{i=1}^{n} (1 - x^i)^(a_i) at every integer x. -/
theorem evalL_den (n : Nat) (a : Nat → Nat) (x : Int) :
    evalL (den n a) x = prodInt (fun i => (1 - x ^ i) ^ (a i)) n := by
  have e : (fun i => evalL (powL (oneMinus i) (a i)) x) = fun i => (1 - x ^ i) ^ (a i) := by
    funext i; rw [evalL_powL, evalL_oneMinus]
  show evalL (prodTo (fun i => powL (oneMinus i) (a i)) n) x = _
  rw [evalL_prodTo]
  show prodInt (fun i => evalL (powL (oneMinus i) (a i)) x) n = _
  rw [e]

theorem evalL_eq_zero (x : Int) : ∀ p : List Int, (∀ d, coeffL p d = 0) → evalL p x = 0
  | [], _ => rfl
  | a :: p, h => by
    have h0 : a = 0 := h 0
    have ht := evalL_eq_zero x p (fun d => h (d + 1))
    show a + x * evalL p x = 0
    rw [h0, ht, Int.mul_zero, Int.add_zero]

/-- Lists denoting the same polynomial have the same values. -/
theorem evalL_congr (x : Int) : ∀ p q : List Int, PolyEq p q → evalL p x = evalL q x
  | [], q, h => (evalL_eq_zero x q (fun d => (h d).symm)).symm
  | a :: p, [], h => evalL_eq_zero x (a :: p) (fun d => h d)
  | a :: p, b :: q, h => by
    have h0 : a = b := h 0
    have ht := evalL_congr x p q (fun d => h (d + 1))
    show a + x * evalL p x = b + x * evalL q x
    rw [h0, ht]

/-- For the witness: Fw(x) * prod (1 - x^i)^(a_i) = prod (1 - x^(22+i))^(a_i) at every integer x. -/
theorem witness_division_eval (x : Int) :
    evalL Fw x * prodInt (fun i => (1 - x ^ i) ^ (aw i)) 21 =
      prodInt (fun i => (1 - x ^ (22 + i)) ^ (aw i)) 21 := by
  rw [← evalL_den, ← evalL_num, ← evalL_mulL, witness_division]

/-! ### The quotient is unique, so "the coefficients of expression (2)" is well defined -/

theorem sumTo_congr (f g : Nat → Int) :
    ∀ n : Nat, (∀ i, i ≤ n → f i = g i) → sumTo f n = sumTo g n
  | 0, h => h 0 (Nat.le_refl 0)
  | n + 1, h => by
    show sumTo f n + f (n + 1) = sumTo g n + g (n + 1)
    rw [sumTo_congr f g n (fun i hi => h i (by omega)), h (n + 1) (Nat.le_refl _)]

theorem mulCoeff_succ (a b : Nat → Int) (d : Nat) :
    mulCoeff a b (d + 1) = sumTo (fun i => a i * b (d + 1 - i)) d + a (d + 1) * b 0 := by
  show sumTo (fun i => a i * b (d + 1 - i)) d + a (d + 1) * b (d + 1 - (d + 1)) = _
  rw [Nat.sub_self]

theorem quotient_unique_aux (a a' b : Nat → Int) (hb : b 0 = 1)
    (h : ∀ d, mulCoeff a b d = mulCoeff a' b d) : ∀ d i : Nat, i ≤ d → a i = a' i := by
  intro d
  induction d with
  | zero =>
    intro i hi
    have hi0 : i = 0 := by omega
    subst hi0
    have e := h 0
    have e' : a 0 * b 0 = a' 0 * b 0 := e
    rw [hb, Int.mul_one, Int.mul_one] at e'
    exact e'
  | succ d ih =>
    intro i hi
    by_cases hid : i ≤ d
    · exact ih i hid
    · have hi1 : i = d + 1 := by omega
      subst hi1
      have e := h (d + 1)
      have e1 : sumTo (fun i => a i * b (d + 1 - i)) d = sumTo (fun i => a' i * b (d + 1 - i)) d :=
        sumTo_congr _ _ d (fun i hi => by
          show a i * b (d + 1 - i) = a' i * b (d + 1 - i)
          rw [ih i hi])
      rw [mulCoeff_succ, mulCoeff_succ, e1, hb, Int.mul_one, Int.mul_one] at e
      exact Int.add_left_cancel e

/-- If D has constant term 1 and P * D = N = P' * D then P = P' (coefficientwise). -/
theorem quotient_unique (P P' D N : List Int) (hD : coeffL D 0 = 1)
    (h : PolyEq (mulL P D) N) (h' : PolyEq (mulL P' D) N) : PolyEq P P' := by
  intro d
  exact quotient_unique_aux (coeffL P) (coeffL P') (coeffL D) hD
    (fun e => by rw [← coeffL_mulL, ← coeffL_mulL, h e, h' e]) d d (Nat.le_refl d)

theorem coeffL_mulL_zero (p q : List Int) : coeffL (mulL p q) 0 = coeffL p 0 * coeffL q 0 := by
  rw [coeffL_mulL]; rfl

theorem coeffL_powL_zero (p : List Int) (hp : coeffL p 0 = 1) : ∀ e : Nat, coeffL (powL p e) 0 = 1
  | 0 => rfl
  | e + 1 => by
    show coeffL (mulL p (powL p e)) 0 = 1
    rw [coeffL_mulL_zero, hp, coeffL_powL_zero p hp e]; rfl

theorem coeffL_prodTo_zero (f : Nat → List Int) (hf : ∀ i, 1 ≤ i → coeffL (f i) 0 = 1) :
    ∀ n : Nat, coeffL (prodTo f n) 0 = 1
  | 0 => rfl
  | n + 1 => by
    show coeffL (mulL (prodTo f n) (f (n + 1))) 0 = 1
    rw [coeffL_mulL_zero, coeffL_prodTo_zero f hf n, hf (n + 1) (by omega)]; rfl

theorem coeffL_oneMinus_zero (k : Nat) (hk : 1 ≤ k) : coeffL (oneMinus k) 0 = 1 := by
  cases k with
  | zero => omega
  | succ k => rfl

/-- The denominator of expression (2) always has constant term 1. -/
theorem den_const (n : Nat) (a : Nat → Nat) : coeffL (den n a) 0 = 1 :=
  coeffL_prodTo_zero _ (fun i hi => coeffL_powL_zero _ (coeffL_oneMinus_zero i hi) (a i)) n

/-- For all parameters, two polynomials representing expression (2) have the same coefficients. -/
theorem expression2_coefficients_unique (m n : Nat) (a : Nat → Nat) (P P' : List Int)
    (h : PolyEq (mulL P (den n a)) (num m n a)) (h' : PolyEq (mulL P' (den n a)) (num m n a)) :
    PolyEq P P' :=
  quotient_unique P P' (den n a) (num m n a) (den_const n a) h h'

/-- Hence EVERY polynomial representing expression (2) at the witness has coefficient -1 at
q^43. -/
theorem witness_every_representative (P : List Int)
    (h : PolyEq (mulL P (den 21 aw)) (num 22 21 aw)) : coeffL P 43 = -1 := by
  rw [expression2_coefficients_unique 22 21 aw P Fw h (fun d => by rw [witness_division]) 43]
  exact witness_coeff_43

/-! ### Sanity checks of the definitions -/

/-- A Gaussian polynomial: n = 2, m = 2, a = (1, 1) gives (1-q^3)(1-q^4)/((1-q)(1-q^2)) =
1 + q + 2q^2 + q^3 + q^4, the q-binomial coefficient [4 choose 2]. -/
theorem sanity_gaussian : mulL [1, 1, 2, 1, 1] (den 2 (fun _ => 1)) = num 2 2 (fun _ => 1) := by
  decide +kernel

/-- The source's own example after Conjecture 4 (attributed there to Stanton): m = 1 and
(a_1, ..., a_17) = (1,3,1,1,1,1,1,1,2,1,1,1,1,1,1,1,1), "where (2) is a polynomial that contains the
term -q^7". The definitions above reproduce it. Here m = 1 < n = 17, so it is NOT a counterexample
to Conjecture 4; it is why the source imposes m >= n. -/
def lStanton : List Nat := [1, 3, 1, 1, 1, 1, 1, 1, 2, 1, 1, 1, 1, 1, 1, 1, 1]

theorem sanity_source_example :
    lStanton.length = 17 ∧
    mulL [1, 1, 3, 1, 4, 0, 5, -1, 6, -1, 7, -1, 6, -1, 5, 0, 4, 1, 3, 1, 1]
      (den 17 (aOf lStanton)) = num 1 17 (aOf lStanton) ∧
    coeffL [1, 1, 3, 1, 4, 0, 5, -1, 6, -1, 7, -1, 6, -1, 5, 0, 4, 1, 3, 1, 1] 7 = -1 := by
  decide +kernel

/-- The hypothesis "expression (2) is a polynomial" is not always true: for n = 2, m = 3,
a = (0, 1) the expression is (1 - q^5)/(1 - q^2), which is not a polynomial (at x = -1 the
denominator vanishes and the numerator is 2). -/
theorem sanity_not_polynomial : ¬ IsPolynomial 3 2 (fun i => if i = 2 then 1 else 0) := by
  intro ⟨P, hP⟩
  have e := evalL_congr (-1) _ _ hP
  rw [evalL_mulL] at e
  have hd : evalL (den 2 (fun i => if i = 2 then 1 else 0)) (-1) = 0 := by decide +kernel
  have hn : evalL (num 3 2 (fun i => if i = 2 then 1 else 0)) (-1) = 2 := by decide +kernel
  rw [hd, hn, Int.mul_zero] at e
  exact absurd e (by decide)

end FakeGaussian

#print axioms FakeGaussian.not_conjecture4
#print axioms FakeGaussian.not_conjecture4List
#print axioms FakeGaussian.conjecture4_counterexample
#print axioms FakeGaussian.witness_division
#print axioms FakeGaussian.witness_division_list
#print axioms FakeGaussian.witness_division_padded
#print axioms FakeGaussian.witness_coeff_43
#print axioms FakeGaussian.witness_isPolynomial
#print axioms FakeGaussian.witness_hypotheses
#print axioms FakeGaussian.witness_shape
#print axioms FakeGaussian.witness_degrees
#print axioms FakeGaussian.witness_every_representative
#print axioms FakeGaussian.witness_division_eval
#print axioms FakeGaussian.lw_spec
#print axioms FakeGaussian.aw_not_symmetric
#print axioms FakeGaussian.conjecture4List_of_conjecture4
#print axioms FakeGaussian.coeffL_mulL
#print axioms FakeGaussian.coeffL_oneMinus_self
#print axioms FakeGaussian.coeffL_oneMinus_ne
#print axioms FakeGaussian.coeffL_oneMinus_zero
#print axioms FakeGaussian.evalL_mulL
#print axioms FakeGaussian.evalL_num
#print axioms FakeGaussian.evalL_den
#print axioms FakeGaussian.expression2_coefficients_unique
#print axioms FakeGaussian.den_const
#print axioms FakeGaussian.sanity_gaussian
#print axioms FakeGaussian.sanity_source_example
#print axioms FakeGaussian.sanity_not_polynomial
