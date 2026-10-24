import Mathlib.NumberTheory.Real.Irrational
import Mathlib.Tactic.NormNum
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.Ring
import Mathlib.Tactic.FieldSimp
import Mathlib.Tactic.FinCases
import Mathlib.Tactic.Tauto
import Mathlib.Tactic.IntervalCases

/- Human-guided audit: Unchanged irrational numerator√2 and distinct irrational divisors√2,√2/2 yield rational1 and2. Uses actual Irrational and Real.sqrt rather than formal coordinate irrationality.
   Original witness action: KEPT. -/
namespace Audit_reddit_mathematics_1dz93wr
theorem certificate : Irrational (Real.sqrt 2) ∧ Irrational (Real.sqrt 2 / 2) ∧
    Real.sqrt 2 ≠ Real.sqrt 2/2 ∧ Real.sqrt 2/Real.sqrt 2 = 1 ∧
    Real.sqrt 2/(Real.sqrt 2/2) = 2 ∧ (1 : ℝ) ≠ 2 := by
  have hi : Irrational (Real.sqrt 2) := irrational_sqrt_two
  have hn : Real.sqrt 2 ≠ 0 := ne_of_gt (Real.sqrt_pos.2 (by norm_num))
  refine ⟨hi, ?_, ?_, div_self hn, ?_, by norm_num⟩
  · simpa using hi.div_ratCast (by norm_num : (2 : ℚ) ≠ 0)
  · intro h
    apply hn
    linarith
  · field_simp
end Audit_reddit_mathematics_1dz93wr
