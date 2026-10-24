/-!
Record: proofwiki_74347__codex_expansion
Source: ProofWiki, "Representation of Integers in Balanced Ternary"
https://proofwiki.org/wiki/Representation_of_Integers_in_Balanced_Ternary

Exact scope: this certificate refutes the source's asserted material existence
step, "For every integer n, there exists a nonnegative integer m such that
3^m + 1 ≤ |2n| ≤ 3^(m+1) − 1."  It does not refute the balanced-ternary
representation theorem itself: zero can instead be handled separately.

Terra-confirmed witness: `n = 0`.  This satisfies the sole outer hypothesis
that `n` is an integer.  For every permitted nonnegative exponent `m`, the
left endpoint is `3^m + 1`, a successor and hence not at most
`|2 * 0| = 0`.  Thus no admissible `m` exists.  The proof retains the genuinely
unbounded quantifier over all nonnegative exponents; it is not a bounded
enumeration.  Consequently the witness also survives any stricter requirement
that the exponent be positive, without conflating that requirement with the
quoted local condition `m ≥ 0`.

Modelling judgments: source integers are Lean `Int`; a nonnegative integer
exponent is represented exactly by `Nat`; absolute value is `Int.natAbs`; and
the two bounds use `Nat` powers and inequalities exactly as directed by the
semantic-source audit.  The final subtraction is natural-number subtraction;
here this agrees with the intended nonnegative integer value because
`3^(m+1) ≥ 1`.  No floating-point absolute value or weakened premise is used.
Typed quantification records both load-bearing domain hypotheses rather than
assuming them outside the proposition.

Independent control: `n = 1`, `m = 0` is permitted by the source's local
nonnegative-exponent condition and gives the exact closed bounds
`2 ≤ |2| = 2 ≤ 2`.  The separate negative-control theorem checks the
admissibility predicate and all three computed values, detecting a vacuous
predicate or uniformly false conclusion.  This control is not claimed for a
different positive-exponent formulation.  The public maintenance evidence
discusses uniqueness and gives no exhibited witness for this failed existence
step; the certificate therefore addresses only the literal necessary step
identified by the semantic audit.

All proofs use only Lean's core kernel.  Closed control arithmetic is discharged
componentwise by kernel `decide`; the unbounded refutation is a small explicit
kernel proof.
-/

namespace ProofWiki74347CodexExpansion

/-- The source's two simultaneous bounds for an integer `n` and a permitted
nonnegative exponent `m`. -/
def Admissible (n : Int) (m : Nat) : Prop :=
  (3 : Nat) ^ m + 1 ≤ Int.natAbs (2 * n) /\
  Int.natAbs (2 * n) ≤ (3 : Nat) ^ (m + 1) - 1

/-- The verified witness fails for every admissible exponent, and therefore
refutes the literal universal existence claim used by the source. -/
theorem refutes_published_universal_interval_claim :
    (¬ ∃ m : Nat, Admissible (0 : Int) m) /\
    ¬ (∀ n : Int, ∃ m : Nat, Admissible n m) := by
  have zeroHasNoExponent : ¬ ∃ m : Nat, Admissible (0 : Int) m := by
    intro h
    cases h with
    | intro m hm =>
        have impossible : (3 : Nat) ^ m + 1 ≤ 0 := hm.1
        exact Nat.not_succ_le_zero ((3 : Nat) ^ m) impossible
  constructor
  · exact zeroHasNoExponent
  · intro universalClaim
    exact zeroHasNoExponent (universalClaim (0 : Int))

/-- Meaningful negative control: the independently checked source-valid pair
`n = 1`, `m = 0` realizes both bounds, with every relevant value exposed. -/
theorem negative_control_n_one_m_zero :
    Admissible (1 : Int) 0 /\
    Int.natAbs (2 * (1 : Int)) = 2 /\
    (3 : Nat) ^ 0 + 1 = 2 /\
    (3 : Nat) ^ (0 + 1) - 1 = 2 := by
  constructor
  · unfold Admissible
    constructor
    · decide
    · decide
  · constructor
    · decide
    · constructor
      · decide
      · decide

end ProofWiki74347CodexExpansion
