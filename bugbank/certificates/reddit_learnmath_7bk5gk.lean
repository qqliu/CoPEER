import Mathlib.LinearAlgebra.Prod
import Mathlib.Data.Rat.Defs
import Mathlib.Tactic.NormNum
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.Ring
import Mathlib.Tactic.FinCases
import Mathlib.Tactic.Tauto

/- Human-review repair, 2026-09-15.
Actual rational vector spaces and Mathlib linear maps certify that an injective composition need not have an injective outer map.
Historical source and human verdicts are preserved in the review packet. -/
namespace RedditLearnmath7bk5gk

def F : (ℚ × ℚ) →ₗ[ℚ] ℚ := LinearMap.fst ℚ ℚ ℚ
def G : ℚ →ₗ[ℚ] (ℚ × ℚ) := LinearMap.inl ℚ ℚ ℚ

theorem audited_counterexample :
    Function.Injective (F.comp G) ∧ ¬ Function.Injective F := by
  constructor
  · intro a b h
    exact h
  · intro h
    have bad := h (show F (0,0) = F (0,1) by rfl)
    have := congrArg Prod.snd bad
    norm_num at this

end RedditLearnmath7bk5gk
