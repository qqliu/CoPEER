import Mathlib.RingTheory.Polynomial.Content
import Mathlib.RingTheory.Localization.Integral
import Mathlib.Tactic
/-!
Record proofwiki_25056 (E11): ProofWiki, "Content of Scalar Multiple".

Quoted local claim, for `q = a / b`, `a b n : ℤ`, `n f ∈ ℤ[X]`:  `cont (b n q f) = a cont (n f)`.
Since `b n q f = a (n f)` as integer polynomials (for every `b ≠ 0`), the quoted line is the
scalar pull-out `cont (a p) = a cont p` with `p = n f`, stated below as `LocalClaim`.
Integer content is Mathlib's `Polynomial.content` (the normalised gcd of the coefficients).
-/
namespace ProofWiki25056Census
open Polynomial

/-- The quoted line, for every integer scalar and every integer polynomial. -/
def LocalClaim : Prop := ∀ (a : ℤ) (p : ℤ[X]), (C a * p).content = a * p.content

end ProofWiki25056Census
