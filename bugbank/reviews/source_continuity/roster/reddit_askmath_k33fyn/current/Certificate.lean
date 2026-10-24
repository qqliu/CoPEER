import Mathlib.Data.Nat.Prime.Basic
import Mathlib.Algebra.Ring.Parity
import Mathlib.Tactic.NormNum
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.Ring
import Mathlib.Tactic.FinCases
import Mathlib.Tactic.Tauto

/- Human-review repair, 2026-09-15.
Negative odd witness -3 avoids the empty-product convention at 1. A product of positive natural primes, including the empty product, cannot equal -3; the missing sign/unit must be handled. The true odd-power conclusion is unaffected.
Historical source and human verdicts are preserved in the review packet. -/
namespace RedditAskmathK33fyn

theorem audited_counterexample :
    Odd (-3 : ℤ) ∧
    ¬ ∃ ps : List ℕ, (∀ p ∈ ps, Nat.Prime p) ∧ (-3 : ℤ) = (ps.prod : ℤ) := by
  constructor
  · exact ⟨-2, by norm_num⟩
  · rintro ⟨ps, _, h⟩
    have := Int.natCast_nonneg ps.prod
    omega

end RedditAskmathK33fyn
