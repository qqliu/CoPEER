import Mathlib.Data.Real.Sqrt
import Mathlib.Tactic.NormNum
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.Ring
import Mathlib.Tactic.FieldSimp
import Mathlib.Tactic.FinCases
import Mathlib.Tactic.Tauto
import Mathlib.Tactic.IntervalCases

/- Human-guided audit: The unchanged ε=1/10,δ=3/10,x=(√2−1/10)² satisfies the full delta bound but produces error exactly ε. Replaces abstract field/sqrt laws by actual Real.sqrt.
   Original witness action: KEPT. -/
namespace Audit_reddit_learnmath_1bbke99
noncomputable def x : ℝ := (Real.sqrt 2 - 1/10)^2
theorem certificate : (0 : ℝ) < 1/10 ∧ (0 : ℝ) < 3/10 ∧
    (3/10 : ℝ) < min 1 ((Real.sqrt 3 + Real.sqrt 2) * (1/10)) ∧
    0 ≤ x ∧ |x - 2| < 3/10 ∧ |Real.sqrt x - Real.sqrt 2| = 1/10 := by
  have h2 := Real.sq_sqrt (show (0 : ℝ) ≤ 2 by norm_num)
  have h3 := Real.sq_sqrt (show (0 : ℝ) ≤ 3 by norm_num)
  have p2 := Real.sqrt_nonneg (2 : ℝ)
  have p3 := Real.sqrt_nonneg (3 : ℝ)
  have a : (7/5 : ℝ) < Real.sqrt 2 := by nlinarith
  have b : Real.sqrt 2 < (3/2 : ℝ) := by nlinarith
  have c : (8/5 : ℝ) < Real.sqrt 3 := by nlinarith
  refine ⟨by norm_num, by norm_num, lt_min (by norm_num) (by nlinarith), sq_nonneg _, ?_, ?_⟩
  · rw [abs_lt]; dsimp [x]; constructor <;> nlinarith
  · rw [x, Real.sqrt_sq (by linarith : (0 : ℝ) ≤ Real.sqrt 2 - 1/10)]
    norm_num
end Audit_reddit_learnmath_1bbke99
