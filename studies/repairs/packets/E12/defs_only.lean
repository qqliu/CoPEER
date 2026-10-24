/-
Record reddit_askmath_1bq1jtc (E12).  Core Lean only: no imports.

Source line (verbatim): "6q + 2 = 2(3q +2) so is even."
Context: the source writes a natural prime p as p = 6q + r and classifies the residues r
that a prime other than 2 and 3 can have; the quoted line is the case r = 2.
The located statement is `Claim` (at the arbitrary integer quotient q); read universally
as the source uses it, it is `UniversalClaim`.
The theorem the source is proving is `SourceGoal` (statement only).
-/
namespace RedditAskmath1bq1jtcCensus

/-- The quoted equality at `q`, exactly as the source writes it. -/
def Claim (q : Int) : Prop := 6*q+2 = 2*(3*q+2)

/-- The located line as the source uses it: for the arbitrary quotient `q`. -/
def UniversalClaim : Prop := ∀ q : Int, Claim q

/-- Primality on `Nat`, stated from scratch (no Mathlib). -/
def IsPrime (p : Nat) : Prop := 2 ≤ p ∧ ∀ d : Nat, d ∣ p → d = 1 ∨ d = p

/-- The source's theorem (statement only): every prime other than 2 and 3 is `6q + 1` or `6q + 5`. -/
def SourceGoal : Prop :=
  ∀ p : Nat, IsPrime p → p ≠ 2 → p ≠ 3 → (∃ q : Nat, p = 6*q+1) ∨ (∃ q : Nat, p = 6*q+5)

end RedditAskmath1bq1jtcCensus
