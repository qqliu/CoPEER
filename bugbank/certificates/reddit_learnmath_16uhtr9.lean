import Mathlib.Tactic.NormNum.Parity
import Mathlib.Algebra.Group.Nat.Even
import Mathlib.Tactic.NormNum
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.Ring
import Mathlib.Tactic.FieldSimp
import Mathlib.Tactic.FinCases
import Mathlib.Tactic.Tauto
import Mathlib.Tactic.IntervalCases

/- Human-guided audit: The proposed inference checks one even and one odd input, without an induction step or parity invariance. P={2,3} passes both checks and fails at 4. Mathlib Even/Odd replace recursive parity.
   Original witness action: KEPT. -/
namespace Audit_reddit_learnmath_16uhtr9
def P (k : ℕ) : Prop := k = 2 ∨ k = 3
theorem certificate : Even (2 : ℕ) ∧ Odd (3 : ℕ) ∧ P 2 ∧ P 3 ∧ ¬ P 4 := by
  norm_num [P]
end Audit_reddit_learnmath_16uhtr9
