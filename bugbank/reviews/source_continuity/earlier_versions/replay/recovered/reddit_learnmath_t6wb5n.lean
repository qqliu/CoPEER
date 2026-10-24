/-!
Record: reddit_learnmath_t6wb5n
Public source: https://www.reddit.com/r/learnmath/comments/t6wb5n/rational_epsilondelta_limit_proof_questions/

Exact source claim under review (the final equality in line 0013):
`|(x-2)(x+2)|/(4*x^2) = |x-2||x+2|/(x^2)`.
The source displayed it as the last step of
`|(1/x^2)-(1/4)| = |(4-x^2)/(4x^2)| = |4-x^2|/|4x^2|
 = |x^2-4|/(4x^2) = |(x-2)(x+2)|/(4x^2)
 = |x-2||x+2|/(x^2)`.

The left definition below deliberately retains the explicit factor `4`.
The numerator identity `|(x-2)(x+2)| = |x-2||x+2|` is valid and is
certified separately; it cannot erase that denominator factor.

Concrete independently verified witness: `x = 1`, with `x != 0`. Both
divisors are nonzero, the numerator identity holds, but the two source sides
are exactly `3/4` and `3`, so the final displayed equality is false.

A context-strengthened witness is also certified at `x = 3/2`,
`epsilon = 1`, and `delta = 4/5`: epsilon and delta are positive,
`delta = min(1,(4/5)*epsilon)`, `0 < |x-2| < delta`, `x != 0`, both
divisions are defined, the numerator identity holds, and the source sides are
`7/36` and `7/9`. Thus the step also fails inside the surrounding proof
neighborhood. Those neighborhood assumptions are not load-bearing for the
standalone algebraic equality, and repairability of the limit proof does not
make this local equality valid.

Negative control: `x = 2` is nonzero and both divisions are defined, but the
zero numerator makes both sides zero and masks the missing factor. This
detects a uniformly-false or vacuous encoding.

Route review and modelling judgment: `ExactRat` is an infinite, exact signed
rational model with an `Int` numerator, a positive `Nat` denominator, and
rational equivalence by cross multiplication rather than structure equality.
It implements integer constants, exact fractions, addition/subtraction,
multiplication, squaring, ordinary absolute value through `Int.natAbs`, and
division through a reciprocal whose interface requires a nonzero proof.

This model represents only the listed exact rational real witnesses. It is
not a finite-domain proxy and does not replace the source claim with a toy
finite analogue or a universal real-analysis, limit, topology, continuity, or
approximation claim. Exact rational field operations have the same values at
these rational real witnesses, so no imported real-analysis semantics are
needed. All results below are reducible kernel computations: there is no
floating point, bounded enumeration, imported tactic, or native evaluation.
-/

namespace RedditLearnmathT6wb5n

structure ExactRat where
  num : Int
  den : Nat
  den_pos : 0 < den

/- Lean's zero-import prelude does not provide the `DecidableEq Int` instance
used implicitly by the first certificate. These total Boolean comparisons
inspect the two core `Int` constructors directly. -/
def intEqual : Int -> Int -> Bool
  | Int.ofNat m, Int.ofNat n => m == n
  | Int.negSucc m, Int.negSucc n => m == n
  | _, _ => false

def intLess : Int -> Int -> Bool
  | Int.ofNat m, Int.ofNat n => decide (m < n)
  | Int.ofNat _, Int.negSucc _ => false
  | Int.negSucc _, Int.ofNat _ => true
  | Int.negSucc m, Int.negSucc n => decide (n < m)

/- Rational equivalence remains literal cross multiplication. These
Prop-valued computational predicates are abbreviations so zero-import kernel
`decide` can see their Boolean equalities while synthesizing `Decidable` in
Lean 4.30. -/
abbrev equivalent (a b : ExactRat) : Prop :=
  intEqual (a.num * Int.ofNat b.den) (b.num * Int.ofNat a.den) = true

abbrev nonzero (a : ExactRat) : Prop :=
  intEqual a.num 0 = false

def ofInt (n : Int) : ExactRat :=
  { num := n, den := 1, den_pos := by decide }

def fraction (n : Int) (d : Nat) (hd : 0 < d) : ExactRat :=
  { num := n, den := d, den_pos := hd }

def add (a b : ExactRat) : ExactRat :=
  { num := a.num * Int.ofNat b.den + b.num * Int.ofNat a.den
    den := a.den * b.den
    den_pos := Nat.mul_pos a.den_pos b.den_pos }

def sub (a b : ExactRat) : ExactRat :=
  { num := a.num * Int.ofNat b.den - b.num * Int.ofNat a.den
    den := a.den * b.den
    den_pos := Nat.mul_pos a.den_pos b.den_pos }

def mul (a b : ExactRat) : ExactRat :=
  { num := a.num * b.num
    den := a.den * b.den
    den_pos := Nat.mul_pos a.den_pos b.den_pos }

def square (a : ExactRat) : ExactRat :=
  mul a a

def absRat (a : ExactRat) : ExactRat :=
  { num := Int.ofNat a.num.natAbs
    den := a.den
    den_pos := a.den_pos }

/- The nonzero proof is a required input. Its impossible zero branch returns
a harmless total value; that branch cannot be called from a well-typed proof
of `nonzero a`. -/
def reciprocal (a : ExactRat) (_ha : nonzero a) : ExactRat :=
  match a.num with
  | Int.ofNat 0 =>
      { num := 0, den := 1, den_pos := by decide }
  | Int.ofNat (Nat.succ n) =>
      { num := Int.ofNat a.den
        den := Nat.succ n
        den_pos := Nat.zero_lt_succ n }
  | Int.negSucc n =>
      { num := -(Int.ofNat a.den)
        den := Nat.succ n
        den_pos := Nat.zero_lt_succ n }

def div (a b : ExactRat) (hb : nonzero b) : ExactRat :=
  mul a (reciprocal b hb)

abbrev less (a b : ExactRat) : Prop :=
  intLess (a.num * Int.ofNat b.den) (b.num * Int.ofNat a.den) = true

def lessOrEqual (a b : ExactRat) : Bool :=
  intLess (a.num * Int.ofNat b.den) (b.num * Int.ofNat a.den) ||
    intEqual (a.num * Int.ofNat b.den) (b.num * Int.ofNat a.den)

def minRat (a b : ExactRat) : ExactRat :=
  if lessOrEqual a b then a else b

/- These definitions preserve the source syntax. In particular,
`sourceLeftDenominator` contains the material factor `4`. -/
def sourceNumerator (x : ExactRat) : ExactRat :=
  absRat (mul (sub x (ofInt 2)) (add x (ofInt 2)))

def claimedNumerator (x : ExactRat) : ExactRat :=
  mul (absRat (sub x (ofInt 2))) (absRat (add x (ofInt 2)))

def sourceLeftDenominator (x : ExactRat) : ExactRat :=
  mul (ofInt 4) (square x)

def sourceRightDenominator (x : ExactRat) : ExactRat :=
  square x

def sourceLeft (x : ExactRat) (h : nonzero (sourceLeftDenominator x)) :
    ExactRat :=
  div (sourceNumerator x) (sourceLeftDenominator x) h

def claimedRight (x : ExactRat) (h : nonzero (sourceRightDenominator x)) :
    ExactRat :=
  div (claimedNumerator x) (sourceRightDenominator x) h

def witnessX : ExactRat := ofInt 1
def threeFourths : ExactRat := fraction 3 4 (by decide)
def three : ExactRat := ofInt 3

def witnessLeftDefined : nonzero (sourceLeftDenominator witnessX) := by
  decide

def witnessRightDefined : nonzero (sourceRightDenominator witnessX) := by
  decide

def witnessLeft : ExactRat := sourceLeft witnessX witnessLeftDefined
def witnessRight : ExactRat := claimedRight witnessX witnessRightDefined

/- This is the literal published final implication at the verified witness,
including x != 0, both division side conditions, and the valid numerator
identity. -/
abbrev PublishedFinalEqualityAtWitness : Prop :=
  nonzero witnessX ->
  nonzero (sourceLeftDenominator witnessX) ->
  nonzero (sourceRightDenominator witnessX) ->
  equivalent (sourceNumerator witnessX) (claimedNumerator witnessX) ->
  equivalent witnessLeft witnessRight

/-- Load-bearing refutation of the exact source equality at `x = 1`. It
certifies the domain premise, both defined divisions, the material numerator
identity, both exact values, the unequal conclusion, and the negated published
witness implication. -/
theorem reddit_learnmath_t6wb5n_refutation :
    nonzero witnessX /\
    nonzero (sourceLeftDenominator witnessX) /\
    nonzero (sourceRightDenominator witnessX) /\
    equivalent (sourceNumerator witnessX) (claimedNumerator witnessX) /\
    equivalent witnessLeft threeFourths /\
    equivalent witnessRight three /\
    Not (equivalent witnessLeft witnessRight) /\
    Not PublishedFinalEqualityAtWitness := by
  decide

def contextX : ExactRat := fraction 3 2 (by decide)
def epsilon : ExactRat := ofInt 1
def delta : ExactRat := fraction 4 5 (by decide)
def fourFifths : ExactRat := fraction 4 5 (by decide)
def sevenThirtySixths : ExactRat := fraction 7 36 (by decide)
def sevenNinths : ExactRat := fraction 7 9 (by decide)
def contextDistance : ExactRat := absRat (sub contextX (ofInt 2))

def contextLeftDefined : nonzero (sourceLeftDenominator contextX) := by
  decide

def contextRightDefined : nonzero (sourceRightDenominator contextX) := by
  decide

def contextLeft : ExactRat := sourceLeft contextX contextLeftDefined
def contextRight : ExactRat := claimedRight contextX contextRightDefined

/-- Context-strengthened rational real witness satisfying every stated
epsilon-delta neighborhood condition. It shows that the same denominator
error remains visible near `2`. -/
theorem context_strengthened_witness_inside_proof_neighborhood :
    less (ofInt 0) epsilon /\
    less (ofInt 0) delta /\
    equivalent delta (minRat (ofInt 1) (mul fourFifths epsilon)) /\
    less (ofInt 0) contextDistance /\
    less contextDistance delta /\
    nonzero contextX /\
    nonzero (sourceLeftDenominator contextX) /\
    nonzero (sourceRightDenominator contextX) /\
    equivalent (sourceNumerator contextX) (claimedNumerator contextX) /\
    equivalent contextLeft sevenThirtySixths /\
    equivalent contextRight sevenNinths /\
    Not (equivalent contextLeft contextRight) := by
  decide

def controlX : ExactRat := ofInt 2

def controlLeftDefined : nonzero (sourceLeftDenominator controlX) := by
  decide

def controlRightDefined : nonzero (sourceRightDenominator controlX) := by
  decide

def controlLeft : ExactRat := sourceLeft controlX controlLeftDefined
def controlRight : ExactRat := claimedRight controlX controlRightDefined

/-- Meaningful negative control: at `x = 2`, every domain and definedness
premise remains true, while the zero numerator makes both encoded source sides
zero and equal, masking precisely the missing denominator factor. -/
theorem negative_control_zero_numerator_masks_missing_factor :
    nonzero controlX /\
    nonzero (sourceLeftDenominator controlX) /\
    nonzero (sourceRightDenominator controlX) /\
    equivalent (sourceNumerator controlX) (ofInt 0) /\
    equivalent (claimedNumerator controlX) (ofInt 0) /\
    equivalent controlLeft (ofInt 0) /\
    equivalent controlRight (ofInt 0) /\
    equivalent controlLeft controlRight := by
  decide

end RedditLearnmathT6wb5n
