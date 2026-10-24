/-!
Record: `arxiv_1304.1796v2__source_enriched_codex`

Public source: https://arxiv.org/abs/1304.1796

Exact target scope: the displayed algebraic proof step used in Part 1 of the
Non-Intersection Bias Lemma, namely
`p0 * (1 + 2/(k-1))^(a-1) <=
p0 * (1 + 2*(a-1)/(k-1))` for sufficiently large `k`.
This certificate refutes that step, not the lemma's final probabilistic bound.

Concrete Terra-verified witness: `a = t = 3`, `k = 1001`, `d = k-1 = 1000`.
After cancelling the common positive `p0`, the two normalized sides are
`251001/250000` and `251000/250000`. Equivalently,
`1002^2 = 1004004 > 1004000 = 1000*(1000+4)`.

Material modelling judgments: all parameters are natural numbers. For every
threshold `N`, the witness uses `k = N+4`, so `k>N`, `a=t=3`, `1<=a`,
`t<=a`, and `a<k`. Writing `d=k-1`, the source probability is represented
exactly by numerator `pNum=d^k` and denominator `pDen=k^k`, since
`p0=((k-1)/k)^k`. Both are positive. Multiplication by the positive common
denominator `pDen*d^2` converts the source step exactly to
`pNum*(d+2)^2 <= pNum*d*(d+4)`. The left side instead exceeds the right by
`4*pNum`. Terra's `p0=1` is therefore the cancelled normalization, not a
replacement probability model.

The lemma setup can realize `a=3` by taking `x` constantly one and `f(x)`
one on exactly three coordinates and two elsewhere. Neither that realization
nor the conditional law of `Y` is load-bearing for this pointwise algebraic
inference, so no finite probability surrogate is introduced. The negative
control changes the witness feature to `a=2`; after clearing its positive
common denominator, both sides are exactly `pNum*(d+2)` for every `d>0`.
-/

namespace Arxiv13041796v2SourceEnrichedCodex

def witnessA : Nat := 3
def witnessT : Nat := 3
def witnessD (N : Nat) : Nat := N + 3
def witnessK (N : Nat) : Nat := witnessD N + 1

def pNumerator (k d : Nat) : Nat := d ^ k
def pDenominator (k : Nat) : Nat := k ^ k

/- This is the strictly positive denominator used to clear both `p0` and the
square of `d` in the source expression at `a=3`. -/
def commonDenominatorAThree (k d : Nat) : Nat :=
  pDenominator k * d ^ 2

def clearedAThreeLeft (k d : Nat) : Nat :=
  pNumerator k d * (d + 2) ^ 2

def clearedAThreeRight (k d : Nat) : Nat :=
  pNumerator k d * (d * (d + 4))

def claimedDisplayedStepAtAThree (k d : Nat) : Prop :=
  clearedAThreeLeft k d <= clearedAThreeRight k d

def sourceHypotheses
    (N k a t d : Nat) : Prop :=
  N < k /\
  k = N + 4 /\
  a = 3 /\
  t = 3 /\
  1 <= a /\
  t <= a /\
  a < k /\
  d = k - 1 /\
  0 < d

/- The elementary identity is the cleared, unscaled source comparison. -/
theorem square_gap (d : Nat) :
    (d + 2) ^ 2 = d * (d + 4) + 4 := by
  simp [Nat.pow_succ, Nat.mul_add, Nat.add_mul, Nat.add_assoc,
    Nat.add_comm, Nat.add_left_comm]
  rw [Nat.mul_comm 2 d]
  rw [show d * 4 = d * 2 + d * 2 by
    exact Nat.mul_add d 2 2]
  simp [Nat.add_assoc, Nat.add_comm, Nat.add_left_comm]

theorem cleared_gap (k d : Nat) :
    clearedAThreeLeft k d =
      clearedAThreeRight k d + pNumerator k d * 4 := by
  unfold clearedAThreeLeft clearedAThreeRight
  rw [square_gap]
  rw [Nat.mul_add]

theorem strict_reverse_when_d_positive
    (k d : Nat) (hd : 0 < d) :
    clearedAThreeRight k d < clearedAThreeLeft k d := by
  have hp : 0 < pNumerator k d := by
    exact Nat.pow_pos hd
  rw [cleared_gap]
  exact Nat.lt_add_of_pos_right (Nat.mul_pos hp (by decide))

def terraConcreteWitness : Prop :=
  witnessK 997 = 1001 /\
  witnessD 997 = 1000 /\
  1002 ^ 2 = 1004004 /\
  1000 * (1000 + 4) = 1004000 /\
  1004000 < 1004004 /\
  Not (1002 ^ 2 <= 1000 * (1000 + 4)) /\
  1000 ^ 2 = 1000000 /\
  1004004 = 4 * 251001 /\
  1000000 = 4 * 250000 /\
  1004000 = 4 * 251000 /\
  251000 < 251001

/-- Load-bearing refutation: every threshold has a source-admissible
`a=t=3`, `k=N+4` witness. The actual source numerator and denominator and the
clearing denominator are positive, while the exact cleared source inequality
is strictly reversed. The final conjunct records the concrete Terra witness. -/
theorem refutes_sufficiently_large_displayed_inequality :
    (forall N : Nat, exists k a t d : Nat,
      sourceHypotheses N k a t d /\
      0 < pNumerator k d /\
      0 < pDenominator k /\
      0 < commonDenominatorAThree k d /\
      clearedAThreeRight k d < clearedAThreeLeft k d /\
      Not (claimedDisplayedStepAtAThree k d)) /\
    terraConcreteWitness := by
  constructor
  · intro N
    let d := witnessD N
    let k := witnessK N
    have hd : 0 < d := by
      simp [d, witnessD]
    have hk : 0 < k := by
      simp [k, witnessK, witnessD]
    have hpNum : 0 < pNumerator k d := by
      exact Nat.pow_pos hd
    have hpDen : 0 < pDenominator k := by
      exact Nat.pow_pos hk
    have hcommon : 0 < commonDenominatorAThree k d := by
      unfold commonDenominatorAThree
      exact Nat.mul_pos hpDen (Nat.pow_pos hd)
    have hreverse :
        clearedAThreeRight k d < clearedAThreeLeft k d :=
      strict_reverse_when_d_positive k d hd
    refine ⟨k, witnessA, witnessT, d, ?_⟩
    constructor
    · simp [sourceHypotheses, k, d, witnessK, witnessD,
        witnessA, witnessT, Nat.add_assoc]
    constructor
    · exact hpNum
    constructor
    · exact hpDen
    constructor
    · exact hcommon
    constructor
    · exact hreverse
    · unfold claimedDisplayedStepAtAThree
      exact Nat.not_le_of_lt hreverse
  · unfold terraConcreteWitness
    constructor
    · decide
    constructor
    · decide
    constructor
    · decide
    constructor
    · decide
    constructor
    · decide
    constructor
    · decide
    constructor
    · decide
    constructor
    · decide
    constructor
    · decide
    constructor
    · decide
    · decide

def negativeControlA : Nat := 2

def commonDenominatorATwo (k d : Nat) : Nat :=
  pDenominator k * d

def clearedATwoLeft (k d : Nat) : Nat :=
  pNumerator k d * (d + 2)

def clearedATwoRight (k d : Nat) : Nat :=
  pNumerator k d * (d + 2)

/-- Meaningful changed-feature negative control: setting `a=2` changes the
exponent from two to one. For every positive `d`, with `k=d+1`, the source
`p0` numerator, denominator, and clearing denominator remain positive, and
the two exactly cleared sides coincide. -/
theorem negative_control_a_two_equality
    (d : Nat) (hd : 0 < d) :
    negativeControlA = 2 /\
    0 < pNumerator (d + 1) d /\
    0 < pDenominator (d + 1) /\
    0 < commonDenominatorATwo (d + 1) d /\
    clearedATwoLeft (d + 1) d = clearedATwoRight (d + 1) d := by
  have hk : 0 < d + 1 := by
    exact Nat.zero_lt_succ d
  have hpNum : 0 < pNumerator (d + 1) d := by
    exact Nat.pow_pos hd
  have hpDen : 0 < pDenominator (d + 1) := by
    exact Nat.pow_pos hk
  constructor
  · rfl
  constructor
  · exact hpNum
  constructor
  · exact hpDen
  constructor
  · unfold commonDenominatorATwo
    exact Nat.mul_pos hpDen hd
  · rfl

end Arxiv13041796v2SourceEnrichedCodex

#print axioms Arxiv13041796v2SourceEnrichedCodex.square_gap
#print axioms Arxiv13041796v2SourceEnrichedCodex.cleared_gap
#print axioms Arxiv13041796v2SourceEnrichedCodex.strict_reverse_when_d_positive
#print axioms Arxiv13041796v2SourceEnrichedCodex.refutes_sufficiently_large_displayed_inequality
#print axioms Arxiv13041796v2SourceEnrichedCodex.negative_control_a_two_equality
