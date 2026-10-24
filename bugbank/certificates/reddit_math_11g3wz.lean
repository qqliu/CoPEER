import Mathlib.LinearAlgebra.Matrix.Determinant.Basic
import Mathlib.Tactic.NormNum
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.Ring
import Mathlib.Tactic.FieldSimp
import Mathlib.Tactic.FinCases
import Mathlib.Tactic.Tauto
import Mathlib.Tactic.IntervalCases

/- Human-guided audit: Unchanged integer projection diag(1,0) is idempotent and annihilates A−I, but differs from0 andI. Uses actual Matrix operations; no custom F3 substitute.
   Original witness action: KEPT. -/
namespace Audit_reddit_math_11g3wz
def A : Matrix (Fin 2) (Fin 2) ℤ := !![1,0;0,0]
theorem certificate : A^2 = A ∧ A*(A-1)=0 ∧ A ≠ 0 ∧ A ≠ 1 := by
  decide
end Audit_reddit_math_11g3wz
