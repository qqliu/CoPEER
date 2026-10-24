import Mathlib.Data.Rat.Defs
import Mathlib.Tactic.NormNum
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.Ring
import Mathlib.Tactic.FieldSimp
import Mathlib.Tactic.FinCases
import Mathlib.Tactic.Tauto
import Mathlib.Tactic.IntervalCases

/- Human-guided audit: r=1/4,s=1/2 are ordered rationals, yet no integer n represents both as successive reciprocals. This certifies failure of claimed coverage, not falsity of density of irrationals.
   Original witness action: KEPT. -/
namespace Audit_reddit_learnmath_h8oug8
theorem certificate : (1/4 : ℚ) < 1/2 ∧
    ¬ ∃ n : ℤ, (1/2 : ℚ) = 1/(n : ℚ) ∧ (1/4 : ℚ) = 1/((n : ℚ)+1) := by
  refine ⟨by norm_num, ?_⟩
  rintro ⟨n,h,h'⟩
  have hn : (n : ℚ) ≠ 0 := by intro z; simp [z] at h
  have n2 : (n : ℚ) = 2 := by field_simp at h; linarith
  norm_num [n2] at h'
end Audit_reddit_learnmath_h8oug8
