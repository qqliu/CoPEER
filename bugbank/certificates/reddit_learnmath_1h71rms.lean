import Mathlib.Data.Nat.Prime.Basic
import Mathlib.Algebra.GroupWithZero.Semiconj
import Mathlib.Tactic.NormNum
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.Ring
import Mathlib.Tactic.FinCases
import Mathlib.Tactic.Tauto

/- Human-review repair, 2026-09-15.
The theorem concerns the quoted local assertion; it does not refute the surrounding theorem.
Historical source and human verdicts are preserved in the review packet. -/
namespace RedditLearnmath1h71rms

theorem audited_counterexample :
    ¬ IsSquare (8 : ℕ) ∧ (8 : ℕ) ∣ 4 ^ 2 ∧ ¬ (8 : ℕ) ∣ 4 := by
  constructor
  · rintro ⟨k, hk⟩
    rcases (show k ≤ 2 ∨ 3 ≤ k by omega) with h | h <;> nlinarith
  · norm_num

end RedditLearnmath1h71rms
