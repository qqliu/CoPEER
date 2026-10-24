import HumanReviewAxiomAudit
/-!
# SE_math_4219732__q — the displayed chain of rational equalities fails

* Source: https://math.stackexchange.com/questions/4219732
* Route: `SELF_CONTAINED_LEAN` (core Lean 4, no imports)

## Claim component modeled

The source joins several parameterized rational expressions by equality.  At
the admissible assignment `(n,b,c,f) = (5,1,1,2)`, their exact values are
`1/10`, `5/108`, `25/4`, `1/16`, and `1/8`; hence the chain is false.

## Modelling judgments

Fractions are stored as numerator/positive denominator pairs.  Equality is
cross multiplication, so no division, floating point, normalization axiom, or
library is trusted.  The expressions below reproduce the arithmetic before
reduction.  The negative control checks two different representations of the
same fraction, ensuring that `fracEq` is not merely rejecting every pair.
-/

set_option maxRecDepth 10000
set_option maxHeartbeats 4000000

namespace SE_math_4219732_q

structure Frac where
  num : Nat
  den : Nat
  deriving DecidableEq

def fracEq (a b : Frac) : Bool := decide (a.den > 0 ∧ b.den > 0 ∧ a.num * b.den = b.num * a.den)

def mul (a b : Frac) : Frac := ⟨a.num * b.num, a.den * b.den⟩

def pow : Frac → Nat → Frac
  | _, 0 => ⟨1, 1⟩
  | a, k + 1 => mul a (pow a k)

def trueLhs : Frac := mul ⟨10, 1⟩ (pow ⟨2, 20⟩ 2)
def substitutedLhs : Frac := mul (pow ⟨5, 3⟩ 3) (pow ⟨2, 20⟩ 2)
def firstRhs : Frac := mul ⟨5^3, 3^3⟩ ⟨3^3, 2^2 * 1 * 5⟩
def secondRhs : Frac := mul ⟨5, 1⟩ ⟨1, 4^2 * 5⟩
def finalRhs : Frac := ⟨1, 4 * 2⟩

def printedChain : Bool :=
  fracEq trueLhs firstRhs
  && fracEq firstRhs secondRhs
  && fracEq secondRhs finalRhs

/-- **Main certificate.**  All parameters are admissible, but the equality chain fails. -/
theorem SE_math_4219732__q_refuted :
    decide (5 ≥ 2 * 1 + 1 ∧ 1 ≥ 1 ∧ 2 ≥ 1) = true
    ∧ fracEq trueLhs ⟨1, 10⟩ = true
    ∧ fracEq substitutedLhs ⟨5, 108⟩ = true
    ∧ fracEq firstRhs ⟨25, 4⟩ = true
    ∧ fracEq secondRhs ⟨1, 16⟩ = true
    ∧ fracEq finalRhs ⟨1, 8⟩ = true
    ∧ printedChain = false := by decide

/-- Negative control: cross multiplication accepts equivalent, unreduced fractions. -/
theorem negative_control_fraction_equality :
    fracEq ⟨1, 10⟩ ⟨2, 20⟩ = true := by decide

end SE_math_4219732_q

#human_review_axiom_audit
