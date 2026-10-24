import Mathlib.Data.Set.Basic
import Mathlib.Tactic.NormNum
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.Ring
import Mathlib.Tactic.FieldSimp
import Mathlib.Tactic.FinCases
import Mathlib.Tactic.Tauto
import Mathlib.Tactic.IntervalCases

/- Human-guided audit: Power set of the unchanged singleton carrier has the surjective identity. Uses actual Set and Function.Surjective instead of a Boolean model.
   Original witness action: KEPT. -/
namespace Audit_reddit_learnmath_37baow
theorem certificate : Function.Surjective (id : Set (Fin 1) → Set (Fin 1)) := Function.surjective_id
end Audit_reddit_learnmath_37baow
