import Mathlib.Tactic.NormNum.GCD
import Mathlib.Data.Int.GCD
import Mathlib.Tactic.NormNum
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.Ring
import Mathlib.Tactic.FinCases
import Mathlib.Tactic.Tauto

/- Audit 2026-09-15. Historical source packets and human judgments remain unchanged. -/
namespace RedditLearnmathA2vtxz

theorem audited_counterexample :
    (2 : ℤ) ∣ 3*2 ∧ Int.gcd 2 3 = 1 ∧ (3 : ℤ) ≠ 1 ∧ (3 : ℤ) ≠ -1 := by
  norm_num

end RedditLearnmathA2vtxz
