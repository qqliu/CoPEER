import Mathlib.Tactic.NormNum.Prime
import Mathlib.Data.Nat.Prime.Defs
import Mathlib.Tactic.NormNum
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.Ring
import Mathlib.Tactic.FieldSimp
import Mathlib.Tactic.FinCases
import Mathlib.Tactic.Tauto
import Mathlib.Tactic.IntervalCases

/- Human-guided audit: 17 is prime by Mathlib Nat.Prime. Source openly labels the passage as an Even Prime Month joke; retain that provenance rather than presenting it as an earnest proof.
   Original witness action: KEPT. -/
namespace Audit_reddit_math_4674e5
theorem certificate : Nat.Prime 17 := by norm_num
end Audit_reddit_math_4674e5
