/-!
Record: reddit_askmath_1kehuzl
Public URL:
https://www.reddit.com/r/askmath/comments/1kehuzl/is_there_a_formalism_where_the_set_of_naturals_is/

Exact target scope: the proposed map from the even natural numbers to all
two-element sets of natural numbers, n ↦ {n, n+1}, is a bijection.

Concrete refuting codomain witness: {0,2}.  It is a genuine two-element set,
but every image is a consecutive pair.  More explicitly, if an image contains
0, then 0 = n or 0 = n+1.  The successor case is impossible; the first case
forces n = 0, whose image contains 1 although {0,2} does not.  Thus {0,2} has
no preimage, so the proposed map is not surjective and hence not bijective.
The independently verified negative control is the attained pair {2,3}, with
even preimage 2.

Material modelling judgments: this is the actual unbounded `Nat` model, not a
finite proxy.  A set is its membership predicate `Nat → Prop`; `Pair a b`
is the unordered predicate x = a ∨ x = b; and `SetEq` is pointwise logical
equivalence, avoiding function extensionality.  `TwoElem` requires distinct
witnesses and extensional equality with their pair.  `Even n` literally means
∃ k, n = k+k.  `Image n` is `Pair n (n+1)`.  Surjectivity quantifies over
every predicate satisfying `TwoElem` and requires an even preimage with equal
image.  Injectivity is restricted to even inputs, and `Bijection` contains both
that injectivity statement and the stated surjectivity.  The well-definedness
theorem records that every even input lands in the two-element codomain; the
negative control records the real domain condition, codomain condition, and
image equality rather than merely checking an isolated arithmetic identity.

Route review: `SELF_CONTAINED_LEAN` is appropriate because Lean core can
represent the actual infinite source structure directly with unbounded `Nat`
and predicates `Nat → Prop`.  No finite analogue, imported set library, or
weakened witness proposition is needed.  This file intentionally has zero
imports and uses only explicit kernel-checked proofs.
-/

namespace RedditAskmath1kehuzl

def Pair (a b x : Nat) : Prop :=
  x = a ∨ x = b

def SetEq (P Q : Nat → Prop) : Prop :=
  ∀ x, P x ↔ Q x

def TwoElem (P : Nat → Prop) : Prop :=
  ∃ a b, a ≠ b ∧ SetEq P (Pair a b)

def Even (n : Nat) : Prop :=
  ∃ k, n = k + k

def Image (n : Nat) : Nat → Prop :=
  Pair n (n + 1)

def Surjective : Prop :=
  ∀ P : Nat → Prop, TwoElem P →
    ∃ n : Nat, Even n ∧ SetEq (Image n) P

def Injective : Prop :=
  ∀ m n : Nat, Even m → Even n →
    SetEq (Image m) (Image n) → m = n

def Bijection : Prop :=
  Injective ∧ Surjective

theorem nat_ne_add_one (n : Nat) : n ≠ n + 1 := by
  induction n with
  | zero =>
      intro h
      cases h
  | succ n ih =>
      intro h
      apply ih
      exact Nat.succ.inj h

/-- Every input from the stated even-natural domain genuinely lands in the
stated codomain of two-element sets. -/
theorem image_is_two_element (n : Nat) (_hn : Even n) :
    TwoElem (Image n) := by
  refine ⟨n, n + 1, nat_ne_add_one n, ?_⟩
  intro x
  exact Iff.rfl

theorem witness_is_two_element : TwoElem (Pair 0 2) := by
  refine ⟨0, 2, ?_, ?_⟩
  · intro h
    cases h
  · intro x
    exact Iff.rfl

/- Core does not need a synthesized `Decidable` instance for this custom
predicate: the two impossible numeral equalities are eliminated explicitly. -/
theorem one_is_not_in_witness : ¬ Pair 0 2 1 := by
  intro h
  cases h with
  | inl oneEqZero =>
      cases oneEqZero
  | inr oneEqTwo =>
      cases oneEqTwo

theorem witness_has_no_even_preimage :
    ¬ ∃ n : Nat, Even n ∧ SetEq (Image n) (Pair 0 2) := by
  intro h
  cases h with
  | intro n hPreimage =>
      cases hPreimage with
      | intro hn hEq =>
          have imageContainsZero : Image n 0 :=
            (hEq 0).mpr (Or.inl rfl)
          cases imageContainsZero with
          | inl zeroEqN =>
              cases zeroEqN
              have targetContainsOne : Pair 0 2 1 :=
                (hEq 1).mp (Or.inr rfl)
              exact one_is_not_in_witness targetContainsOne
          | inr zeroEqSucc =>
              cases zeroEqSucc

theorem claimed_surjectivity_fails : ¬ Surjective := by
  intro hSurjective
  exact witness_has_no_even_preimage
    (hSurjective (Pair 0 2) witness_is_two_element)

/-- Load-bearing refutation of the literal published bijection claim: the
codomain witness {0,2} is valid, has no even preimage, and therefore falsifies
both the full surjectivity proposition and the stated bijection proposition. -/
theorem refutes_claimed_bijection :
    TwoElem (Pair 0 2) ∧
    (¬ ∃ n : Nat, Even n ∧ SetEq (Image n) (Pair 0 2)) ∧
    ¬ Surjective ∧
    ¬ Bijection := by
  refine ⟨witness_is_two_element, witness_has_no_even_preimage,
    claimed_surjectivity_fails, ?_⟩
  intro hBijection
  exact claimed_surjectivity_fails hBijection.2

/-- Meaningful negative control: in the same unbounded model, the even input
2 really attains the valid two-element codomain member {2,3}.  This detects a
uniformly false image relation or a vacuous domain/codomain encoding. -/
theorem negative_control_consecutive_pair_is_attained :
    Even 2 ∧
    TwoElem (Pair 2 3) ∧
    SetEq (Image 2) (Pair 2 3) := by
  refine ⟨⟨1, rfl⟩, ?_, ?_⟩
  · refine ⟨2, 3, nat_ne_add_one 2, ?_⟩
    intro x
    exact Iff.rfl
  · intro x
    exact Iff.rfl

end RedditAskmath1kehuzl

#print axioms RedditAskmath1kehuzl.records
#print axioms RedditAskmath1kehuzl.nat_ne_add_one
#print axioms RedditAskmath1kehuzl.image_is_two_element
#print axioms RedditAskmath1kehuzl.witness_is_two_element
#print axioms RedditAskmath1kehuzl.one_is_not_in_witness
#print axioms RedditAskmath1kehuzl.witness_has_no_even_preimage
#print axioms RedditAskmath1kehuzl.claimed_surjectivity_fails
#print axioms RedditAskmath1kehuzl.refutes_claimed_bijection
#print axioms RedditAskmath1kehuzl.negative_control_consecutive_pair_is_attained
