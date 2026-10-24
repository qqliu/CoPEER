import Mathlib.Data.Nat.Digits.Lemmas
import Mathlib.Data.Nat.Digits.Lemmas
import Mathlib.Data.Rat.Defs
import Mathlib.Tactic.NormNum
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.Ring
import Mathlib.Tactic.FinCases
import Mathlib.Tactic.Tauto

/- Human-review repair, 2026-09-15.
The theorem concerns the quoted local assertion; it does not refute the surrounding theorem.
Historical source and human verdicts are preserved in the review packet. -/
namespace RedditLearnmath40nenp

theorem audited_counterexample :
    Nat.Coprime 1 2 ∧ (0 : ℚ) ≤ 1/2 ∧ (1/2 : ℚ) ≤ 1 ∧
    (Nat.digits 10 1).length = (Nat.digits 10 2).length := by
  refine ⟨by decide, by norm_num, by norm_num, ?_⟩
  decide

end RedditLearnmath40nenp
