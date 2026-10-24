/- Human-review certificate. Original witness preserved; historical certificate remains in the frozen packet. -/
import Mathlib
namespace QEDCert.SE_cs_13118__a13122
-- The source defines Sigma using the lower limit 1.
theorem real_sum_counterexample :
    (∑ k ∈ Finset.Icc 1 2, (2 : ℝ)^k) = 6 ∧
    ((2 : ℝ)^3 - 1)/(2 - 1) = 7 ∧
    (∑ k ∈ Finset.Icc 1 2, (2 : ℝ)^k) ≠ ((2 : ℝ)^3 - 1)/(2 - 1) := by
 rw [show Finset.Icc 1 2 = ({1,2} : Finset ℕ) from by decide]
 norm_num
end QEDCert.SE_cs_13118__a13122
