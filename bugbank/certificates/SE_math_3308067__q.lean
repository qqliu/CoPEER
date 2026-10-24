/- Human-review certificate. Original witness preserved; historical certificate remains in the frozen packet. -/
import Mathlib
namespace QEDCert.SE_math_3308067__q
theorem mathlib_source_counterexample :
    Fintype.card (Fin 2) = 2 ∧ (⊥ : SimpleGraph (Fin 2)).edgeFinset.card = 0 ∧
    (∀ v : Fin 2, (⊥ : SimpleGraph (Fin 2)).degree v = 0) ∧
    ¬ (⊥ : SimpleGraph (Fin 2)).edgeFinset.card = Nat.choose 2 2 := by
 simp

end QEDCert.SE_math_3308067__q
