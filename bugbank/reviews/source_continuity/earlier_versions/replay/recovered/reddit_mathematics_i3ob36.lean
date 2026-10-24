/-!
Record: `reddit_mathematics_i3ob36`

Public source: https://www.reddit.com/r/mathematics/comments/i3ob36/interesting_proof_by_induction_example/

Exact target scope: the local induction-step assertion that, for every
interestingness predicate `I` on the natural numbers and every natural `n`,
the two premises `I n` and `¬ I (n + 1)` alone imply that `n + 1` is the
smallest non-interesting natural.  The base case is a separate obligation and
is not modeled as a premise of this local implication.

Modeling judgments: natural numbers are Lean's actual `Nat` values
`0, 1, 2, ...`; interestingness is an arbitrary predicate `Nat → Prop`;
addition and strict order are Lean's ordinary natural-number operations; and
`SmallestNonInteresting I m` means both `¬ I m` and that every natural `k < m`
is interesting.  The source implication retains both universal quantifiers
and both load-bearing hypotheses.  No finite proxy is introduced.

Concrete witness: take `I = {3}` and `n = 3`.  Then `I 3`, while `I 4` is
false, but `I 1` is also false and `1 < 4`; hence `4` is not the smallest
non-interesting natural.  The independently verified negative control uses
the same `n = 3` and `I = {0,1,2,3}`, encoded by `I k ↔ k < 4`: its premises
hold and `4` genuinely is the smallest non-interesting natural.  Thus the
control detects a vacuous or uniformly-false encoding and checks the omitted
smaller-number condition on which minimality depends.

Route review: this is a self-contained Lean certificate because the claim and
both models use only genuine natural numbers, ordinary addition and order,
predicates, and first-order quantification.  The implementation deliberately
uses zero imports and kernel `decide` only for exposed closed numeral facts.
-/

namespace RedditMathematicsI3ob36

def SmallestNonInteresting (I : Nat → Prop) (m : Nat) : Prop :=
  ¬ I m ∧ ∀ k : Nat, k < m → I k

def SourceClaim : Prop :=
  ∀ (I : Nat → Prop) (n : Nat),
    I n → ¬ I (n + 1) → SmallestNonInteresting I (n + 1)

def witnessI (k : Nat) : Prop :=
  k = 3

def controlI (k : Nat) : Prop :=
  k < 4

theorem witness_three_is_interesting : witnessI 3 := by
  rfl

theorem witness_four_is_not_interesting : ¬ witnessI (3 + 1) := by
  change ¬ ((4 : Nat) = 3)
  decide

theorem witness_one_is_not_interesting : ¬ witnessI 1 := by
  change ¬ ((1 : Nat) = 3)
  decide

theorem witness_one_is_smaller : 1 < 3 + 1 := by
  decide

theorem witness_four_is_not_smallest :
    ¬ SmallestNonInteresting witnessI (3 + 1) := by
  intro hSmallest
  exact witness_one_is_not_interesting
    (hSmallest.2 1 witness_one_is_smaller)

/-- Load-bearing refutation of the literal, fully quantified source claim. -/
theorem refutes_source_claim : ¬ SourceClaim := by
  intro hClaim
  exact witness_four_is_not_smallest
    (hClaim witnessI 3 witness_three_is_interesting
      witness_four_is_not_interesting)

theorem control_three_is_interesting : controlI 3 := by
  change (3 : Nat) < 4
  decide

theorem control_four_is_not_interesting : ¬ controlI (3 + 1) := by
  change ¬ ((4 : Nat) < 4)
  decide

/-- Meaningful negative control: under `I k ↔ k < 4`, the same local premises
hold and the asserted minimality conclusion is true. -/
theorem negative_control_four_is_genuinely_smallest :
    controlI 3 ∧
    ¬ controlI (3 + 1) ∧
    SmallestNonInteresting controlI (3 + 1) := by
  constructor
  · exact control_three_is_interesting
  constructor
  · exact control_four_is_not_interesting
  constructor
  · exact control_four_is_not_interesting
  · intro k hk
    exact hk

end RedditMathematicsI3ob36
