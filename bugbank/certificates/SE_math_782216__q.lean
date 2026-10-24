/- Human-review certificate. Original witness preserved; historical certificate remains in the frozen packet. -/
import Mathlib
namespace SE_math_782216_q
theorem mathlib_source_counterexample :
    (⊥ : SimpleGraph (Fin 2)).IsAcyclic ∧
    (⊥ : SimpleGraph (Fin 2)).edgeFinset.card = 0 ∧
    ¬ Fintype.card (Fin 2) ≤ 1 := by
 exact ⟨SimpleGraph.isAcyclic_bot, by simp, by decide⟩

end SE_math_782216_q
