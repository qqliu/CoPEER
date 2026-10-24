import Mathlib.Data.Fintype.Card
import Mathlib.Data.Finset.Card
import Mathlib.Tactic.NormNum
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.Ring
import Mathlib.Tactic.FieldSimp
import Mathlib.Tactic.FinCases
import Mathlib.Tactic.Tauto
import Mathlib.Tactic.IntervalCases

/- Human-guided audit: No assignment of253 events to365 days can cover all days; at least112 are absent. Uses Function.Surjective/Fintype and Finset cardinality. The full-coverage event is therefore empty under every probability law.
   Original witness action: KEPT. -/
namespace Audit_reddit_learnmath_ugzgrr
theorem certificate :
    (∀ f : Fin 253 → Fin 365, ¬ Function.Surjective f) ∧
    (∀ f : Fin 253 → Fin 365, 112 ≤ ((Finset.univ : Finset (Fin 365)) \ (Finset.univ.image f)).card) := by
  constructor
  · intro f h
    have := Fintype.card_le_of_surjective f h
    norm_num at this
  · intro f
    have hi := Finset.card_image_le (s := (Finset.univ : Finset (Fin 253))) (f := f)
    rw [Finset.card_sdiff_of_subset (Finset.subset_univ _)]
    norm_num at hi ⊢; omega
end Audit_reddit_learnmath_ugzgrr
