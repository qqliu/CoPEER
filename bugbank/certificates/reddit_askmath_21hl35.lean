import Mathlib.Algebra.Ring.Parity
import Mathlib.Tactic.NormNum
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.Ring
import Mathlib.Tactic.FinCases
import Mathlib.Tactic.Tauto

/- Human-review repair, 2026-09-15.
The theorem concerns the quoted local assertion; it does not refute the surrounding theorem.
Historical source and human verdicts are preserved in the review packet. -/
namespace RedditAskmath21hl35

theorem audited_counterexample :
    Even (0 : ℤ) ∧ (0 : ℤ) < 1 ∧
    ¬ ∃ n : ℤ, 0 < n ∧ (0 : ℤ) = 2*n := by
  constructor
  · exact ⟨0, by norm_num⟩
  · constructor
    · norm_num
    · rintro ⟨n, hn, h⟩
      omega

end RedditAskmath21hl35
