import Mathlib.Tactic.NormNum.RealSqrt
import Mathlib.NumberTheory.Real.Irrational
import Mathlib.Tactic.NormNum
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.Ring
import Mathlib.Tactic.FieldSimp
import Mathlib.Tactic.FinCases
import Mathlib.Tactic.Tauto
import Mathlib.Tactic.IntervalCases

/- Human-guided audit: The unchanged reduced fraction4/1 is the actual principal root√16, hence rational;16 divides its square but not its numerator. Uses Nat.Coprime and Real.sqrt.
   Original witness action: KEPT. -/
namespace Audit_reddit_mathematics_1j7062e
theorem certificate : Nat.Coprime 4 1 ∧ (1 : ℕ) ≠ 0 ∧ Real.sqrt 16 = (4/1 : ℝ) ∧
    ¬ Irrational (Real.sqrt 16) ∧ ¬ (16 : ℕ) ∣ 4 := by
  norm_num [Irrational]
  exact ⟨(4 : ℚ), by norm_num⟩
end Audit_reddit_mathematics_1j7062e
