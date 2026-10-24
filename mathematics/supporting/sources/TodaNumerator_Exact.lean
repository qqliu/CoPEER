/-
  TodaNumerator.lean  --  census rank 11, record rx_algebra_toda_numerator_unimodality
  (version 2; version 1 is kept beside this file as TodaNumerator.v1.lean.  The work was interrupted
  and resumed by a second agent, who added sections 9 and 10 and this header; sections 1 to 8 are
  unchanged from version 1.)

  Source: A. Labelle, "On a specialization of Toda eigenfunctions", arXiv:2502.10655v3,
  Definition 1.1 (fermionic recursion (1)), Theorem 1.1, Conjecture 7.3:
      "The polynomial (q)_alpha^2 J_alpha is unimodal."

  READ THIS FIRST.  The RECORDED witness (B_3, alpha = alpha_1 + alpha_2, numerator 1 + q^2) refutes
  only the literal reading "unimodal in consecutive powers of q, zero coefficients included".  It is the
  type A_2 numerator 1 + q of the source's own Example 1.1 with q replaced by q^2, because alpha sits on
  the two long simple roots (`recorded_witness_is_A2_in_q_squared`); in t = q^2 it is unimodal.  The
  refutation that survives every regrading uses a SECOND witness (B_2, alpha = 2 alpha_1 + 2 alpha_2),
  which was found by the census agent during this formalisation and is NOT part of the recorded model
  discovery.

  What is certified here (core Lean 4, no Mathlib, no axioms beyond the three standard ones):

  * general definitions: a Gram matrix of simple roots (`Admissible`), the q-factorial (q)_gamma with
    the source's exponents d_i * j, the energy (beta,beta)/2, the rational functions J_alpha as
    power series modulo q^(N+1) (the ring Z[q]/(q^(N+1)), in which every 1 - q^k, k >= 1, is a unit),
    the numerator H_alpha = (q)_alpha^2 J_alpha and its coefficients `Hc G a i`;
  * the conjecture as ONE general proposition in four forms:
      `Conjecture73`           unimodal in consecutive powers of q (the literal reading),
      `Conjecture73_regraded`  unimodal in powers of q^e for some e >= 1 (any regrading),
      `Conjecture73_relational` the regraded reading over EVERY family solving the source's
                               equation (1) modulo q^(N+1), with no reference to the implementation,
      `Conjecture73_simplyLaced` (stated only; NOT refuted here);
  * `not_conjecture73`            via the RECORDED witness: B_3, alpha = alpha_1 + alpha_2, H = 1 + q^2;
  * `not_conjecture73_regraded`, `not_conjecture73_relational`   via the SECOND witness:
      B_2, alpha = 2 alpha_1 + 2 alpha_2, H = 1 + q + 3q^2 + 2q^3 + 5q^4 + 2q^5 + 3q^6 + q^7 + q^8,
      whose coefficients 3 > 2 < 5 sit at consecutive exponents with every coefficient positive;
  * a third witness inside the recorded root system: B_3, alpha = 2 alpha_1 + alpha_2 + alpha_3,
      H = 1 + 2q + 4q^2 + 3q^3 + 4q^4 + 2q^5 + q^6 (`not_conjecture73_regraded_via_b3`);
  * positive controls: the definitions reproduce the source's printed Examples 1.1 and 1.3 (type A);
  * instance certificates that the computed families satisfy the source's equation (1) LITERALLY
    modulo q^(N+1), with every inverse 1/(q)_gamma checked by multiplying back;
  * (section 9, general theorem) `eq1_unique`: equation (1) modulo q^(N+1) with J_0 = 1 has AT MOST ONE
    solution on the box, for every Gram matrix, order and vector with positive energies;
  * (section 10) `b2_every_solution`, `b3_every_solution`, `b3_211_every_solution`: the numerator of
    EVERY family solving equation (1) modulo q^13 at the three witnesses is the displayed one, and
    `b2_every_solution_not_regraded`: none of them is unimodal under any regrading.

  NOT certified in Lean (the reader supplies it; see BINDING.md):

  * the step from the source's J_alpha in Q(q) to power series: J_alpha has no pole at q = 0 (its
    denominators are products of 1 - q^k, k >= 1), and reduction modulo q^(N+1) is a ring homomorphism,
    so the reductions of the source's J_beta form a family satisfying `SatisfiesEq1`.  GIVEN that,
    `eq1_unique` identifies them with the computed family, so the certified lists are the first
    thirteen coefficients of the source's numerators;
  * `Conjecture73` and `Conjecture73_regraded` are stated through `Hc`, that is through the memoised
    implementation `Jfam` of equation (2); that `Hc G a i` is the i-th coefficient of the source's
    numerator for EVERY admissible G and a is a matter of reading the definitions (at the witnesses it
    is backed by the certificates above).  `Conjecture73_relational` does not mention `Jfam`;
  * the identification of `Admissible` + `IsRootSystem` data with split semisimple Lie algebras;
  * Theorem 1.1 of the source (that H is a polynomial): not needed, the valleys sit at exponents <= 4.

  NOT refuted here: the conjecture restricted to simply laced types (`Conjecture73_simplyLaced`), and a
  class-wise repair (`Conjecture73_classwise`: unimodal along each residue class of exponents modulo
  the largest d_i), which the second witness satisfies on its support (`b2_residue_classes`).  Neither
  restriction is in the source's text.  See BINDING.md.
-/
set_option maxRecDepth 100000

namespace Toda

/-! ## 1. Truncated power series: the ring Z[q]/(q^(N+1)) -/

/-- Coefficient lists; index = exponent of q. -/
abbrev Poly := List Int

def coeff (p : Poly) (n : Nat) : Int := p.getD n 0

/-- `sumTo n f = f 0 + f 1 + ... + f n`. -/
def sumTo (n : Nat) (f : Nat → Int) : Int :=
  (List.range (n + 1)).foldl (fun acc i => acc + f i) 0

/-- The element of Z[q]/(q^(N+1)) with coefficients `f 0, ..., f N`. -/
def tab (N : Nat) (f : Nat → Int) : Poly := (List.range (N + 1)).map f

def zeroT (N : Nat) : Poly := tab N (fun _ => 0)
def oneT (N : Nat) : Poly := tab N (fun n => if n = 0 then 1 else 0)
/-- q^e modulo q^(N+1). -/
def monoT (N e : Nat) : Poly := tab N (fun n => if n = e then 1 else 0)
def addT (N : Nat) (p r : Poly) : Poly := tab N (fun n => coeff p n + coeff r n)
/-- Cauchy product modulo q^(N+1). -/
def mulT (N : Nat) (p r : Poly) : Poly :=
  tab N (fun n => sumTo n (fun i => coeff p i * coeff r (n - i)))
/-- 1 - q^k modulo q^(N+1). -/
def oneMinusT (N k : Nat) : Poly :=
  tab N (fun n => (if n = 0 then 1 else 0) - (if n = k then 1 else 0))
/-- 1 + q^k + q^(2k) + ... modulo q^(N+1): the inverse of 1 - q^k for k >= 1. -/
def geomT (N k : Nat) : Poly := tab N (fun n => if n % k = 0 then 1 else 0)

def prodT (N : Nat) (l : List Poly) : Poly := l.foldl (mulT N) (oneT N)
def sumPolys (N : Nat) (l : List Poly) : Poly := l.foldl (addT N) (zeroT N)

/-- The computational table really has the stated coefficients. -/
theorem coeff_tab (N n : Nat) (f : Nat → Int) (h : n ≤ N) : coeff (tab N f) n = f n := by
  simp [coeff, tab, List.getD_eq_getElem?_getD, Nat.lt_succ_of_le h]

/-- Coefficient n of a product is the Cauchy sum. -/
theorem coeff_mulT (N n : Nat) (p r : Poly) (h : n ≤ N) :
    coeff (mulT N p r) n = sumTo n (fun i => coeff p i * coeff r (n - i)) :=
  coeff_tab N n _ h

theorem coeff_addT (N n : Nat) (p r : Poly) (h : n ≤ N) :
    coeff (addT N p r) n = coeff p n + coeff r n :=
  coeff_tab N n _ h

/-! ## 2. Root data: the Gram matrix of the simple roots -/

abbrev Gram := List (List Int)

/-- (alpha_i, alpha_j). -/
def entry (G : Gram) (i j : Nat) : Int := (G.getD i []).getD j 0

def dot : List Int → List Int → Int
  | x :: xs, y :: ys => x * y + dot xs ys
  | _, _ => 0

/-- (beta, beta) for beta = sum x_i alpha_i. -/
def quad (G : Gram) (x : List Int) : Int := dot x (G.map (fun row => dot row x))

/-- (beta, beta)/2 for beta = sum b_i alpha_i with b_i in N. -/
def energy (G : Gram) (b : List Nat) : Nat := (quad G (b.map Int.ofNat) / 2).toNat

/-- d_i = (alpha_i, alpha_i)/2. -/
def dvec (G : Gram) : List Nat :=
  (List.range G.length).map (fun i => (entry G i i / 2).toNat)

/-- Nodes i and j lie in the same connected component of the Dynkin diagram. -/
inductive Conn (G : Gram) : Nat → Nat → Prop
  | refl (i : Nat) : Conn G i i
  | step {i j k : Nat} : entry G i j ≠ 0 → Conn G j k → Conn G i k

/-- `G` is the Gram matrix of the simple roots of a finite reduced crystallographic root system,
    with the invariant form normalised so that short roots have squared length 2 in every
    irreducible component: symmetric, even positive diagonal, non-positive off-diagonal entries with
    integral Cartan numbers 2(alpha_i,alpha_j)/(alpha_i,alpha_i), positive definite, and in each
    component the shortest simple root has squared length 2. -/
structure Admissible (G : Gram) : Prop where
  square : ∀ row ∈ G, row.length = G.length
  symm : ∀ i, i < G.length → ∀ j, j < G.length → entry G i j = entry G j i
  diag : ∀ i, i < G.length → 0 < entry G i i ∧ entry G i i % 2 = 0
  cartan : ∀ i, i < G.length → ∀ j, j < G.length → i ≠ j →
    entry G i j ≤ 0 ∧ (2 * entry G i j) % entry G i i = 0
  posdef : ∀ x : List Int, x.length = G.length → (∃ i, x.getD i 0 ≠ 0) → 0 < quad G x
  normalized : ∀ i, i < G.length →
    2 ≤ entry G i i ∧ ∃ j, j < G.length ∧ Conn G i j ∧ entry G j j = 2

/-- Simply laced: every d_i = 1. -/
def SimplyLaced (G : Gram) : Prop := ∀ i, i < G.length → entry G i i = 2

/-- (x, y) for vectors given in simple-root coordinates. -/
def bil (G : Gram) (x y : List Int) : Int := dot x (G.map (fun row => dot row y))

/-- The reflection s_gamma(beta) = beta - (2(beta,gamma)/(gamma,gamma)) gamma, in simple-root coordinates. -/
def reflect (G : Gram) (γ β : List Int) : List Int :=
  List.zipWith (fun b c => b - (2 * bil G β γ / bil G γ γ) * c) β γ

/-- The i-th simple root in simple-root coordinates. -/
def unitVec (n i : Nat) : List Int := (List.range n).map (fun j => if j = i then 1 else 0)

/-- `R` lists, in simple-root coordinates, a finite reduced crystallographic root system of which the
    coordinate vectors are a base, with Gram matrix `G`, and no root is shorter than squared length 2:
    it contains the simple roots, is closed under every reflection s_gamma (gamma in R) with integral
    Cartan numbers, contains no multiples of a root other than plus or minus itself, and every root
    has all coordinates >= 0 or all coordinates <= 0. -/
structure IsRootSystem (G : Gram) (R : List (List Int)) : Prop where
  simple : ∀ i, i < G.length → unitVec G.length i ∈ R
  dims : ∀ β ∈ R, β.length = G.length
  positive : ∀ β ∈ R, 2 ≤ bil G β β
  integral : ∀ β ∈ R, ∀ γ ∈ R, (2 * bil G β γ) % bil G γ γ = 0
  closed : ∀ β ∈ R, ∀ γ ∈ R, reflect G γ β ∈ R
  reduced : ∀ β ∈ R, ∀ γ ∈ R,
    (∀ i, i < G.length → ∀ j, j < G.length → β.getD i 0 * γ.getD j 0 = β.getD j 0 * γ.getD i 0) →
      γ = β ∨ γ = β.map (fun c => -c)
  base : ∀ β ∈ R, (∀ c ∈ β, 0 ≤ c) ∨ (∀ c ∈ β, c ≤ 0)

/-! ## 3. The source's objects -/

/-- The exponents d_i * j, 1 <= j <= gamma_i, of the factors of (q)_gamma. -/
def qfacExponents (d γ : List Nat) : List Nat :=
  (List.zip d γ).flatMap (fun p => (List.range p.2).map (fun j => p.1 * (j + 1)))

/-- (q)_gamma = prod_i prod_{j=1}^{gamma_i} (1 - q^(d_i j)), modulo q^(N+1). -/
def qfacT (N : Nat) (d γ : List Nat) : Poly := prodT N ((qfacExponents d γ).map (oneMinusT N))

/-- 1/(q)_gamma modulo q^(N+1), as a product of geometric series. -/
def invQfacT (N : Nat) (d γ : List Nat) : Poly := prodT N ((qfacExponents d γ).map (geomT N))

/-- All b with 0 <= b <= a coordinatewise, in lexicographic order (a linear extension of <=). -/
def box : List Nat → List (List Nat)
  | [] => [[]]
  | x :: xs => (List.range (x + 1)).flatMap (fun k => (box xs).map (fun t => k :: t))

/-- Coordinatewise order on vectors of equal length: 0 <= b <= a. -/
inductive VLe : List Nat → List Nat → Prop
  | nil : VLe [] []
  | cons {x y : Nat} {xs ys : List Nat} : x ≤ y → VLe xs ys → VLe (x :: xs) (y :: ys)

/-- `box a` is exactly the interval {b : 0 <= b <= a} of the source's sums. -/
theorem mem_box (a : List Nat) : ∀ b, b ∈ box a ↔ VLe b a := by
  induction a with
  | nil =>
    intro b
    simp only [box, List.mem_singleton]
    constructor
    · intro h; subst h; exact VLe.nil
    · intro h; cases h; rfl
  | cons x xs ih =>
    intro b
    simp only [box, List.mem_flatMap, List.mem_range, List.mem_map]
    constructor
    · intro ⟨k, hk, t, ht, hb⟩
      subst hb
      exact VLe.cons (by omega) ((ih t).mp ht)
    · intro h
      cases h with
      | cons hxy hrest => exact ⟨_, by omega, _, (ih _).mpr hrest, rfl⟩

def vsub (b c : List Nat) : List Nat := List.zipWith (fun x y => x - y) b c
def isZero (b : List Nat) : Bool := b.all (fun x => x == 0)

/-- One summand of the fermionic recursion: q^((beta,beta)/2) J_beta / (q)_(alpha - beta). -/
def summand (N : Nat) (G : Gram) (J : List Nat → Poly) (b c : List Nat) : Poly :=
  mulT N (monoT N (energy G c)) (mulT N (invQfacT N (dvec G) (vsub b c)) (J c))

/-- Right-hand side of the source's equation (1): the sum over ALL 0 <= beta <= alpha. -/
def rhs1 (N : Nat) (G : Gram) (J : List Nat → Poly) (b : List Nat) : Poly :=
  sumPolys N ((box b).map (summand N G J b))

/-- The sum in the source's equation (2): over 0 <= beta < alpha. -/
def rhs2 (N : Nat) (G : Gram) (J : List Nat → Poly) (b : List Nat) : Poly :=
  sumPolys N (((box b).filter (fun c => c != b)).map (summand N G J b))

def lookupJ (tbl : List (List Nat × Poly)) (c : List Nat) : Poly := (tbl.lookup c).getD []

/-- Equation (2): J_b = (1 - q^((b,b)/2))^(-1) * rhs2, with J_0 = 1; memoised. -/
def stepJ (N : Nat) (G : Gram) (tbl : List (List Nat × Poly)) (b : List Nat) :
    List (List Nat × Poly) :=
  tbl ++ [(b, if isZero b then oneT N
              else mulT N (geomT N (energy G b)) (rhs2 N G (lookupJ tbl) b))]

def Jtable (N : Nat) (G : Gram) (a : List Nat) : List (List Nat × Poly) :=
  (box a).foldl (stepJ N G) []

/-- The family b |-> J_b modulo q^(N+1), for 0 <= b <= a. -/
def Jfam (N : Nat) (G : Gram) (a : List Nat) : List Nat → Poly := lookupJ (Jtable N G a)

/-- (q)_a^2 J_a modulo q^(N+1), for ANY family J. -/
def numerator (N : Nat) (G : Gram) (a : List Nat) (J : List Nat → Poly) : Poly :=
  mulT N (mulT N (qfacT N (dvec G) a) (qfacT N (dvec G) a)) (J a)

/-- (q)_a^2 J_a modulo q^(N+1), for the computed family. -/
def Htr (N : Nat) (G : Gram) (a : List Nat) : Poly := numerator N G a (Jfam N G a)

/-- The coefficient of q^i in the numerator H_a = (q)_a^2 J_a. -/
def Hc (G : Gram) (a : List Nat) (i : Nat) : Int := coeff (Htr i G a) i

/-- A family satisfies the source's equation (1) literally, modulo q^(N+1), with J_0 = 1. -/
def SatisfiesEq1 (N : Nat) (G : Gram) (a : List Nat) (J : List Nat → Poly) : Prop :=
  J (a.map (fun _ => 0)) = oneT N ∧ ∀ b ∈ box a, J b = rhs1 N G J b

/-- Every 1/(q)_gamma used is a genuine inverse modulo q^(N+1). -/
def InversesOK (N : Nat) (G : Gram) (a : List Nat) : Prop :=
  ∀ γ ∈ box a, mulT N (qfacT N (dvec G) γ) (invQfacT N (dvec G) γ) = oneT N

/-! ## 4. Unimodality and the conjecture -/

/-- Unimodal in consecutive exponents (zero coefficients included): some peak k separates weak
    increase from weak decrease. -/
def UnimodalSeq (h : Nat → Int) : Prop :=
  ∃ k, (∀ i, i < k → h i ≤ h (i + 1)) ∧ (∀ i, k ≤ i → h (i + 1) ≤ h i)

/-- Unimodal after some regrading t = q^e: all nonzero coefficients sit at multiples of e and the
    sequence of coefficients of t^m is unimodal. -/
def RegradedUnimodal (h : Nat → Int) : Prop :=
  ∃ e, 0 < e ∧ (∀ i, h i ≠ 0 → e ∣ i) ∧ UnimodalSeq (fun m => h (e * m))

theorem regraded_of_unimodal (h : Nat → Int) (hu : UnimodalSeq h) : RegradedUnimodal h := by
  refine ⟨1, Nat.one_pos, fun i _ => Nat.one_dvd i, ?_⟩
  have : (fun m => h (1 * m)) = h := by funext m; rw [Nat.one_mul]
  rw [this]; exact hu

/-- A strict valley at three consecutive exponents excludes unimodality. -/
theorem not_unimodal_of_valley (h : Nat → Int) (j : Nat)
    (h1 : h (j + 1) < h j) (h2 : h (j + 1) < h (j + 2)) : ¬ UnimodalSeq h := by
  intro ⟨k, inc, dec⟩
  by_cases hk : k ≤ j + 1
  · have hd : h (j + 2) ≤ h (j + 1) := dec (j + 1) hk
    omega
  · have := inc j (by omega)
    omega

/-- A valley at consecutive exponents together with a nonzero coefficient of q^1 excludes every
    regraded reading. -/
theorem not_regraded_of_valley (h : Nat → Int) (j : Nat) (hq : h 1 ≠ 0)
    (h1 : h (j + 1) < h j) (h2 : h (j + 1) < h (j + 2)) : ¬ RegradedUnimodal h := by
  intro ⟨e, _, hdiv, hu⟩
  have he : e = 1 := Nat.dvd_one.mp (hdiv 1 hq)
  subst he
  have : (fun m => h (1 * m)) = h := by funext m; rw [Nat.one_mul]
  rw [this] at hu
  exact not_unimodal_of_valley h j h1 h2 hu

/-- Conjecture 7.3, literal reading: for every admissible root datum and every alpha in Q_{>=0},
    the numerator (q)_alpha^2 J_alpha is unimodal. -/
def Conjecture73 : Prop :=
  ∀ (G : Gram) (R : List (List Int)) (a : List Nat),
    Admissible G → IsRootSystem G R → a.length = G.length → UnimodalSeq (Hc G a)

/-- Conjecture 7.3 under the most generous grading convention. -/
def Conjecture73_regraded : Prop :=
  ∀ (G : Gram) (R : List (List Int)) (a : List Nat),
    Admissible G → IsRootSystem G R → a.length = G.length → RegradedUnimodal (Hc G a)

/-- Conjecture 7.3 restricted to simply laced root data.  Stated for the record; NOT refuted here. -/
def Conjecture73_simplyLaced : Prop :=
  ∀ (G : Gram) (R : List (List Int)) (a : List Nat),
    Admissible G → IsRootSystem G R → SimplyLaced G → a.length = G.length → UnimodalSeq (Hc G a)

/-- Truncated form of `RegradedUnimodal`: up to order N, nonzero coefficients sit at multiples of e
    and the coefficients of t^m = q^(e m) rise weakly up to m = k and fall weakly afterwards. -/
def TruncRegradedUnimodal (N k e : Nat) (p : Poly) : Prop :=
  (∀ i, i ≤ N → coeff p i ≠ 0 → e ∣ i) ∧
  (∀ m, m < k → e * (m + 1) ≤ N → coeff p (e * m) ≤ coeff p (e * (m + 1))) ∧
  (∀ m, k ≤ m → e * (m + 1) ≤ N → coeff p (e * (m + 1)) ≤ coeff p (e * m))

/-- Conjecture 7.3 in RELATIONAL form, independent of the memoised implementation `Jfam`:
    for every admissible datum there are a regrading e and a peak k such that EVERY family solving
    the source's equation (1) modulo q^(N+1) (with J_0 = 1 and genuine inverses) has a numerator
    that is unimodal in t = q^e with peak k up to order N, for every N.
    With e = 1 this is the literal reading, so this is the most generous form. -/
def Conjecture73_relational : Prop :=
  ∀ (G : Gram) (R : List (List Int)) (a : List Nat),
    Admissible G → IsRootSystem G R → a.length = G.length →
      ∃ e k, 0 < e ∧ ∀ (N : Nat) (J : List Nat → Poly),
        SatisfiesEq1 N G a J → InversesOK N G a → TruncRegradedUnimodal N k e (numerator N G a J)

theorem conjecture73_imp_regraded : Conjecture73 → Conjecture73_regraded :=
  fun h G R a hG hR ha => regraded_of_unimodal _ (h G R a hG hR ha)

theorem conjecture73_imp_simplyLaced : Conjecture73 → Conjecture73_simplyLaced :=
  fun h G R a hG hR _ ha => h G R a hG hR ha

/-! ## 5. The two root data -/

/-- B_3, simple roots e1-e2, e2-e3, e3 with (x,y) = 2 x.y: short roots have squared length 2. -/
def B3 : Gram := [[4, -2, 0], [-2, 4, -2], [0, -2, 2]]

/-- B_2 (= C_2), long simple root first: (4, -2; -2, 2). -/
def B2 : Gram := [[4, -2], [-2, 2]]

theorem sq_nonneg (a : Int) : 0 ≤ a * a := by
  rcases Int.le_total 0 a with h | h
  · exact Int.mul_nonneg h h
  · have h0 : 0 ≤ -a := by omega
    have h2 := Int.mul_nonneg h0 h0
    rw [Int.neg_mul_neg] at h2
    exact h2

theorem eq_zero_of_sq (a : Int) (h : a * a = 0) : a = 0 := by
  rcases Int.mul_eq_zero.mp h with h | h <;> exact h

theorem b2_quad (x0 x1 : Int) :
    quad B2 [x0, x1] = (2 * x0 - x1) * (2 * x0 - x1) + x1 * x1 := by
  simp [quad, dot, B2]; grind

theorem b3_quad (x0 x1 x2 : Int) :
    quad B3 [x0, x1, x2]
      = (2 * x0 - x1) * (2 * x0 - x1) + x1 * x1 + 2 * ((x1 - x2) * (x1 - x2)) := by
  simp [quad, dot, B3]; grind

theorem b2_posdef (x : List Int) (hx : x.length = 2) (hne : ∃ i, x.getD i 0 ≠ 0) :
    0 < quad B2 x := by
  match x, hx with
  | [x0, x1], _ =>
    rw [b2_quad]
    have s1 := sq_nonneg (2 * x0 - x1)
    have s2 := sq_nonneg x1
    apply Int.lt_of_not_ge
    intro hle
    have z2 : x1 = 0 := eq_zero_of_sq x1 (by omega)
    have z1 : 2 * x0 - x1 = 0 := eq_zero_of_sq _ (by omega)
    obtain ⟨i, hi⟩ := hne
    match i with
    | 0 => simp at hi; omega
    | 1 => simp at hi; omega
    | (k + 2) => simp at hi

theorem b3_posdef (x : List Int) (hx : x.length = 3) (hne : ∃ i, x.getD i 0 ≠ 0) :
    0 < quad B3 x := by
  match x, hx with
  | [x0, x1, x2], _ =>
    rw [b3_quad]
    have s1 := sq_nonneg (2 * x0 - x1)
    have s2 := sq_nonneg x1
    have s3 := sq_nonneg (x1 - x2)
    apply Int.lt_of_not_ge
    intro hle
    have z2 : x1 = 0 := eq_zero_of_sq x1 (by omega)
    have z1 : 2 * x0 - x1 = 0 := eq_zero_of_sq _ (by omega)
    have z3 : x1 - x2 = 0 := eq_zero_of_sq _ (by omega)
    obtain ⟨i, hi⟩ := hne
    match i with
    | 0 => simp at hi; omega
    | 1 => simp at hi; omega
    | 2 => simp at hi; omega
    | (k + 3) => simp at hi

theorem b2_admissible : Admissible B2 where
  square := by decide
  symm := by decide
  diag := by decide
  cartan := by decide
  posdef := b2_posdef
  normalized := by
    intro i hi
    have hi' : i < 2 := hi
    match i, hi' with
    | 0, _ => exact ⟨by decide, 1, by decide, Conn.step (j := 1) (by decide) (Conn.refl 1), by decide⟩
    | 1, _ => exact ⟨by decide, 1, by decide, Conn.refl 1, by decide⟩

theorem b3_admissible : Admissible B3 where
  square := by decide
  symm := by decide
  diag := by decide
  cartan := by decide
  posdef := b3_posdef
  normalized := by
    intro i hi
    have hi' : i < 3 := hi
    match i, hi' with
    | 0, _ =>
      exact ⟨by decide, 2, by decide,
        Conn.step (j := 1) (by decide) (Conn.step (j := 2) (by decide) (Conn.refl 2)), by decide⟩
    | 1, _ => exact ⟨by decide, 2, by decide, Conn.step (j := 2) (by decide) (Conn.refl 2), by decide⟩
    | 2, _ => exact ⟨by decide, 2, by decide, Conn.refl 2, by decide⟩

/-- The 18 roots of B_3 in simple-root coordinates (e1-e2, e2-e3, e3). -/
def B3pos : List (List Int) :=
  [[1, 0, 0], [0, 1, 0], [0, 0, 1], [1, 1, 0], [0, 1, 1], [1, 1, 1], [0, 1, 2], [1, 1, 2], [1, 2, 2]]
def B3roots : List (List Int) := B3pos ++ B3pos.map (fun β => β.map (fun c => -c))

/-- The 8 roots of B_2 in simple-root coordinates (long simple root first). -/
def B2pos : List (List Int) := [[1, 0], [0, 1], [1, 1], [1, 2]]
def B2roots : List (List Int) := B2pos ++ B2pos.map (fun β => β.map (fun c => -c))

theorem b3_rootSystem : IsRootSystem B3 B3roots where
  simple := by decide +kernel
  dims := by decide +kernel
  positive := by decide +kernel
  integral := by decide +kernel
  closed := by decide +kernel
  reduced := by decide +kernel
  base := by decide +kernel

theorem b2_rootSystem : IsRootSystem B2 B2roots where
  simple := by decide +kernel
  dims := by decide +kernel
  positive := by decide +kernel
  integral := by decide +kernel
  closed := by decide +kernel
  reduced := by decide +kernel
  base := by decide +kernel

/-- Squared lengths: B_3 has 6 short roots of squared length 2 and 12 long roots of squared length 4;
    B_2 has 4 and 4. -/
theorem b3_lengths :
    B3roots.map (fun β => bil B3 β β) = [4, 4, 2, 4, 2, 2, 4, 4, 4, 4, 4, 2, 4, 2, 2, 4, 4, 4] := by
  decide +kernel
theorem b2_lengths : B2roots.map (fun β => bil B2 β β) = [4, 2, 2, 4, 4, 2, 2, 4] := by
  decide +kernel

theorem b3_box : box [1, 1, 0] = [[0, 0, 0], [0, 1, 0], [1, 0, 0], [1, 1, 0]] := by decide +kernel
theorem b2_box :
    box [2, 2] = [[0, 0], [0, 1], [0, 2], [1, 0], [1, 1], [1, 2], [2, 0], [2, 1], [2, 2]] := by
  decide +kernel

/-! ## 6. Instance facts: the recorded witness B_3, alpha = alpha_1 + alpha_2 -/

theorem b3_d : dvec B3 = [2, 2, 1] := by decide +kernel
theorem b3_energies :
    (box [1, 1, 0]).map (energy B3) = [0, 2, 2, 2] := by decide +kernel

/-- H = 1 + q^2 to order q^12 (the source's Remark 4.1 gives degree 2). -/
theorem b3_H : Htr 12 B3 [1, 1, 0] = [1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0] := by decide +kernel

/-- J_(1,1,0) = (1 + q^2)/(1 - q^2)^4 to order q^12. -/
theorem b3_J :
    Jfam 12 B3 [1, 1, 0] [1, 1, 0]
      = mulT 12 [1, 0, 1] (prodT 12 [geomT 12 2, geomT 12 2, geomT 12 2, geomT 12 2]) := by
  decide +kernel

/-- The computed family satisfies the source's equation (1) literally, modulo q^13. -/
theorem b3_eq1 : SatisfiesEq1 12 B3 [1, 1, 0] (Jfam 12 B3 [1, 1, 0]) := by
  unfold SatisfiesEq1; decide +kernel

theorem b3_inverses : InversesOK 12 B3 [1, 1, 0] := by
  unfold InversesOK; decide +kernel

theorem b3_Hc : Hc B3 [1, 1, 0] 0 = 1 ∧ Hc B3 [1, 1, 0] 1 = 0 ∧ Hc B3 [1, 1, 0] 2 = 1 := by
  decide +kernel

/-- The recorded witness has the shape 1, 0, 1, 0, ..., 0: in t = q^2 it is 1 + t, which IS unimodal.
    It refutes only the literal reading. -/
theorem recorded_witness_is_regraded_shape :
    (List.range 13).map (Hc B3 [1, 1, 0]) = [1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0] := by
  decide +kernel

/-! ## 7. Instance facts: the second witness B_2, alpha = 2 alpha_1 + 2 alpha_2 -/

theorem b2_d : dvec B2 = [2, 1] := by decide +kernel
theorem b2_energies :
    (box [2, 2]).map (fun b => (b, energy B2 b))
      = [([0, 0], 0), ([0, 1], 1), ([0, 2], 4), ([1, 0], 2), ([1, 1], 1), ([1, 2], 2),
         ([2, 0], 8), ([2, 1], 5), ([2, 2], 4)] := by decide +kernel

/-- H = 1 + q + 3q^2 + 2q^3 + 5q^4 + 2q^5 + 3q^6 + q^7 + q^8 to order q^12
    (monic palindromic of degree 8, as the source's Remark 4.1 predicts). -/
theorem b2_H : Htr 12 B2 [2, 2] = [1, 1, 3, 2, 5, 2, 3, 1, 1, 0, 0, 0, 0] := by decide +kernel

theorem b2_eq1 : SatisfiesEq1 12 B2 [2, 2] (Jfam 12 B2 [2, 2]) := by
  unfold SatisfiesEq1; decide +kernel

theorem b2_inverses : InversesOK 12 B2 [2, 2] := by
  unfold InversesOK; decide +kernel

/-- The same family checked at the truncation orders that `Hc` uses. -/
theorem b2_eq1_low : ∀ N ∈ [1, 2, 3, 4],
    SatisfiesEq1 N B2 [2, 2] (Jfam N B2 [2, 2]) ∧ InversesOK N B2 [2, 2] := by
  unfold SatisfiesEq1 InversesOK; decide +kernel

theorem b3_eq1_low : ∀ N ∈ [0, 1, 2],
    SatisfiesEq1 N B3 [1, 1, 0] (Jfam N B3 [1, 1, 0]) ∧ InversesOK N B3 [1, 1, 0] := by
  unfold SatisfiesEq1 InversesOK; decide +kernel

theorem b2_Hc :
    (List.range 13).map (Hc B2 [2, 2]) = [1, 1, 3, 2, 5, 2, 3, 1, 1, 0, 0, 0, 0] := by
  decide +kernel

theorem b2_Hc_valley :
    Hc B2 [2, 2] 1 = 1 ∧ Hc B2 [2, 2] 2 = 3 ∧ Hc B2 [2, 2] 3 = 2 ∧ Hc B2 [2, 2] 4 = 5 := by
  decide +kernel

/-! ## 7b. A third witness inside the RECORDED root system: B_3, alpha = 2 alpha_1 + alpha_2 + alpha_3 -/

/-- H = 1 + 2q + 4q^2 + 3q^3 + 4q^4 + 2q^5 + q^6: full support, every coefficient positive, 4 > 3 < 4. -/
theorem b3_211_H : Htr 12 B3 [2, 1, 1] = [1, 2, 4, 3, 4, 2, 1, 0, 0, 0, 0, 0, 0] := by decide +kernel

theorem b3_211_eq1 :
    SatisfiesEq1 12 B3 [2, 1, 1] (Jfam 12 B3 [2, 1, 1]) ∧ InversesOK 12 B3 [2, 1, 1] := by
  unfold SatisfiesEq1 InversesOK; decide +kernel

theorem b3_211_eq1_low : ∀ N ∈ [1, 2, 3, 4],
    SatisfiesEq1 N B3 [2, 1, 1] (Jfam N B3 [2, 1, 1]) ∧ InversesOK N B3 [2, 1, 1] := by
  unfold SatisfiesEq1 InversesOK; decide +kernel

theorem b3_211_Hc_valley :
    Hc B3 [2, 1, 1] 1 = 2 ∧ Hc B3 [2, 1, 1] 2 = 4 ∧ Hc B3 [2, 1, 1] 3 = 3 ∧ Hc B3 [2, 1, 1] 4 = 4 := by
  decide +kernel

/-! ## 7c. Positive controls against formulas PRINTED in the source (type A) -/

def A2 : Gram := [[2, -1], [-1, 2]]
def A3 : Gram := [[2, -1, 0], [-1, 2, -1], [0, -1, 2]]

/-- Source, Example 1.1: in type A_2 the numerator is the Gaussian binomial [a1+a2 choose a1]_q.
    For a = (1,1): 1 + q.  For a = (2,2): [4 choose 2]_q = 1 + q + 2q^2 + q^3 + q^4. -/
theorem a2_example_1_1 :
    Htr 8 A2 [1, 1] = [1, 1, 0, 0, 0, 0, 0, 0, 0] ∧ Htr 8 A2 [2, 2] = [1, 1, 2, 1, 1, 0, 0, 0, 0] := by
  decide +kernel

/-- Source, Example 1.3: for alpha = alpha_1 + ... + alpha_n in type A_n the numerator is the n-th
    Narayana polynomial; n = 3 gives 1 + 3q + q^2. -/
theorem a3_example_1_3 : Htr 8 A3 [1, 1, 1] = [1, 3, 1, 0, 0, 0, 0, 0, 0] := by decide +kernel

/-- The recorded witness is the A_2 numerator 1 + q of Example 1.1 with q replaced by q^2:
    alpha = alpha_1 + alpha_2 lives on the two LONG simple roots of B_3, where d_i = 2. -/
theorem recorded_witness_is_A2_in_q_squared :
    (List.range 9).map (fun m => coeff (Htr 16 B3 [1, 1, 0]) (2 * m)) = Htr 8 A2 [1, 1]
      ∧ (List.range 8).map (fun m => coeff (Htr 16 B3 [1, 1, 0]) (2 * m + 1)) = [0, 0, 0, 0, 0, 0, 0, 0] := by
  decide +kernel

/-! ## 8. The refutations, each as one theorem -/

/-- The recorded witness is not unimodal in consecutive powers of q. -/
theorem b3_not_unimodal : ¬ UnimodalSeq (Hc B3 [1, 1, 0]) := by
  obtain ⟨h0, h1, h2⟩ := b3_Hc
  exact not_unimodal_of_valley _ 0 (by rw [h0, h1]; decide) (by rw [h1, h2]; decide)

/-- The second witness is not unimodal under any regrading. -/
theorem b2_not_regraded : ¬ RegradedUnimodal (Hc B2 [2, 2]) := by
  obtain ⟨h1, h2, h3, h4⟩ := b2_Hc_valley
  exact not_regraded_of_valley _ 2 (by rw [h1]; decide) (by rw [h2, h3]; decide)
    (by rw [h3, h4]; decide)

/-- The third witness, inside the recorded root system, is not unimodal under any regrading. -/
theorem b3_211_not_regraded : ¬ RegradedUnimodal (Hc B3 [2, 1, 1]) := by
  obtain ⟨h1, h2, h3, h4⟩ := b3_211_Hc_valley
  exact not_regraded_of_valley _ 2 (by rw [h1]; decide) (by rw [h2, h3]; decide)
    (by rw [h3, h4]; decide)

/-- Conjecture 7.3, literal reading, refuted by the RECORDED witness (B_3, 1 + q^2). -/
theorem not_conjecture73 : ¬ Conjecture73 :=
  fun h => b3_not_unimodal (h B3 B3roots [1, 1, 0] b3_admissible b3_rootSystem (by decide))

/-- Conjecture 7.3 refuted under every grading convention by the SECOND witness (B_2, (2,2)). -/
theorem not_conjecture73_regraded : ¬ Conjecture73_regraded :=
  fun h => b2_not_regraded (h B2 B2roots [2, 2] b2_admissible b2_rootSystem (by decide))

/-- The same, from the recorded root system B_3 at alpha = 2 alpha_1 + alpha_2 + alpha_3. -/
theorem not_conjecture73_regraded_via_b3 : ¬ Conjecture73_regraded :=
  fun h => b3_211_not_regraded (h B3 B3roots [2, 1, 1] b3_admissible b3_rootSystem (by decide))

/-- The relational form, which does not mention `Jfam` or `Hc`, refuted by the second witness. -/
theorem not_conjecture73_relational : ¬ Conjecture73_relational := by
  intro h
  obtain ⟨e, k, _, hk⟩ := h B2 B2roots [2, 2] b2_admissible b2_rootSystem (by decide)
  obtain ⟨hdiv, inc, dec⟩ := hk 12 (Jfam 12 B2 [2, 2]) b2_eq1 b2_inverses
  have hnum : numerator 12 B2 [2, 2] (Jfam 12 B2 [2, 2]) = [1, 1, 3, 2, 5, 2, 3, 1, 1, 0, 0, 0, 0] :=
    b2_H
  rw [hnum] at hdiv inc dec
  have e1 : e = 1 := Nat.dvd_one.mp (hdiv 1 (by decide) (by decide))
  subst e1
  by_cases hk3 : k ≤ 3
  · have h5 := dec 3 hk3 (by decide)
    revert h5; decide
  · have h3 := inc 2 (by omega) (by decide)
    revert h3; decide

/-- The literal reading also falls to the second witness alone. -/
theorem not_conjecture73_via_b2 : ¬ Conjecture73 :=
  fun h => not_conjecture73_regraded (conjecture73_imp_regraded h)

/-- The recorded witness cannot serve against the regraded reading on the computed range:
    B_3 and B_2 are not simply laced, so neither touches the simply laced conjecture. -/
theorem b3_not_simplyLaced : ¬ SimplyLaced B3 := by
  intro h; have := h 0 (by decide); revert this; decide

theorem b2_not_simplyLaced : ¬ SimplyLaced B2 := by
  intro h; have := h 0 (by decide); revert this; decide

/-! ## 9. Equation (1) modulo q^(N+1) has at most one solution (general theorem)

    Added by the resuming agent.  For ANY Gram matrix `G`, order `N` and vector `a` such that every
    nonzero `b` in the box has energy (b,b)/2 >= 1, two families that both satisfy the source's
    equation (1) modulo q^(N+1) with J_0 = 1 agree on the whole box.  This is the source's remark
    "(1) together with the initial condition J_0 = 1 uniquely determines the rational functions",
    transported to Z[q]/(q^(N+1)) and proved, not assumed.  Consequence: the numerator of EVERY
    solving family is the computed one (`b2_every_solution`, `b3_every_solution`). -/

def vsum : List Nat → Nat
  | [] => 0
  | x :: xs => x + vsum xs

theorem vle_refl : ∀ (a : List Nat), VLe a a
  | [] => VLe.nil
  | _ :: xs => VLe.cons (Nat.le_refl _) (vle_refl xs)

theorem vle_trans {c b : List Nat} (h1 : VLe c b) : ∀ {a : List Nat}, VLe b a → VLe c a := by
  induction h1 with
  | nil => intro a h; exact h
  | cons hxy _ ih =>
    intro a h2
    cases h2 with
    | cons hyz hrest2 => exact VLe.cons (Nat.le_trans hxy hyz) (ih hrest2)

theorem vle_vsum {c b : List Nat} (h : VLe c b) :
    vsum c ≤ vsum b ∧ (vsum c = vsum b → c = b) := by
  induction h with
  | nil => exact ⟨Nat.le_refl _, fun _ => rfl⟩
  | @cons x y xs ys hxy _ ih =>
    obtain ⟨ih1, ih2⟩ := ih
    refine ⟨by simp only [vsum]; omega, fun heq => ?_⟩
    simp only [vsum] at heq
    have hx : x = y := by omega
    have hs : vsum xs = vsum ys := by omega
    rw [hx, ih2 hs]

theorem box_trans {a b c : List Nat} (hc : c ∈ box b) (hb : b ∈ box a) : c ∈ box a :=
  (mem_box a c).mpr (vle_trans ((mem_box b c).mp hc) ((mem_box a b).mp hb))

theorem vsum_lt_of_mem_box {b c : List Nat} (hc : c ∈ box b) (hne : c ≠ b) : vsum c < vsum b := by
  obtain ⟨h1, h2⟩ := vle_vsum ((mem_box b c).mp hc)
  exact Nat.lt_of_le_of_ne h1 (fun heq => hne (h2 heq))

theorem zero_of_isZero {b a : List Nat} (h : VLe b a) : isZero b = true → b = a.map (fun _ => 0) := by
  induction h with
  | nil => intro _; rfl
  | @cons x y xs ys _ _ ih =>
    intro hz
    have hsplit : isZero (x :: xs) = ((x == 0) && isZero xs) := rfl
    rw [hsplit] at hz
    cases hx : (x == 0) with
    | false => rw [hx] at hz; simp at hz
    | true =>
      rw [hx] at hz
      have hxs : isZero xs = true := by simpa using hz
      have hx0 : x = 0 := by simpa using hx
      rw [hx0, ih hxs]
      rfl

theorem foldl_add_congr (f g : Nat → Int) : ∀ (l : List Nat), (∀ i ∈ l, f i = g i) → ∀ (init : Int),
    l.foldl (fun acc i => acc + f i) init = l.foldl (fun acc i => acc + g i) init
  | [], _, _ => rfl
  | x :: xs, h, init => by
    simp only [List.foldl_cons]
    rw [h x (by simp)]
    exact foldl_add_congr f g xs (fun i hi => h i (List.mem_cons_of_mem _ hi)) _

theorem sumTo_congr (n : Nat) (f g : Nat → Int) (h : ∀ i, i ≤ n → f i = g i) :
    sumTo n f = sumTo n g :=
  foldl_add_congr f g _ (fun i hi => h i (by have := List.mem_range.mp hi; omega)) 0

theorem map_congr_own {α β : Type} (f g : α → β) : ∀ (l : List α), (∀ x ∈ l, f x = g x) → l.map f = l.map g
  | [], _ => rfl
  | x :: xs, h => by
    simp only [List.map_cons]
    rw [h x (by simp), map_congr_own f g xs (fun y hy => h y (List.mem_cons_of_mem _ hy))]

theorem tab_congr (N : Nat) (f g : Nat → Int) (h : ∀ n, n ≤ N → f n = g n) : tab N f = tab N g := by
  unfold tab
  apply map_congr_own
  intro n hn
  exact h n (by have := List.mem_range.mp hn; omega)

theorem foldl_addT_isTab (N : Nat) : ∀ (l : List Poly) (p : Poly),
    (∃ f, p = tab N f) → ∃ f, l.foldl (addT N) p = tab N f
  | [], _, hp => hp
  | x :: xs, p, _ => foldl_addT_isTab N xs (addT N p x) ⟨_, rfl⟩

theorem coeff_foldl_addT_congr (N n : Nat) (hn : n ≤ N) {α : Type} (F F' : α → Poly) :
    ∀ (l : List α), (∀ c ∈ l, coeff (F c) n = coeff (F' c) n) →
      ∀ (p p' : Poly), coeff p n = coeff p' n →
        coeff ((l.map F).foldl (addT N) p) n = coeff ((l.map F').foldl (addT N) p') n
  | [], _, _, _, h => h
  | c :: cs, hF, p, p', h => by
    simp only [List.map_cons, List.foldl_cons]
    apply coeff_foldl_addT_congr N n hn F F' cs (fun d hd => hF d (List.mem_cons_of_mem _ hd))
    rw [coeff_addT N n _ _ hn, coeff_addT N n _ _ hn, h, hF c (by simp)]

/-- Coefficient n of the summand indexed by c only sees coefficients k of J_c with k + (c,c)/2 <= n. -/
theorem coeff_summand_congr (N n : Nat) (hn : n ≤ N) (G : Gram) (J J' : List Nat → Poly)
    (b c : List Nat) (h : ∀ k, k + energy G c ≤ n → coeff (J c) k = coeff (J' c) k) :
    coeff (summand N G J b c) n = coeff (summand N G J' b c) n := by
  unfold summand
  rw [coeff_mulT N n _ _ hn, coeff_mulT N n _ _ hn]
  apply sumTo_congr
  intro i hi
  by_cases hie : i = energy G c
  · subst hie
    have hne : n - energy G c ≤ N := by omega
    rw [coeff_mulT N (n - energy G c) _ _ hne, coeff_mulT N (n - energy G c) _ _ hne]
    congr 1
    apply sumTo_congr
    intro k hk
    rw [h (n - energy G c - k) (by omega)]
  · have hz : coeff (monoT N (energy G c)) i = 0 := by
      unfold monoT
      rw [coeff_tab N i _ (by omega)]
      simp [hie]
    rw [hz, Int.zero_mul, Int.zero_mul]

theorem eq1_coeff_core (N : Nat) (G : Gram) (a : List Nat) (J J' : List Nat → Poly)
    (hE : ∀ b ∈ box a, isZero b = false → 1 ≤ energy G b)
    (h : SatisfiesEq1 N G a J) (h' : SatisfiesEq1 N G a J') (m : Nat) (hm : m ≤ N)
    (hprev : ∀ k, k < m → ∀ b ∈ box a, coeff (J b) k = coeff (J' b) k) :
    ∀ s, ∀ b ∈ box a, vsum b < s → coeff (J b) m = coeff (J' b) m := by
  intro s
  induction s with
  | zero => intro b _ hs; exact absurd hs (Nat.not_lt_zero _)
  | succ s ih =>
    intro b hb hs
    cases hz : isZero b with
    | true =>
      have hb0 : b = a.map (fun _ => 0) := zero_of_isZero ((mem_box a b).mp hb) hz
      rw [hb0, h.1, h'.1]
    | false =>
      have e1 : coeff (J b) m = coeff (rhs1 N G J b) m :=
        congrArg (fun p => coeff p m) (h.2 b hb)
      have e2 : coeff (J' b) m = coeff (rhs1 N G J' b) m :=
        congrArg (fun p => coeff p m) (h'.2 b hb)
      refine (e1.trans ?_).trans e2.symm
      unfold rhs1 sumPolys
      refine coeff_foldl_addT_congr N m hm (summand N G J b) (summand N G J' b) (box b) ?_
        (zeroT N) (zeroT N) rfl
      intro c hc
      apply coeff_summand_congr N m hm
      intro k hk
      have hca : c ∈ box a := box_trans hc hb
      by_cases hcb : c = b
      · have he : 1 ≤ energy G c := by rw [hcb]; exact hE b hb hz
        exact hprev k (by omega) c hca
      · have hlt := vsum_lt_of_mem_box hc hcb
        by_cases hkm : k < m
        · exact hprev k hkm c hca
        · have hkeq : k = m := by omega
          rw [hkeq]
          exact ih c hca (by omega)

theorem eq1_coeff_unique (N : Nat) (G : Gram) (a : List Nat) (J J' : List Nat → Poly)
    (hE : ∀ b ∈ box a, isZero b = false → 1 ≤ energy G b)
    (h : SatisfiesEq1 N G a J) (h' : SatisfiesEq1 N G a J') :
    ∀ n m, m ≤ n → m ≤ N → ∀ b ∈ box a, coeff (J b) m = coeff (J' b) m := by
  intro n
  induction n with
  | zero =>
    intro m hm0 hmN b hb
    have hm : m = 0 := by omega
    subst hm
    exact eq1_coeff_core N G a J J' hE h h' 0 hmN (fun k hk => absurd hk (Nat.not_lt_zero k))
      (vsum b + 1) b hb (Nat.lt_succ_self _)
  | succ n ih =>
    intro m hmn hmN b hb
    by_cases hle : m ≤ n
    · exact ih m hle hmN b hb
    · exact eq1_coeff_core N G a J J' hE h h' m hmN
        (fun k hk c hc => ih k (by omega) (by omega) c hc) (vsum b + 1) b hb (Nat.lt_succ_self _)

/-- UNIQUENESS: two families solving the source's equation (1) modulo q^(N+1) with J_0 = 1
    coincide on {b : 0 <= b <= a}. -/
theorem eq1_unique (N : Nat) (G : Gram) (a : List Nat) (J J' : List Nat → Poly)
    (hE : ∀ b ∈ box a, isZero b = false → 1 ≤ energy G b)
    (h : SatisfiesEq1 N G a J) (h' : SatisfiesEq1 N G a J') : ∀ b ∈ box a, J b = J' b := by
  intro b hb
  have hc : ∀ n, n ≤ N → coeff (J b) n = coeff (J' b) n :=
    fun n hn => eq1_coeff_unique N G a J J' hE h h' n n (Nat.le_refl n) hn b hb
  have t1 : ∃ f, rhs1 N G J b = tab N f := foldl_addT_isTab N _ _ ⟨fun _ => 0, rfl⟩
  have t2 : ∃ f, rhs1 N G J' b = tab N f := foldl_addT_isTab N _ _ ⟨fun _ => 0, rfl⟩
  obtain ⟨f, hf⟩ := t1
  obtain ⟨f', hf'⟩ := t2
  have hJ : J b = tab N f := (h.2 b hb).trans hf
  have hJ' : J' b = tab N f' := (h'.2 b hb).trans hf'
  rw [hJ, hJ']
  apply tab_congr
  intro n hn
  have hcn := hc n hn
  rw [hJ, hJ', coeff_tab N n f hn, coeff_tab N n f' hn] at hcn
  exact hcn

theorem numerator_unique (N : Nat) (G : Gram) (a : List Nat) (J J' : List Nat → Poly)
    (hE : ∀ b ∈ box a, isZero b = false → 1 ≤ energy G b)
    (h : SatisfiesEq1 N G a J) (h' : SatisfiesEq1 N G a J') :
    numerator N G a J = numerator N G a J' := by
  unfold numerator
  rw [eq1_unique N G a J J' hE h h' a ((mem_box a a).mpr (vle_refl a))]

/-! ## 10. Consequences at the witnesses: EVERY solving family, not only the computed one -/

theorem b2_energy_pos : ∀ b ∈ box [2, 2], isZero b = false → 1 ≤ energy B2 b := by decide +kernel
theorem b3_energy_pos : ∀ b ∈ box [1, 1, 0], isZero b = false → 1 ≤ energy B3 b := by decide +kernel
theorem b3_211_energy_pos : ∀ b ∈ box [2, 1, 1], isZero b = false → 1 ≤ energy B3 b := by
  decide +kernel

/-- Second witness: every family solving the source's equation (1) modulo q^13 with J_0 = 1 has the
    numerator 1 + q + 3q^2 + 2q^3 + 5q^4 + 2q^5 + 3q^6 + q^7 + q^8 (to order q^12). -/
theorem b2_every_solution (J : List Nat → Poly) (h : SatisfiesEq1 12 B2 [2, 2] J) :
    numerator 12 B2 [2, 2] J = [1, 1, 3, 2, 5, 2, 3, 1, 1, 0, 0, 0, 0] :=
  (numerator_unique 12 B2 [2, 2] J (Jfam 12 B2 [2, 2]) b2_energy_pos h b2_eq1).trans b2_H

/-- Recorded witness: every solving family has the numerator 1 + q^2 (to order q^12). -/
theorem b3_every_solution (J : List Nat → Poly) (h : SatisfiesEq1 12 B3 [1, 1, 0] J) :
    numerator 12 B3 [1, 1, 0] J = [1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0] :=
  (numerator_unique 12 B3 [1, 1, 0] J (Jfam 12 B3 [1, 1, 0]) b3_energy_pos h b3_eq1).trans b3_H

/-- Third witness: every solving family has the numerator 1 + 2q + 4q^2 + 3q^3 + 4q^4 + 2q^5 + q^6. -/
theorem b3_211_every_solution (J : List Nat → Poly) (h : SatisfiesEq1 12 B3 [2, 1, 1] J) :
    numerator 12 B3 [2, 1, 1] J = [1, 2, 4, 3, 4, 2, 1, 0, 0, 0, 0, 0, 0] :=
  (numerator_unique 12 B3 [2, 1, 1] J (Jfam 12 B3 [2, 1, 1]) b3_211_energy_pos h b3_211_eq1.1).trans
    b3_211_H

/-- At the second witness NO solving family has a numerator that is unimodal under ANY regrading
    t = q^e and ANY peak k.  This is the instance-level refutation, free of the implementation. -/
theorem b2_every_solution_not_regraded (J : List Nat → Poly) (h : SatisfiesEq1 12 B2 [2, 2] J)
    (e k : Nat) : ¬ TruncRegradedUnimodal 12 k e (numerator 12 B2 [2, 2] J) := by
  rw [b2_every_solution J h]
  intro ⟨hdiv, inc, dec⟩
  have e1 : e = 1 := Nat.dvd_one.mp (hdiv 1 (by decide) (by decide))
  subst e1
  by_cases hk3 : k ≤ 3
  · have h5 := dec 3 hk3 (by decide)
    revert h5; decide
  · have h3 := inc 2 (by omega) (by decide)
    revert h3; decide

/-- At the recorded witness every solving family IS unimodal after the regrading t = q^2 (peak 0 or 1):
    the recorded witness cannot refute the regraded reading, whichever solution is taken. -/
theorem b3_every_solution_is_regraded_unimodal (J : List Nat → Poly)
    (h : SatisfiesEq1 12 B3 [1, 1, 0] J) :
    TruncRegradedUnimodal 12 1 2 (numerator 12 B3 [1, 1, 0] J) := by
  rw [b3_every_solution J h]
  have key : ∀ m, m ≤ 5 → 1 ≤ m →
      coeff [1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0] (2 * (m + 1))
        ≤ coeff [1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0] (2 * m) := by decide
  refine ⟨by decide, by decide, ?_⟩
  intro m h1 h2
  exact key m (by omega) h1

/-! ### A class-wise repair that the second witness does NOT refute (stated only)

    Not a reading of the source, which says "unimodal" and explains it by hard Lefschetz for a variety
    whose even Betti numbers are the coefficients.  Recorded so that nobody reads the refutation as
    saying more than it does: along each residue class of exponents modulo 2 the second witness is
    1, 3, 5, 3, 1 and 1, 2, 2, 1, both unimodal. -/

/-- Unimodal along each residue class of exponents modulo r. -/
def ClasswiseUnimodal (r : Nat) (h : Nat → Int) : Prop :=
  ∀ j, j < r → UnimodalSeq (fun m => h (r * m + j))

/-- The largest d_i (1, 2 or 3 for a root datum). -/
def lacing (G : Gram) : Nat := (dvec G).foldl max 1

/-- A class-wise form of Conjecture 7.3.  Stated for the record; NOT refuted and NOT proved here. -/
def Conjecture73_classwise : Prop :=
  ∀ (G : Gram) (R : List (List Int)) (a : List Nat),
    Admissible G → IsRootSystem G R → a.length = G.length →
      ClasswiseUnimodal (lacing G) (Hc G a)

theorem b2_lacing : lacing B2 = 2 := by decide +kernel

theorem b2_residue_classes :
    (List.range 5).map (fun m => Hc B2 [2, 2] (2 * m)) = [1, 3, 5, 3, 1] ∧
    (List.range 4).map (fun m => Hc B2 [2, 2] (2 * m + 1)) = [1, 2, 2, 1] := by
  decide +kernel

end Toda

#print axioms Toda.not_conjecture73
#print axioms Toda.not_conjecture73_regraded
#print axioms Toda.not_conjecture73_via_b2
#print axioms Toda.not_conjecture73_relational
#print axioms Toda.not_conjecture73_regraded_via_b3
#print axioms Toda.b3_not_unimodal
#print axioms Toda.b2_not_regraded
#print axioms Toda.b3_admissible
#print axioms Toda.b3_rootSystem
#print axioms Toda.b2_rootSystem
#print axioms Toda.b3_lengths
#print axioms Toda.b2_lengths
#print axioms Toda.b2_admissible
#print axioms Toda.b3_H
#print axioms Toda.b3_J
#print axioms Toda.b3_eq1
#print axioms Toda.b3_inverses
#print axioms Toda.b3_eq1_low
#print axioms Toda.recorded_witness_is_regraded_shape
#print axioms Toda.b2_H
#print axioms Toda.b2_eq1
#print axioms Toda.b2_inverses
#print axioms Toda.b2_eq1_low
#print axioms Toda.b2_Hc
#print axioms Toda.b2_Hc_valley
#print axioms Toda.b3_211_H
#print axioms Toda.b3_211_eq1
#print axioms Toda.b3_211_eq1_low
#print axioms Toda.b3_211_Hc_valley
#print axioms Toda.a2_example_1_1
#print axioms Toda.a3_example_1_3
#print axioms Toda.recorded_witness_is_A2_in_q_squared
#print axioms Toda.mem_box
#print axioms Toda.coeff_tab
#print axioms Toda.coeff_mulT
#print axioms Toda.not_unimodal_of_valley
#print axioms Toda.not_regraded_of_valley
#print axioms Toda.conjecture73_imp_regraded
#print axioms Toda.eq1_unique
#print axioms Toda.numerator_unique
#print axioms Toda.eq1_coeff_unique
#print axioms Toda.b2_every_solution
#print axioms Toda.b3_every_solution
#print axioms Toda.b3_211_every_solution
#print axioms Toda.b2_every_solution_not_regraded
#print axioms Toda.b3_every_solution_is_regraded_unimodal
#print axioms Toda.b2_energy_pos
#print axioms Toda.b3_energy_pos
#print axioms Toda.b3_211_energy_pos
#print axioms Toda.b2_lacing
#print axioms Toda.b2_residue_classes
#print axioms Toda.b3_211_not_regraded
#print axioms Toda.b3_Hc
#print axioms Toda.b3_d
#print axioms Toda.b2_d
#print axioms Toda.b3_energies
#print axioms Toda.b2_energies
#print axioms Toda.b3_not_simplyLaced
#print axioms Toda.b2_not_simplyLaced
#print axioms Toda.coeff_addT
#print axioms Toda.regraded_of_unimodal
#print axioms Toda.conjecture73_imp_simplyLaced
#print axioms Toda.b3_box
#print axioms Toda.b2_box

/-
  ===========================================================================================
  ADDITION (namespace `Exact`).  Everything above this line is the text of TodaNumerator.lean,
  unchanged.  Everything below was added later by a separate agent, after the adversarial review
  (its section 2 and non-blocking remark 1): the refutation restated through EXACT identities in
  Z[q], so that the statement needs no truncation order, no power series and no inverse.

  If J_b = P_b / (q)_b^2, the source's equation (1) at b, multiplied by (q)_b^3, reads

      P_b (q)_b = sum over 0 <= c <= b of q^((c,c)/2) P_c ((q)_b/(q)_c)^2 ((q)_b/(q)_(b-c)),

  with (q)_b/(q)_c     = prod_i prod_{j=c_i+1}^{b_i}     (1 - q^(d_i j)),
       (q)_b/(q)_(b-c) = prod_i prod_{j=b_i-c_i+1}^{b_i} (1 - q^(d_i j)),   d_i = (alpha_i,alpha_i)/2,
  an identity between POLYNOMIALS.  `ClearedEq1 G a P` says: P_0 = 1 and this identity holds at every
  b in the box of a.

  This namespace uses its OWN polynomial arithmetic on coefficient lists (schoolbook product, no
  truncation), its own bilinear form, d_i, box enumeration (last coordinate outermost) and its own
  notion of unimodality (no strict interior dip).  From the certificate above the headline
  `not_conjecture73_exact` reuses ONLY `Toda.Admissible`, `Toda.IsRootSystem`, the Gram matrix
  `Toda.B2`, the root list `Toda.B2roots` and the two proofs `Toda.b2_admissible`,
  `Toda.b2_rootSystem`.  The theorems of section E9 are cross-checks against the certificate and
  are not used by the headline.

  What is proved here and what is left to prose is set out in EXACT_FORM.md.
  ===========================================================================================
-/

namespace Exact

/-! ## E1. Z[q] as coefficient lists (index = exponent of q); no truncation anywhere -/

abbrev Pol := List Int

/-- Coefficient of q^n; 0 beyond the end of the list. -/
def cf : Pol → Nat → Int
  | [], _ => 0
  | x :: _, 0 => x
  | _ :: xs, n + 1 => cf xs n

def padd : Pol → Pol → Pol
  | [], r => r
  | x :: xs, [] => x :: xs
  | x :: xs, y :: ys => (x + y) :: padd xs ys

def pscale (k : Int) : Pol → Pol
  | [] => []
  | x :: xs => (k * x) :: pscale k xs

/-- Schoolbook product: (x + q p') r = x r + q (p' r). -/
def pmul : Pol → Pol → Pol
  | [], _ => []
  | x :: xs, r => padd (pscale x r) (0 :: pmul xs r)

def allZero : Pol → Bool
  | [] => true
  | x :: xs => decide (x = 0) && allZero xs

/-- Equality of polynomials: equal entries on the common part, zeros beyond it. -/
def peq : Pol → Pol → Bool
  | [], r => allZero r
  | x :: xs, [] => allZero (x :: xs)
  | x :: xs, y :: ys => decide (x = y) && peq xs ys

/-- q^e. -/
def mono : Nat → Pol
  | 0 => [1]
  | e + 1 => 0 :: mono e

/-- 1 - q^k  (the zero polynomial when k = 0). -/
def oneMinus (k : Nat) : Pol := padd [1] (pscale (-1) (mono k))

def psum : List Pol → Pol
  | [] => []
  | p :: ps => padd p (psum ps)

/-- `csum n f = f 0 + f 1 + ... + f n`. -/
def csum : Nat → (Nat → Int) → Int
  | 0, f => f 0
  | n + 1, f => csum n f + f (n + 1)

/-! ### The list operations really are the ring operations of Z[q] (general theorems) -/

theorem cf_nil (n : Nat) : cf [] n = 0 := by cases n <;> rfl

theorem cf_eq_getD : ∀ (p : Pol) (n : Nat), cf p n = p.getD n 0
  | [], n => by rw [cf_nil]; rfl
  | _ :: _, 0 => rfl
  | _ :: xs, n + 1 => by
    show cf xs n = (_ :: xs).getD (n + 1) 0
    rw [cf_eq_getD xs n]; rfl

theorem cf_padd : ∀ (p r : Pol) (n : Nat), cf (padd p r) n = cf p n + cf r n
  | [], r, n => by
    show cf r n = cf [] n + cf r n
    rw [cf_nil]; omega
  | x :: xs, [], n => by
    show cf (x :: xs) n = cf (x :: xs) n + cf [] n
    rw [cf_nil]; omega
  | x :: xs, y :: ys, 0 => rfl
  | x :: xs, y :: ys, n + 1 => by
    show cf (padd xs ys) n = cf xs n + cf ys n
    exact cf_padd xs ys n

theorem cf_pscale (k : Int) : ∀ (p : Pol) (n : Nat), cf (pscale k p) n = k * cf p n
  | [], n => by
    show cf [] n = k * cf [] n
    rw [cf_nil, Int.mul_zero]
  | x :: xs, 0 => rfl
  | x :: xs, n + 1 => by
    show cf (pscale k xs) n = k * cf xs n
    exact cf_pscale k xs n

theorem csum_congr : ∀ (n : Nat) (f g : Nat → Int), (∀ i, i ≤ n → f i = g i) → csum n f = csum n g
  | 0, f, g, h => h 0 (Nat.le_refl 0)
  | n + 1, f, g, h => by
    show csum n f + f (n + 1) = csum n g + g (n + 1)
    rw [csum_congr n f g (fun i hi => h i (by omega)), h (n + 1) (Nat.le_refl _)]

theorem csum_zero : ∀ (n : Nat), csum n (fun _ => 0) = 0
  | 0 => rfl
  | n + 1 => by
    show csum n (fun _ => 0) + 0 = 0
    rw [csum_zero n]; rfl

theorem csum_shift : ∀ (n : Nat) (f : Nat → Int), csum (n + 1) f = f 0 + csum n (fun i => f (i + 1))
  | 0, f => rfl
  | n + 1, f => by
    show csum (n + 1) f + f (n + 2) = f 0 + (csum n (fun i => f (i + 1)) + f (n + 2))
    rw [csum_shift n f]; omega

/-- Coefficient n of the schoolbook product is the Cauchy sum: `pmul` is multiplication in Z[q]. -/
theorem cf_pmul : ∀ (p r : Pol) (n : Nat),
    cf (pmul p r) n = csum n (fun i => cf p i * cf r (n - i))
  | [], r, n => by
    show cf [] n = _
    rw [cf_nil]
    have : (fun i => cf [] i * cf r (n - i)) = (fun _ => (0 : Int)) := by
      funext i; rw [cf_nil, Int.zero_mul]
    rw [this, csum_zero]
  | x :: xs, r, 0 => by
    show cf (padd (pscale x r) (0 :: pmul xs r)) 0 = cf (x :: xs) 0 * cf r (0 - 0)
    rw [cf_padd, cf_pscale]
    show x * cf r 0 + 0 = x * cf r 0
    omega
  | x :: xs, r, n + 1 => by
    show cf (padd (pscale x r) (0 :: pmul xs r)) (n + 1) = _
    rw [cf_padd, cf_pscale, csum_shift]
    show x * cf r (n + 1) + cf (pmul xs r) n
        = x * cf r (n + 1 - 0) + csum n (fun i => cf xs i * cf r (n + 1 - (i + 1)))
    rw [cf_pmul xs r n, Nat.sub_zero]
    have : (fun i => cf xs i * cf r (n + 1 - (i + 1))) = (fun i => cf xs i * cf r (n - i)) := by
      funext i; rw [Nat.add_sub_add_right]
    rw [this]

theorem cf_mono_ne : ∀ (e i : Nat), i ≠ e → cf (mono e) i = 0
  | 0, 0, h => absurd rfl h
  | 0, i + 1, _ => cf_nil i
  | _ + 1, 0, _ => rfl
  | e + 1, i + 1, h => cf_mono_ne e i (fun hie => h (by omega))

theorem cf_mono_self : ∀ (e : Nat), cf (mono e) e = 1
  | 0 => rfl
  | e + 1 => cf_mono_self e

theorem allZero_cf : ∀ (p : Pol), allZero p = true → ∀ n, cf p n = 0
  | [], _, n => cf_nil n
  | x :: xs, h, n => by
    have h' : (decide (x = 0) && allZero xs) = true := h
    rw [Bool.and_eq_true] at h'
    cases n with
    | zero => exact of_decide_eq_true h'.1
    | succ n => exact allZero_cf xs h'.2 n

/-- `peq p r = true` means equality of all coefficients, that is p = r in Z[q]. -/
theorem peq_cf : ∀ (p r : Pol), peq p r = true → ∀ n, cf p n = cf r n
  | [], r, h, n => by rw [cf_nil]; exact (allZero_cf r h n).symm
  | x :: xs, [], h, n => by rw [cf_nil]; exact allZero_cf (x :: xs) h n
  | x :: xs, y :: ys, h, n => by
    have h' : (decide (x = y) && peq xs ys) = true := h
    rw [Bool.and_eq_true] at h'
    cases n with
    | zero => exact of_decide_eq_true h'.1
    | succ n => exact peq_cf xs ys h'.2 n

theorem cf_allZero : ∀ (p : Pol), (∀ n, cf p n = 0) → allZero p = true
  | [], _ => rfl
  | x :: xs, h => by
    show (decide (x = 0) && allZero xs) = true
    rw [Bool.and_eq_true]
    exact ⟨decide_eq_true (h 0), cf_allZero xs (fun n => h (n + 1))⟩

theorem cf_peq : ∀ (p r : Pol), (∀ n, cf p n = cf r n) → peq p r = true
  | [], r, h => cf_allZero r (fun n => by rw [← h n, cf_nil])
  | x :: xs, [], h => cf_allZero (x :: xs) (fun n => by rw [h n, cf_nil])
  | x :: xs, y :: ys, h => by
    show (decide (x = y) && peq xs ys) = true
    rw [Bool.and_eq_true]
    exact ⟨decide_eq_true (h 0), cf_peq xs ys (fun n => h (n + 1))⟩

/-- The Boolean test `peq` is exactly equality in Z[q] (trailing zeros do not matter). -/
theorem peq_iff (p r : Pol) : peq p r = true ↔ ∀ n, cf p n = cf r n := ⟨peq_cf p r, cf_peq p r⟩

theorem cf_psum_congr {α : Type} (n : Nat) (F F' : α → Pol) : ∀ (l : List α),
    (∀ c ∈ l, cf (F c) n = cf (F' c) n) → cf (psum (l.map F)) n = cf (psum (l.map F')) n
  | [], _ => rfl
  | c :: cs, h => by
    show cf (padd (F c) (psum (cs.map F))) n = cf (padd (F' c) (psum (cs.map F'))) n
    rw [cf_padd, cf_padd, h c (List.mem_cons_self ..),
      cf_psum_congr n F F' cs (fun d hd => h d (List.mem_cons_of_mem _ hd))]

/-! ## E2. Root data read off the Gram matrix (own definitions) -/

abbrev GramM := List (List Int)

def isum : List Int → Int
  | [] => 0
  | x :: xs => x + isum xs

/-- (alpha_i, alpha_j); 0 outside the matrix. -/
def gent (G : GramM) (i j : Nat) : Int := cf (G.getD i []) j

/-- The i-th coordinate as an integer; 0 beyond the end. -/
def coord (x : List Nat) (i : Nat) : Int := Int.ofNat (x.getD i 0)

/-- (x, y) = sum_{i,j} x_i (alpha_i, alpha_j) y_j  for x = sum x_i alpha_i, y = sum y_j alpha_j. -/
def form (G : GramM) (x y : List Nat) : Int :=
  isum ((List.range G.length).map (fun i =>
    isum ((List.range G.length).map (fun j => coord x i * gent G i j * coord y j))))

/-- (b, b)/2. -/
def halfNorm (G : GramM) (b : List Nat) : Nat := (form G b b / 2).toNat

/-- d_i = (alpha_i, alpha_i)/2. -/
def dd (G : GramM) (i : Nat) : Nat := (gent G i i / 2).toNat

/-! ## E3. The box {c : 0 <= c <= a}, enumerated with the LAST coordinate outermost -/

def upTo : Nat → List Nat
  | 0 => [0]
  | n + 1 => upTo n ++ [n + 1]

def mybox : List Nat → List (List Nat)
  | [] => [[]]
  | x :: xs => (mybox xs).flatMap (fun t => (upTo x).map (fun k => k :: t))

def zeroVec (a : List Nat) : List Nat := a.map (fun _ => 0)

def vminus : List Nat → List Nat → List Nat
  | x :: xs, y :: ys => (x - y) :: vminus xs ys
  | _, _ => []

/-- Coordinatewise order on vectors of equal length. -/
inductive Below : List Nat → List Nat → Prop
  | nil : Below [] []
  | cons {x y : Nat} {xs ys : List Nat} : x ≤ y → Below xs ys → Below (x :: xs) (y :: ys)

theorem mem_upTo : ∀ (n k : Nat), k ∈ upTo n ↔ k ≤ n
  | 0, k => by
    show k ∈ [0] ↔ k ≤ 0
    rw [List.mem_singleton]; omega
  | n + 1, k => by
    show k ∈ upTo n ++ [n + 1] ↔ k ≤ n + 1
    rw [List.mem_append, mem_upTo n k, List.mem_singleton]; omega

/-- `mybox a` is exactly the interval of the source's sum. -/
theorem mem_mybox : ∀ (a b : List Nat), b ∈ mybox a ↔ Below b a
  | [], b => by
    show b ∈ [[]] ↔ Below b []
    rw [List.mem_singleton]
    constructor
    · intro h; rw [h]; exact Below.nil
    · intro h; cases h; rfl
  | x :: xs, b => by
    show b ∈ (mybox xs).flatMap (fun t => (upTo x).map (fun k => k :: t)) ↔ Below b (x :: xs)
    rw [List.mem_flatMap]
    constructor
    · intro ⟨t, ht, hb⟩
      rw [List.mem_map] at hb
      obtain ⟨k, hk, hkb⟩ := hb
      rw [← hkb]
      exact Below.cons ((mem_upTo x k).mp hk) ((mem_mybox xs t).mp ht)
    · intro h
      cases h with
      | @cons k _ t _ hk hrest =>
        exact ⟨t, (mem_mybox xs t).mpr hrest, List.mem_map.mpr ⟨k, (mem_upTo x k).mpr hk, rfl⟩⟩

/-! ## E4. The cleared form of the source's equation (1) -/

/-- prod_{j = lo+1}^{lo+t} (1 - q^(d j)). -/
def run (d lo : Nat) : Nat → Pol
  | 0 => [1]
  | t + 1 => pmul (run d lo t) (oneMinus (d * (lo + t + 1)))

/-- prod_{j = lo+1}^{hi} (1 - q^(d j)); the empty product 1 when hi <= lo. -/
def segment (d lo hi : Nat) : Pol := run d lo (hi - lo)

def ratioFrom (G : GramM) : Nat → List Nat → List Nat → Pol
  | i, l :: ls, h :: hs => pmul (segment (dd G i) l h) (ratioFrom G (i + 1) ls hs)
  | _, _, _ => [1]

/-- prod_i prod_{j = lo_i + 1}^{hi_i} (1 - q^(d_i j)) = (q)_hi / (q)_lo  for lo <= hi. -/
def ratio (G : GramM) (lo hi : List Nat) : Pol := ratioFrom G 0 lo hi

/-- (q)_b. -/
def qfac (G : GramM) (b : List Nat) : Pol := ratio G (zeroVec b) b

/-- ((q)_b/(q)_c)^2 ((q)_b/(q)_(b-c)). -/
def kernelPol (G : GramM) (b c : List Nat) : Pol :=
  pmul (pmul (ratio G c b) (ratio G c b)) (ratio G (vminus b c) b)

/-- q^((c,c)/2) P_c ((q)_b/(q)_c)^2 ((q)_b/(q)_(b-c)). -/
def term (G : GramM) (P : List Nat → Pol) (b c : List Nat) : Pol :=
  pmul (mono (halfNorm G c)) (pmul (P c) (kernelPol G b c))

/-- The right-hand side: the sum over ALL 0 <= c <= b (the term c = b included). -/
def clearedRhs (G : GramM) (P : List Nat → Pol) (b : List Nat) : Pol :=
  psum ((mybox b).map (term G P b))

/-- The source's equation (1) for J_b = P_b/(q)_b^2, cleared of denominators, on the box of a,
    with the initial condition P_0 = 1.  An exact statement in Z[q]. -/
def ClearedEq1 (G : GramM) (a : List Nat) (P : List Nat → Pol) : Prop :=
  peq (P (zeroVec a)) [1] = true ∧
  ∀ b ∈ mybox a, peq (pmul (P b) (qfac G b)) (clearedRhs G P b) = true

/-- Every quotient used above is a genuine quotient: ((q)_b/(q)_c) (q)_c = (q)_b and
    ((q)_b/(q)_(b-c)) (q)_(b-c) = (q)_b, checked by multiplying back. -/
def QuotientsOK (G : GramM) (a : List Nat) : Prop :=
  ∀ b ∈ mybox a, ∀ c ∈ mybox b,
    peq (pmul (ratio G c b) (qfac G c)) (qfac G b) = true ∧
    peq (pmul (ratio G (vminus b c) b) (qfac G (vminus b c))) (qfac G b) = true

/-! ## E5. Unimodality without reference to the certificate's `UnimodalSeq` -/

/-- No strict interior dip: no i < j < k with h j < h i and h j < h k.  Every sequence that rises
    weakly to a peak and falls weakly afterwards has this property (`valleyFree_of_peak`). -/
def ValleyFree (h : Nat → Int) : Prop := ¬ ∃ i j k, i < j ∧ j < k ∧ h j < h i ∧ h j < h k

/-- The same after some regrading t = q^e: every exponent with nonzero coefficient is a multiple
    of e, and the sequence m |-> h (e m) has no strict interior dip. -/
def RegradedValleyFree (h : Nat → Int) : Prop :=
  ∃ e, 0 < e ∧ (∀ i, h i ≠ 0 → e ∣ i) ∧ ValleyFree (fun m => h (e * m))

/-- Conjecture 7.3 in exact form: for every root datum and every alpha, the numerator of EVERY
    polynomial family satisfying the cleared equation (1) is unimodal after some regrading. -/
def Conjecture73_exact : Prop :=
  ∀ (G : List (List Int)) (R : List (List Int)) (a : List Nat),
    Toda.Admissible G → Toda.IsRootSystem G R → a.length = G.length →
      ∀ P : List Nat → List Int, ClearedEq1 G a P → RegradedValleyFree (cf (P a))

/-- A family given by a finite table; the zero polynomial elsewhere. -/
def fromTable : List (List Nat × Pol) → List Nat → Pol
  | [], _ => []
  | (k, v) :: rest, b => if k = b then v else fromTable rest b

/-! ## E6. The witnesses -/

/-- B_2, box of (2,2): the nine numerators. -/
def PB2 : List Nat → Pol := fromTable
  [([0, 0], [1]), ([0, 1], [1]), ([0, 2], [1]), ([1, 0], [1]), ([2, 0], [1]),
   ([1, 1], [1, 1, 1]),
   ([1, 2], [1, 1, 3, 1, 1]),
   ([2, 1], [1, 1, 1, 1, 1]),
   ([2, 2], [1, 1, 3, 2, 5, 2, 3, 1, 1])]

/-- B_3, box of (1,1,0) (the RECORDED witness): four numerators. -/
def PB3_110 : List Nat → Pol := fromTable
  [([0, 0, 0], [1]), ([0, 1, 0], [1]), ([1, 0, 0], [1]), ([1, 1, 0], [1, 0, 1])]

/-- B_3, box of (2,1,1) (the third witness): twelve numerators. -/
def PB3_211 : List Nat → Pol := fromTable
  [([0, 0, 0], [1]), ([0, 0, 1], [1]), ([0, 1, 0], [1]), ([1, 0, 0], [1]), ([1, 0, 1], [1]),
   ([2, 0, 0], [1]), ([2, 0, 1], [1]),
   ([0, 1, 1], [1, 1, 1]),
   ([1, 1, 0], [1, 0, 1]),
   ([1, 1, 1], [1, 2, 4, 2, 1]),
   ([2, 1, 0], [1, 0, 1, 0, 1]),
   ([2, 1, 1], [1, 2, 4, 3, 4, 2, 1])]

/-- The exact identity at all nine states of the box of (2,2) in B_2. -/
theorem b2_cleared : ClearedEq1 Toda.B2 [2, 2] PB2 := by
  unfold ClearedEq1; decide +kernel

/-- The exact identity at all four states of the box of the recorded witness. -/
theorem b3_110_cleared : ClearedEq1 Toda.B3 [1, 1, 0] PB3_110 := by
  unfold ClearedEq1; decide +kernel

/-- The exact identity at all twelve states of the box of the third witness. -/
theorem b3_211_cleared : ClearedEq1 Toda.B3 [2, 1, 1] PB3_211 := by
  unfold ClearedEq1; decide +kernel

theorem PB2_top : PB2 [2, 2] = [1, 1, 3, 2, 5, 2, 3, 1, 1] := by decide +kernel
theorem PB3_110_top : PB3_110 [1, 1, 0] = [1, 0, 1] := by decide +kernel
theorem PB3_211_top : PB3_211 [2, 1, 1] = [1, 2, 4, 3, 4, 2, 1] := by decide +kernel

/-- The quotients are genuine at every pair of states of the three boxes. -/
theorem b2_quotients : QuotientsOK Toda.B2 [2, 2] := by unfold QuotientsOK; decide +kernel
theorem b3_110_quotients : QuotientsOK Toda.B3 [1, 1, 0] := by unfold QuotientsOK; decide +kernel
theorem b3_211_quotients : QuotientsOK Toda.B3 [2, 1, 1] := by unfold QuotientsOK; decide +kernel

/-- The data the identities were evaluated on, displayed: the order of the box, (b,b)/2 at every
    state, the d_i, and (q)_(2,2) = (1 - q^2)(1 - q^4)(1 - q)(1 - q^2). -/
theorem b2_data :
    mybox [2, 2] = [[0, 0], [1, 0], [2, 0], [0, 1], [1, 1], [2, 1], [0, 2], [1, 2], [2, 2]] ∧
    (mybox [2, 2]).map (halfNorm Toda.B2) = [0, 2, 8, 1, 1, 5, 4, 2, 4] ∧
    [dd Toda.B2 0, dd Toda.B2 1] = [2, 1] ∧
    qfac Toda.B2 [2, 2] = [1, -1, -2, 2, 0, 0, 2, -2, -1, 1] ∧
    pmul (PB2 [2, 2]) (qfac Toda.B2 [2, 2])
      = [1, 0, 0, -1, -1, -1, -3, 4, 1, 1, 4, -3, -1, -1, -1, 0, 0, 1] := by decide +kernel

theorem b3_data :
    mybox [1, 1, 0] = [[0, 0, 0], [1, 0, 0], [0, 1, 0], [1, 1, 0]] ∧
    (mybox [1, 1, 0]).map (halfNorm Toda.B3) = [0, 2, 2, 2] ∧
    (mybox [2, 1, 1]).map (halfNorm Toda.B3) = [0, 2, 8, 2, 2, 6, 1, 3, 9, 1, 1, 5] ∧
    [dd Toda.B3 0, dd Toda.B3 1, dd Toda.B3 2] = [2, 2, 1] := by decide +kernel

/-- The dip, displayed: coefficients 1, 3, 2, 5 at q^1, q^2, q^3, q^4, all positive. -/
theorem b2_dip_displayed :
    cf (PB2 [2, 2]) 1 = 1 ∧ cf (PB2 [2, 2]) 2 = 3 ∧ cf (PB2 [2, 2]) 3 = 2 ∧ cf (PB2 [2, 2]) 4 = 5 := by
  decide +kernel

/-- A dip at consecutive exponents together with a nonzero coefficient of q^1 excludes every
    regrading. -/
theorem not_regraded_of_dip (h : Nat → Int) (j : Nat) (hq : h 1 ≠ 0)
    (h1 : h (j + 1) < h j) (h2 : h (j + 1) < h (j + 2)) : ¬ RegradedValleyFree h := by
  intro ⟨e, _, hdiv, hv⟩
  have e1 : e = 1 := Nat.dvd_one.mp (hdiv 1 hq)
  subst e1
  apply hv
  refine ⟨j, j + 1, j + 2, by omega, by omega, ?_, ?_⟩
  · show h (1 * (j + 1)) < h (1 * j)
    rw [Nat.one_mul, Nat.one_mul]; exact h1
  · show h (1 * (j + 1)) < h (1 * (j + 2))
    rw [Nat.one_mul, Nat.one_mul]; exact h2

/-- THE HEADLINE.  Conjecture 7.3 in exact form is false: B_2, alpha = 2 alpha_1 + 2 alpha_2,
    numerator 1 + q + 3q^2 + 2q^3 + 5q^4 + 2q^5 + 3q^6 + q^7 + q^8, coefficients 3 > 2 < 5 at the
    consecutive exponents 2, 3, 4, coefficient of q^1 equal to 1. -/
theorem not_conjecture73_exact : ¬ Conjecture73_exact := by
  intro h
  have hr : RegradedValleyFree (cf (PB2 [2, 2])) :=
    h Toda.B2 Toda.B2roots [2, 2] Toda.b2_admissible Toda.b2_rootSystem (by decide) PB2 b2_cleared
  rw [PB2_top] at hr
  exact not_regraded_of_dip _ 2 (by decide) (by decide) (by decide) hr

/-- The third witness (inside the recorded root system B_3) also has a dip under every regrading:
    1 + 2q + 4q^2 + 3q^3 + 4q^4 + 2q^5 + q^6, coefficients 4 > 3 < 4. -/
theorem b3_211_not_regraded : ¬ RegradedValleyFree (cf (PB3_211 [2, 1, 1])) := by
  rw [PB3_211_top]
  exact not_regraded_of_dip _ 2 (by decide) (by decide) (by decide)

/-! ### The RECORDED witness does NOT refute the regraded statement -/

theorem onePlusQ2_tail (t : Nat) : cf [1, 0, 1] (2 * (t + 2)) = 0 := by
  rw [show 2 * (t + 2) = (2 * t + 1) + 3 by omega]
  exact cf_nil (2 * t + 1)

/-- 1 + q^2 with e = 2: every exponent that occurs is even, and in t = q^2 the sequence 1, 1, 0, ...
    has no dip. -/
theorem b3_110_regraded_with_e2 :
    (∀ i, cf (PB3_110 [1, 1, 0]) i ≠ 0 → 2 ∣ i) ∧
      ValleyFree (fun m => cf (PB3_110 [1, 1, 0]) (2 * m)) := by
  rw [PB3_110_top]
  constructor
  · intro i hi
    match i, hi with
    | 0, _ => exact ⟨0, rfl⟩
    | 1, hi => exact absurd rfl hi
    | 2, _ => exact ⟨1, rfl⟩
    | i + 3, hi => exact absurd (cf_nil i) hi
  · intro ⟨i, j, k, hij, hjk, _, h2⟩
    obtain ⟨t, rfl⟩ : ∃ t, k = t + 2 := ⟨k - 2, by omega⟩
    have h2' : cf [1, 0, 1] (2 * j) < cf [1, 0, 1] (2 * (t + 2)) := h2
    rw [onePlusQ2_tail t] at h2'
    match j, hij with
    | 0, hij => omega
    | 1, _ => revert h2'; decide
    | s + 2, _ => rw [onePlusQ2_tail s] at h2'; omega

/-- The recorded witness's numerator IS regraded-unimodal (e = 2): the recorded model witness does
    not refute `Conjecture73_exact`. -/
theorem b3_110_is_regraded : RegradedValleyFree (cf (PB3_110 [1, 1, 0])) :=
  ⟨2, by decide, b3_110_regraded_with_e2.1, b3_110_regraded_with_e2.2⟩

/-- ... while in consecutive powers of q (e = 1) it has the dip 1 > 0 < 1: it contradicts only the
    literal reading, as the certificate above says. -/
theorem b3_110_literal_dip : ¬ ValleyFree (cf (PB3_110 [1, 1, 0])) := by
  rw [PB3_110_top]
  intro hv
  exact hv ⟨0, 1, 2, by decide, by decide, by decide, by decide⟩

/-! ## E7. `ValleyFree` is implied by the peak form of unimodality (general theorem) -/

theorem chain_up (h : Nat → Int) (p : Nat) (inc : ∀ i, i < p → h i ≤ h (i + 1)) :
    ∀ (t i : Nat), i + t ≤ p → h i ≤ h (i + t)
  | 0, i, _ => Int.le_refl _
  | t + 1, i, hp => by
    have h1 := chain_up h p inc t i (by omega)
    have h2 := inc (i + t) (by omega)
    exact Int.le_trans h1 h2

theorem chain_down (h : Nat → Int) (p : Nat) (dec : ∀ i, p ≤ i → h (i + 1) ≤ h i) :
    ∀ (t i : Nat), p ≤ i → h (i + t) ≤ h i
  | 0, i, _ => Int.le_refl _
  | t + 1, i, hp => by
    have h1 := chain_down h p dec t i hp
    have h2 := dec (i + t) (by omega)
    exact Int.le_trans h2 h1

/-- Weak increase up to a peak p and weak decrease after it excludes a strict interior dip. -/
theorem valleyFree_of_peak (h : Nat → Int)
    (hu : ∃ p, (∀ i, i < p → h i ≤ h (i + 1)) ∧ (∀ i, p ≤ i → h (i + 1) ≤ h i)) :
    ValleyFree h := by
  intro ⟨i, j, k, hij, hjk, h1, h2⟩
  obtain ⟨p, inc, dec⟩ := hu
  by_cases hp : j ≤ p
  · have hc := chain_up h p inc (j - i) i (by omega)
    rw [show i + (j - i) = j by omega] at hc
    omega
  · have hc := chain_down h p dec (k - j) j (by omega)
    rw [show j + (k - j) = k by omega] at hc
    omega

/-! ## E8. Uniqueness: two polynomial families satisfying the cleared equation agree

    For ANY Gram matrix G and vector a such that (b,b)/2 >= 1 at every nonzero b of the box and
    every (q)_b has constant term 1, two families satisfying `ClearedEq1 G a` have the same
    coefficients at every b of the box.  The proof never divides: P_b (q)_b (1 - q^((b,b)/2)) is
    compared coefficient by coefficient, by induction on the exponent and on the height of b.
    This is the cancellation of the nonzero polynomial (q)_b (1 - q^((b,b)/2)) in Z[q]. -/

def height : List Nat → Nat
  | [] => 0
  | x :: xs => x + height xs

theorem below_refl : ∀ (a : List Nat), Below a a
  | [] => Below.nil
  | _ :: xs => Below.cons (Nat.le_refl _) (below_refl xs)

theorem below_trans {c b : List Nat} (h1 : Below c b) : ∀ {a : List Nat}, Below b a → Below c a := by
  induction h1 with
  | nil => intro a h; exact h
  | cons hxy _ ih =>
    intro a h2
    cases h2 with
    | cons hyz hrest => exact Below.cons (Nat.le_trans hxy hyz) (ih hrest)

theorem below_height {c b : List Nat} (h : Below c b) :
    height c ≤ height b ∧ (height c = height b → c = b) := by
  induction h with
  | nil => exact ⟨Nat.le_refl _, fun _ => rfl⟩
  | @cons x y xs ys hxy _ ih =>
    obtain ⟨ih1, ih2⟩ := ih
    refine ⟨by simp only [height]; omega, fun heq => ?_⟩
    simp only [height] at heq
    have hx : x = y := by omega
    have hs : height xs = height ys := by omega
    rw [hx, ih2 hs]

theorem mybox_trans {a b c : List Nat} (hc : c ∈ mybox b) (hb : b ∈ mybox a) : c ∈ mybox a :=
  (mem_mybox a c).mpr (below_trans ((mem_mybox b c).mp hc) ((mem_mybox a b).mp hb))

theorem height_lt_of_mem {b c : List Nat} (hc : c ∈ mybox b) (hne : c ≠ b) : height c < height b := by
  obtain ⟨h1, h2⟩ := below_height ((mem_mybox b c).mp hc)
  exact Nat.lt_of_le_of_ne h1 (fun heq => hne (h2 heq))

/-- Coefficient n of the term indexed by c only sees coefficients k of P_c with k + (c,c)/2 <= n. -/
theorem cf_term_congr (G : GramM) (P P' : List Nat → Pol) (b c : List Nat) (n : Nat)
    (h : ∀ k, k + halfNorm G c ≤ n → cf (P c) k = cf (P' c) k) :
    cf (term G P b c) n = cf (term G P' b c) n := by
  unfold term
  rw [cf_pmul, cf_pmul]
  apply csum_congr
  intro i hi
  by_cases hie : i = halfNorm G c
  · rw [cf_pmul, cf_pmul]
    congr 1
    apply csum_congr
    intro k hk
    rw [h k (by omega)]
  · rw [cf_mono_ne _ _ hie, Int.zero_mul, Int.zero_mul]

/-- If X Q and X' Q have the same coefficient m, Q has constant term 1 and X, X' agree below m,
    then X and X' agree at m. -/
theorem cauchy_top (X X' Q : Nat → Int) (m : Nat) (hQ0 : Q 0 = 1)
    (hlow : ∀ i, i < m → X i = X' i)
    (hs : csum m (fun i => X i * Q (m - i)) = csum m (fun i => X' i * Q (m - i))) :
    X m = X' m := by
  cases m with
  | zero =>
    have hs' : X 0 * Q (0 - 0) = X' 0 * Q (0 - 0) := hs
    rw [Nat.sub_self, hQ0, Int.mul_one, Int.mul_one] at hs'
    exact hs'
  | succ m =>
    have hs' : csum m (fun i => X i * Q (m + 1 - i)) + X (m + 1) * Q (m + 1 - (m + 1))
        = csum m (fun i => X' i * Q (m + 1 - i)) + X' (m + 1) * Q (m + 1 - (m + 1)) := hs
    have hc : csum m (fun i => X i * Q (m + 1 - i)) = csum m (fun i => X' i * Q (m + 1 - i)) :=
      csum_congr m _ _ (fun i hi => by rw [hlow i (by omega)])
    rw [hc, Nat.sub_self, hQ0, Int.mul_one, Int.mul_one] at hs'
    omega

theorem cleared_core (G : GramM) (a : List Nat) (P P' : List Nat → Pol)
    (hE : ∀ b ∈ mybox a, b ≠ zeroVec a → 1 ≤ halfNorm G b)
    (hQ : ∀ b ∈ mybox a, cf (qfac G b) 0 = 1)
    (h : ClearedEq1 G a P) (h' : ClearedEq1 G a P') (m : Nat)
    (hprev : ∀ k, k < m → ∀ b ∈ mybox a, cf (P b) k = cf (P' b) k) :
    ∀ s, ∀ b ∈ mybox a, height b < s → cf (P b) m = cf (P' b) m := by
  intro s
  induction s with
  | zero => intro b _ hs; exact absurd hs (Nat.not_lt_zero _)
  | succ s ih =>
    intro b hb hs
    by_cases hz : b = zeroVec a
    · rw [hz, peq_cf _ _ h.1 m, peq_cf _ _ h'.1 m]
    · have he : 1 ≤ halfNorm G b := hE b hb hz
      have e1 := peq_cf _ _ (h.2 b hb) m
      have e2 := peq_cf _ _ (h'.2 b hb) m
      have hr : cf (clearedRhs G P b) m = cf (clearedRhs G P' b) m := by
        unfold clearedRhs
        apply cf_psum_congr
        intro c hc
        apply cf_term_congr
        intro k hk
        have hca : c ∈ mybox a := mybox_trans hc hb
        by_cases hcb : c = b
        · rw [hcb] at hk
          rw [hcb]
          exact hprev k (by omega) b hb
        · have hlt := height_lt_of_mem hc hcb
          by_cases hkm : k < m
          · exact hprev k hkm c hca
          · have hkeq : k = m := by omega
            rw [hkeq]
            exact ih c hca (by omega)
      have hl : cf (pmul (P b) (qfac G b)) m = cf (pmul (P' b) (qfac G b)) m :=
        e1.trans (hr.trans e2.symm)
      rw [cf_pmul, cf_pmul] at hl
      exact cauchy_top (cf (P b)) (cf (P' b)) (cf (qfac G b)) m (hQ b hb)
        (fun i hi => hprev i hi b hb) hl

theorem cleared_coeff_unique (G : GramM) (a : List Nat) (P P' : List Nat → Pol)
    (hE : ∀ b ∈ mybox a, b ≠ zeroVec a → 1 ≤ halfNorm G b)
    (hQ : ∀ b ∈ mybox a, cf (qfac G b) 0 = 1)
    (h : ClearedEq1 G a P) (h' : ClearedEq1 G a P') :
    ∀ n m, m ≤ n → ∀ b ∈ mybox a, cf (P b) m = cf (P' b) m := by
  intro n
  induction n with
  | zero =>
    intro m hm0 b hb
    have hm : m = 0 := by omega
    subst hm
    exact cleared_core G a P P' hE hQ h h' 0 (fun k hk => absurd hk (Nat.not_lt_zero k))
      (height b + 1) b hb (Nat.lt_succ_self _)
  | succ n ih =>
    intro m hmn b hb
    by_cases hle : m ≤ n
    · exact ih m hle b hb
    · exact cleared_core G a P P' hE hQ h h' m
        (fun k hk c hc => ih k (by omega) c hc) (height b + 1) b hb (Nat.lt_succ_self _)

/-- UNIQUENESS in Z[q]: two families satisfying the cleared equation (1) on the box of a, with
    P_0 = 1, have the same coefficient function at every b of the box; in particular at a. -/
theorem cleared_unique (G : GramM) (a : List Nat) (P P' : List Nat → Pol)
    (hE : ∀ b ∈ mybox a, b ≠ zeroVec a → 1 ≤ halfNorm G b)
    (hQ : ∀ b ∈ mybox a, cf (qfac G b) 0 = 1)
    (h : ClearedEq1 G a P) (h' : ClearedEq1 G a P') :
    ∀ b ∈ mybox a, cf (P b) = cf (P' b) := by
  intro b hb
  funext n
  exact cleared_coeff_unique G a P P' hE hQ h h' n n (Nat.le_refl n) b hb

/-- The two hypotheses of `cleared_unique` at the three witnesses, by kernel evaluation. -/
theorem b2_side : (∀ b ∈ mybox [2, 2], b ≠ zeroVec [2, 2] → 1 ≤ halfNorm Toda.B2 b) ∧
    (∀ b ∈ mybox [2, 2], cf (qfac Toda.B2 b) 0 = 1) := by decide +kernel
theorem b3_110_side : (∀ b ∈ mybox [1, 1, 0], b ≠ zeroVec [1, 1, 0] → 1 ≤ halfNorm Toda.B3 b) ∧
    (∀ b ∈ mybox [1, 1, 0], cf (qfac Toda.B3 b) 0 = 1) := by decide +kernel
theorem b3_211_side : (∀ b ∈ mybox [2, 1, 1], b ≠ zeroVec [2, 1, 1] → 1 ≤ halfNorm Toda.B3 b) ∧
    (∀ b ∈ mybox [2, 1, 1], cf (qfac Toda.B3 b) 0 = 1) := by decide +kernel

theorem top_mem (a : List Nat) : a ∈ mybox a := (mem_mybox a a).mpr (below_refl a)

/-- Second witness: EVERY polynomial family satisfying the cleared equation (1) on the box of (2,2)
    in B_2 has the numerator 1 + q + 3q^2 + 2q^3 + 5q^4 + 2q^5 + 3q^6 + q^7 + q^8, as a whole
    polynomial. -/
theorem b2_every_family (P : List Nat → Pol) (h : ClearedEq1 Toda.B2 [2, 2] P) :
    cf (P [2, 2]) = cf [1, 1, 3, 2, 5, 2, 3, 1, 1] := by
  rw [← PB2_top]
  exact cleared_unique Toda.B2 [2, 2] P PB2 b2_side.1 b2_side.2 h b2_cleared [2, 2] (top_mem _)

theorem b3_110_every_family (P : List Nat → Pol) (h : ClearedEq1 Toda.B3 [1, 1, 0] P) :
    cf (P [1, 1, 0]) = cf [1, 0, 1] := by
  rw [← PB3_110_top]
  exact cleared_unique Toda.B3 [1, 1, 0] P PB3_110 b3_110_side.1 b3_110_side.2 h b3_110_cleared
    [1, 1, 0] (top_mem _)

theorem b3_211_every_family (P : List Nat → Pol) (h : ClearedEq1 Toda.B3 [2, 1, 1] P) :
    cf (P [2, 1, 1]) = cf [1, 2, 4, 3, 4, 2, 1] := by
  rw [← PB3_211_top]
  exact cleared_unique Toda.B3 [2, 1, 1] P PB3_211 b3_211_side.1 b3_211_side.2 h b3_211_cleared
    [2, 1, 1] (top_mem _)

/-- At B_2, (2,2), NO family satisfying the cleared equation has a regraded-unimodal numerator. -/
theorem b2_no_family_regraded (P : List Nat → Pol) (h : ClearedEq1 Toda.B2 [2, 2] P) :
    ¬ RegradedValleyFree (cf (P [2, 2])) := by
  rw [b2_every_family P h]
  exact not_regraded_of_dip _ 2 (by decide) (by decide) (by decide)

/-- At the recorded witness EVERY family satisfying the cleared equation has a regraded-unimodal
    numerator: the recorded witness cannot refute `Conjecture73_exact`, whichever family is taken. -/
theorem b3_110_every_family_regraded (P : List Nat → Pol) (h : ClearedEq1 Toda.B3 [1, 1, 0] P) :
    RegradedValleyFree (cf (P [1, 1, 0])) := by
  rw [b3_110_every_family P h, ← PB3_110_top]
  exact b3_110_is_regraded

/-! ## E9. Cross-checks against the certificate above (not used by the headline) -/

theorem below_iff_vle {b a : List Nat} : Below b a ↔ Toda.VLe b a := by
  constructor
  · intro h
    induction h with
    | nil => exact Toda.VLe.nil
    | cons hxy _ ih => exact Toda.VLe.cons hxy ih
  · intro h
    induction h with
    | nil => exact Below.nil
    | cons hxy _ ih => exact Below.cons hxy ih

/-- The two enumerations of the box have the same members (they differ in order). -/
theorem mem_mybox_iff_mem_box (a b : List Nat) : b ∈ mybox a ↔ b ∈ Toda.box a := by
  rw [mem_mybox, Toda.mem_box, below_iff_vle]

/-- The certificate's peak-form unimodality implies `ValleyFree`, with and without regrading. -/
theorem valleyFree_of_unimodalSeq (h : Nat → Int) (hu : Toda.UnimodalSeq h) : ValleyFree h :=
  valleyFree_of_peak h hu

theorem regradedValleyFree_of_regradedUnimodal (h : Nat → Int) (hu : Toda.RegradedUnimodal h) :
    RegradedValleyFree h := by
  obtain ⟨e, he, hdiv, hs⟩ := hu
  exact ⟨e, he, hdiv, valleyFree_of_peak _ hs⟩

/-- Own (b,b)/2 and d_i agree with the certificate's at the three witnesses. -/
theorem halfNorm_agrees :
    (mybox [2, 2]).map (halfNorm Toda.B2) = (mybox [2, 2]).map (Toda.energy Toda.B2) ∧
    (mybox [1, 1, 0]).map (halfNorm Toda.B3) = (mybox [1, 1, 0]).map (Toda.energy Toda.B3) ∧
    (mybox [2, 1, 1]).map (halfNorm Toda.B3) = (mybox [2, 1, 1]).map (Toda.energy Toda.B3) ∧
    (List.range 2).map (dd Toda.B2) = Toda.dvec Toda.B2 ∧
    (List.range 3).map (dd Toda.B3) = Toda.dvec Toda.B3 := by decide +kernel

/-- The exact numerators, cut at q^12, are the certificate's truncated numerators. -/
theorem exact_agrees_with_truncated :
    (List.range 13).map (cf (PB2 [2, 2])) = Toda.Htr 12 Toda.B2 [2, 2] ∧
    (List.range 13).map (cf (PB3_110 [1, 1, 0])) = Toda.Htr 12 Toda.B3 [1, 1, 0] ∧
    (List.range 13).map (cf (PB3_211 [2, 1, 1])) = Toda.Htr 12 Toda.B3 [2, 1, 1] := by
  rw [Toda.b2_H, Toda.b3_H, Toda.b3_211_H]
  decide +kernel

/-- Own (q)_b, cut at q^12, is the certificate's (q)_b at every state of the three boxes. -/
theorem qfac_agrees :
    (∀ b ∈ mybox [2, 2],
      (List.range 13).map (cf (qfac Toda.B2 b)) = Toda.qfacT 12 (Toda.dvec Toda.B2) b) ∧
    (∀ b ∈ mybox [2, 1, 1],
      (List.range 13).map (cf (qfac Toda.B3 b)) = Toda.qfacT 12 (Toda.dvec Toda.B3) b) := by
  decide +kernel

/-- P_b/(q)_b^2 modulo q^13 (inverses as in the certificate) is the certificate's computed family
    J_b at every state: the exact numerators and the truncated computation describe the same
    rational functions to the order the certificate works at. -/
theorem exact_family_is_certificate_family :
    (∀ b ∈ mybox [2, 2],
      Toda.mulT 12 (PB2 b) (Toda.mulT 12 (Toda.invQfacT 12 (Toda.dvec Toda.B2) b)
        (Toda.invQfacT 12 (Toda.dvec Toda.B2) b)) = Toda.Jfam 12 Toda.B2 [2, 2] b) ∧
    (∀ b ∈ mybox [1, 1, 0],
      Toda.mulT 12 (PB3_110 b) (Toda.mulT 12 (Toda.invQfacT 12 (Toda.dvec Toda.B3) b)
        (Toda.invQfacT 12 (Toda.dvec Toda.B3) b)) = Toda.Jfam 12 Toda.B3 [1, 1, 0] b) ∧
    (∀ b ∈ mybox [2, 1, 1],
      Toda.mulT 12 (PB3_211 b) (Toda.mulT 12 (Toda.invQfacT 12 (Toda.dvec Toda.B3) b)
        (Toda.invQfacT 12 (Toda.dvec Toda.B3) b)) = Toda.Jfam 12 Toda.B3 [2, 1, 1] b) := by
  decide +kernel

/-- Positive controls: the source's printed type A examples satisfy the cleared equation
    (Example 1.1: [4 choose 2]_q; Example 1.3: the Narayana polynomial 1 + 3q + q^2). -/
def PA2 : List Nat → Pol := fromTable
  [([0, 0], [1]), ([0, 1], [1]), ([0, 2], [1]), ([1, 0], [1]), ([2, 0], [1]),
   ([1, 1], [1, 1]), ([1, 2], [1, 1, 1]), ([2, 1], [1, 1, 1]), ([2, 2], [1, 1, 2, 1, 1])]

def PA3 : List Nat → Pol := fromTable
  [([0, 0, 0], [1]), ([0, 0, 1], [1]), ([0, 1, 0], [1]), ([1, 0, 0], [1]), ([1, 0, 1], [1]),
   ([0, 1, 1], [1, 1]), ([1, 1, 0], [1, 1]), ([1, 1, 1], [1, 3, 1])]

theorem a2_cleared : ClearedEq1 Toda.A2 [2, 2] PA2 := by
  unfold ClearedEq1; decide +kernel

theorem a3_cleared : ClearedEq1 Toda.A3 [1, 1, 1] PA3 := by
  unfold ClearedEq1; decide +kernel

end Exact

#print axioms Exact.not_conjecture73_exact
#print axioms Exact.b2_cleared
#print axioms Exact.b3_110_cleared
#print axioms Exact.b3_211_cleared
#print axioms Exact.PB2_top
#print axioms Exact.PB3_110_top
#print axioms Exact.PB3_211_top
#print axioms Exact.b2_quotients
#print axioms Exact.b3_110_quotients
#print axioms Exact.b3_211_quotients
#print axioms Exact.b2_data
#print axioms Exact.b3_data
#print axioms Exact.b2_dip_displayed
#print axioms Exact.not_regraded_of_dip
#print axioms Exact.b3_211_not_regraded
#print axioms Exact.onePlusQ2_tail
#print axioms Exact.b3_110_regraded_with_e2
#print axioms Exact.b3_110_is_regraded
#print axioms Exact.b3_110_literal_dip
#print axioms Exact.cf_nil
#print axioms Exact.cf_eq_getD
#print axioms Exact.cf_padd
#print axioms Exact.cf_pscale
#print axioms Exact.csum_congr
#print axioms Exact.csum_zero
#print axioms Exact.csum_shift
#print axioms Exact.cf_pmul
#print axioms Exact.cf_mono_ne
#print axioms Exact.cf_mono_self
#print axioms Exact.allZero_cf
#print axioms Exact.peq_cf
#print axioms Exact.cf_allZero
#print axioms Exact.cf_peq
#print axioms Exact.peq_iff
#print axioms Exact.cf_psum_congr
#print axioms Exact.mem_upTo
#print axioms Exact.mem_mybox
#print axioms Exact.chain_up
#print axioms Exact.chain_down
#print axioms Exact.valleyFree_of_peak
#print axioms Exact.below_refl
#print axioms Exact.below_trans
#print axioms Exact.below_height
#print axioms Exact.mybox_trans
#print axioms Exact.height_lt_of_mem
#print axioms Exact.cf_term_congr
#print axioms Exact.cauchy_top
#print axioms Exact.cleared_core
#print axioms Exact.cleared_coeff_unique
#print axioms Exact.cleared_unique
#print axioms Exact.b2_side
#print axioms Exact.b3_110_side
#print axioms Exact.b3_211_side
#print axioms Exact.top_mem
#print axioms Exact.b2_every_family
#print axioms Exact.b3_110_every_family
#print axioms Exact.b3_211_every_family
#print axioms Exact.b2_no_family_regraded
#print axioms Exact.b3_110_every_family_regraded
#print axioms Exact.below_iff_vle
#print axioms Exact.mem_mybox_iff_mem_box
#print axioms Exact.valleyFree_of_unimodalSeq
#print axioms Exact.regradedValleyFree_of_regradedUnimodal
#print axioms Exact.halfNorm_agrees
#print axioms Exact.exact_agrees_with_truncated
#print axioms Exact.qfac_agrees
#print axioms Exact.exact_family_is_certificate_family
#print axioms Exact.a2_cleared
#print axioms Exact.a3_cleared
