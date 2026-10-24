import Mathlib.Data.Nat.Basic
import Mathlib.Tactic.NormNum
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.Ring
import Mathlib.Tactic.FinCases
import Mathlib.Tactic.Tauto

/- Human-review repair, 2026-09-15.
The theorem concerns the quoted local assertion; it does not refute the surrounding theorem.
Historical source and human verdicts are preserved in the review packet. -/
namespace RedditLearnmathQ0j6vm

def f (n : ℕ) := 2*n
def g (n : ℕ) := if n = 1 then 2 else n

theorem audited_counterexample :
    Function.Injective (g ∘ f) ∧ ¬ Function.Injective g := by
  constructor
  · intro a b h
    have ha : 2*a ≠ 1 := by omega
    have hb : 2*b ≠ 1 := by omega
    simp [Function.comp_def, f, g, ha, hb] at h
    omega
  · intro h
    have bad := h (show g 1 = g 2 by norm_num [g])
    omega

end RedditLearnmathQ0j6vm
