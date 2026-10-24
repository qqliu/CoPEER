/- Human-review certificate. Original witness preserved; historical certificate remains in the frozen packet. -/
import Mathlib
namespace SE_math_4066749_q
def sourceBipartite : SimpleGraph (Fin 3) where
 Adj i j := (i = 0 ∧ j ≠ 0) ∨ (i ≠ 0 ∧ j = 0)
 symm := by intro i j h; tauto
 loopless := ⟨fun _ h => by tauto⟩
instance : DecidableRel sourceBipartite.Adj := fun _ _ => inferInstanceAs (Decidable (_ ∨ _))
theorem mathlib_source_counterexample :
    ¬(⊥ : SimpleGraph (Fin 3)).Connected ∧
    ((⊥ : SimpleGraph (Fin 3))ᶜ).Adj 1 2 ∧
    ¬sourceBipartite.Adj 1 2 ∧ (⊥ : SimpleGraph (Fin 3))ᶜ ≠ sourceBipartite := by
 refine ⟨SimpleGraph.not_connected_bot, by decide, by decide, ?_⟩
 intro heq
 have : sourceBipartite.Adj 1 2 := heq ▸ (by decide : ((⊥ : SimpleGraph (Fin 3))ᶜ).Adj 1 2)
 exact (by decide : ¬sourceBipartite.Adj 1 2) this

end SE_math_4066749_q
