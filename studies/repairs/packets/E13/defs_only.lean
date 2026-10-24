/-!
Record reddit_learnmath_8yjpp7 (E13).  Core Lean, no imports.

Source claim (the odd branch of an induction about the pseudocode `Increment`):
  "If floor(n / 2) is even then we have the aforementioned case 1) in the recursive
   call and thus we have (floor(n / 2)+ 1) * 2 = n + 2."
Oddness of n comes from the enclosing "2) n is odd" branch; the floor-even hypothesis from
the quoted sentence.  `Odd` and `Even` are Mathlib's, unfolded on Nat as `IsOdd`, `IsEven`.
The located statement is `SourceClaim`; `SourceClaimQuoteOnly` is the quoted sentence read
alone (only the floor-even hypothesis).
The source's pseudocode is `Increment`; the statement its induction is after is `SourceGoal`.
-/

namespace Census_reddit_learnmath_8yjpp7

/-- Mathlib's `Odd` on Nat, unfolded. -/
def IsOdd (n : Nat) : Prop := ∃ m, n = 2 * m + 1
/-- Mathlib's `Even` on Nat, unfolded. -/
def IsEven (n : Nat) : Prop := ∃ r, n = r + r

/-- The source's local claim, both hypotheses retained (oddness comes from the
enclosing "2) n is odd" branch, the floor-even hypothesis from the quoted sentence). -/
def SourceClaim : Prop :=
  ∀ n : Nat, IsOdd n → IsEven (n / 2) → (n / 2 + 1) * 2 = n + 2

/-- The quoted sentence read alone: only the floor-even hypothesis. -/
def SourceClaimQuoteOnly : Prop :=
  ∀ n : Nat, IsEven (n / 2) → (n / 2 + 1) * 2 = n + 2

/-- The source's pseudocode:
    Increment(y): if y = 0 then return(1) else
                    if (y mod 2) = 1 then return(2 · Increment(y/2)) else return(y + 1) -/
def Increment (y : Nat) : Nat :=
  if h0 : y = 0 then 1
  else if y % 2 = 1 then 2 * Increment (y / 2)
  else y + 1
termination_by y
decreasing_by omega

/-- The statement the source's induction is after (statement only). -/
def SourceGoal : Prop := ∀ n : Nat, Increment n = n + 1

end Census_reddit_learnmath_8yjpp7
