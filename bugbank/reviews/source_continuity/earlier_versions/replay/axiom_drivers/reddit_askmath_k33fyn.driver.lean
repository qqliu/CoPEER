/-!
Record: reddit_askmath_k33fyn
Public source: https://www.reddit.com/r/askmath/comments/k33fyn/proofs_using_unique_prime_factorizations/

Exact target scope: the source proof applies a prime-factorization theorem stated
for integers greater than `1` to every odd integer `x`, and therefore assumes a
displayed nonempty product of primes for every such `x`.  The concrete witness
is the allowed odd integer `x = 1`: its factor list is empty, with empty product
`1`, while every nonempty list of positive natural primes has product at least
`2`.  The independently verified negative control is `x = 3`, represented by
the nonempty factor list `[3]`.

Modelling judgments: `x` ranges over `Int`; oddness means `x = 2*k + 1` for an
integer `k`; factors range over `Nat`; natural divisibility is witnessed by a
natural quotient; and a natural prime has lower bound `2` and no divisors other
than `1` and itself.  List multiplication is recursive with empty product `1`,
and `Factorized` explicitly requires a nonempty all-prime list whose natural
product is embedded into `Int` with `Int.ofNat`.  Thus this model is the
positive-prime product displayed by the source, not a signed factorization and
not a finite prime lookup table.  `FTAApplicable x` records only the theorem's
material side condition `1 < x`: it excludes the unit witness and accepts the
odd control `3`; no full fundamental-theorem-of-arithmetic result is asserted.
The units and negative odd integers require separate handling rather than being
silently included in this positive factorization model.
-/

namespace RedditAskmathK33fyn

def OddInt (x : Int) : Prop :=
  ∃ k : Int, x = 2 * k + 1

def NatDivides (d n : Nat) : Prop :=
  ∃ q : Nat, n = d * q

def PrimeNat (p : Nat) : Prop :=
  2 ≤ p ∧ ∀ d : Nat, NatDivides d p → d = 1 ∨ d = p

def product : List Nat → Nat
  | [] => 1
  | p :: ps => p * product ps

def AllPrime : List Nat → Prop
  | [] => True
  | p :: ps => PrimeNat p ∧ AllPrime ps

def Factorized (x : Int) : Prop :=
  ∃ ps : List Nat,
    ps ≠ [] ∧ AllPrime ps ∧ x = Int.ofNat (product ps)

def FTAApplicable (x : Int) : Prop :=
  1 < x

theorem product_pos_of_allPrime :
    ∀ ps : List Nat, AllPrime ps → 0 < product ps
  | [], _ => by decide
  | p :: ps, hall => by
      exact Nat.mul_pos
        (Nat.lt_of_lt_of_le (by decide : 0 < 2) hall.1.1)
        (product_pos_of_allPrime ps hall.2)

theorem nonempty_allPrime_product_ge_two
    (ps : List Nat) (hne : ps ≠ []) (hall : AllPrime ps) :
    2 ≤ product ps := by
  cases ps with
  | nil => exact False.elim (hne rfl)
  | cons p rest =>
      have hp : 2 ≤ p := hall.1.1
      have hrest : 0 < product rest :=
        product_pos_of_allPrime rest hall.2
      have hp_le_product : p ≤ p * product rest := by
        have hmul := Nat.mul_le_mul_left p hrest
        simpa using hmul
      exact Nat.le_trans hp hp_le_product

theorem positive_le_three_cases
    (n : Nat) (hpos : 0 < n) (hle : n ≤ 3) :
    n = 1 ∨ n = 2 ∨ n = 3 := by
  cases n with
  | zero => simp at hpos
  | succ n =>
      cases n with
      | zero => exact Or.inl rfl
      | succ n =>
          cases n with
          | zero => exact Or.inr (Or.inl rfl)
          | succ n =>
              cases n with
              | zero => exact Or.inr (Or.inr rfl)
              | succ n => simp at hle

theorem primeNat_three : PrimeNat 3 := by
  constructor
  · decide
  · intro d hd
    rcases hd with ⟨q, hproduct⟩
    have hdpos : 0 < d := by
      cases d with
      | zero => simp at hproduct
      | succ d => exact Nat.zero_lt_succ d
    have hqpos : 0 < q := by
      cases q with
      | zero => simp at hproduct
      | succ q => exact Nat.zero_lt_succ q
    have hdle : d ≤ 3 := by
      calc
        d = d * 1 := by simp
        _ ≤ d * q := Nat.mul_le_mul_left d hqpos
        _ = 3 := hproduct.symm
    have hqle : q ≤ 3 := by
      calc
        q = q * 1 := by simp
        _ ≤ q * d := Nat.mul_le_mul_left q hdpos
        _ = d * q := Nat.mul_comm q d
        _ = 3 := hproduct.symm
    rcases positive_le_three_cases d hdpos hdle with hd | hd | hd
    · subst d
      exact Or.inl rfl
    · subst d
      rcases positive_le_three_cases q hqpos hqle with hq | hq | hq
      · subst q
        simp at hproduct
      · subst q
        simp at hproduct
      · subst q
        simp at hproduct
    · subst d
      exact Or.inr rfl

theorem oddInt_one : OddInt 1 := by
  refine ⟨0, ?_⟩
  decide

theorem not_factorized_one : ¬ Factorized 1 := by
  intro hfactor
  rcases hfactor with ⟨ps, hne, hall, heq⟩
  have hge : 2 ≤ product ps :=
    nonempty_allPrime_product_ge_two ps hne hall
  have hproduct : product ps = 1 := by
    have habs := congrArg Int.natAbs heq
    simpa using habs.symm
  rw [hproduct] at hge
  exact (by decide : ¬ (2 ≤ 1)) hge

theorem refutes_published_universal_step :
    ¬ (∀ x : Int, OddInt x → Factorized x) := by
  intro published
  exact not_factorized_one (published 1 oddInt_one)

/-- Load-bearing refutation of the literal universal proof step: `1` satisfies
the source's odd-integer premise, fails the required nonempty positive-prime
factorization, and is outside the stated theorem's `1 < x` applicability scope.
-/
theorem reddit_askmath_k33fyn_refutation :
    OddInt 1 ∧
    ¬ Factorized 1 ∧
    ¬ FTAApplicable 1 ∧
    ¬ (∀ x : Int, OddInt x → Factorized x) := by
  refine ⟨oddInt_one, not_factorized_one, ?_,
    refutes_published_universal_step⟩
  change ¬ ((1 : Int) < 1)
  decide

/-- Meaningful negative control: the same oddness and positive-factorization
encoding accepts `3`, with the genuine nonempty prime list `[3]`, and `3` is
inside the corrected applicability scope. -/
theorem reddit_askmath_k33fyn_negative_control :
    OddInt 3 ∧ PrimeNat 3 ∧ Factorized 3 ∧ FTAApplicable 3 := by
  constructor
  · refine ⟨1, ?_⟩
    decide
  constructor
  · exact primeNat_three
  constructor
  · refine ⟨[3], ?_, ?_, ?_⟩
    · decide
    · exact ⟨primeNat_three, True.intro⟩
    · decide
  · change (1 : Int) < 3
    decide

end RedditAskmathK33fyn

#print axioms RedditAskmathK33fyn.product_pos_of_allPrime
#print axioms RedditAskmathK33fyn.nonempty_allPrime_product_ge_two
#print axioms RedditAskmathK33fyn.positive_le_three_cases
#print axioms RedditAskmathK33fyn.primeNat_three
#print axioms RedditAskmathK33fyn.oddInt_one
#print axioms RedditAskmathK33fyn.not_factorized_one
#print axioms RedditAskmathK33fyn.refutes_published_universal_step
#print axioms RedditAskmathK33fyn.reddit_askmath_k33fyn_refutation
#print axioms RedditAskmathK33fyn.reddit_askmath_k33fyn_negative_control
