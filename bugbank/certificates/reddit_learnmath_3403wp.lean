import Mathlib.Data.Fintype.Fin
import Mathlib.Data.Finset.Powerset
import Mathlib.Data.Finset.Prod
import Mathlib.Tactic.NormNum
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.Ring
import Mathlib.Tactic.FieldSimp
import Mathlib.Tactic.FinCases
import Mathlib.Tactic.Tauto
import Mathlib.Tactic.IntervalCases

/- Human-guided audit: A cabinet is a pair of chosen subsets. Mathlib powersetCard/product cardinalities give 6435×120=772200 rather than their sum6555; the stored source supplies all pool sizes.
   Original witness action: KEPT. -/
namespace Audit_reddit_learnmath_3403wp
def cabinets := ((Finset.univ : Finset (Fin 15)).powersetCard 8).product
  ((Finset.univ : Finset (Fin 10)).powersetCard 7)
theorem certificate : cabinets.card = 772200 ∧ cabinets.card ≠ 6555 := by
  norm_num [cabinets, Finset.card_product, Finset.card_powersetCard, Nat.choose]
end Audit_reddit_learnmath_3403wp
