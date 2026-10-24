/- Record g3ref-pnv-102 (E17): Mathlib file (`import Mathlib`, as the released file).

Source: a reference-derived proof text for the problem "Show that any prime divisor of x^4 - x^2 + 1 is
congruent to 1 modulo 12" (stored problem text P0001-P0004, proof text lines 0001-0008). Line 0004 asserts,
for an integer a and a prime p dividing a^4 - a^2 + 1, that p | 4a^4 - 4a^2 + 4 = (2a - 1)^2 + 3.
`lhs a` and `rhs a` are the two sides of that identity. `SourceIdentity` reads the identity for every
integer a; `SourceIdentityInContext` reads it in the source's context (a prime p dividing a^4 - a^2 + 1).
`SourceGoal` is the source's stated goal (P0001), recorded for reference only.
Primality and divisibility are Mathlib's standard predicates. -/
import Mathlib

namespace G3refPnv102
def lhs (a : ℤ) : ℤ := 4 * a ^ 4 - 4 * a ^ 2 + 4
def rhs (a : ℤ) : ℤ := (2 * a - 1) ^ 2 + 3

/-- The located identity (stored line 0004) read for every integer `a`. -/
def SourceIdentity : Prop := ∀ a : ℤ, lhs a = rhs a

/-- The located identity in the source's context: `a` an integer, `p` a prime dividing `a^4 - a^2 + 1`. -/
def SourceIdentityInContext : Prop :=
  ∀ (a : ℤ) (p : ℕ), Nat.Prime p → (p : ℤ) ∣ a ^ 4 - a ^ 2 + 1 → lhs a = rhs a

/-- The source's stated goal (problem text P0001): every prime divisor of `x^4 - x^2 + 1` is `1 mod 12`.
Recorded for reference only. -/
def SourceGoal : Prop := ∀ (x : ℤ) (p : ℕ), Nat.Prime p → (p : ℤ) ∣ x ^ 4 - x ^ 2 + 1 → p % 12 = 1
end G3refPnv102
