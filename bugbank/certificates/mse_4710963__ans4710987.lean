import Mathlib.Data.Rat.Defs
import Mathlib.Tactic.NormNum

/-! Keep k=5,n=1012. Use ordinary rational division, not truncated natural
division. This is a local numerator/sign typo; the corrected comparison
32<2024 supports the source's conclusion k≤4. -/
namespace MSE_4710963_ans4710987

def derivedRhs (k : ℚ) : ℚ := 8*(k-1)/(k-4)
def printedRhs (k : ℚ) : ℚ := 8*k/(k-4)

theorem mse_4710963__ans4710987_refutation :
    derivedRhs 5 = 32 ∧ printedRhs 5 = 40 ∧
    derivedRhs 5 ≠ printedRhs 5 ∧
    ¬ (2*1012 < derivedRhs 5) ∧ ¬ (2*1012 < printedRhs 5) := by
  norm_num [derivedRhs,printedRhs]
end MSE_4710963_ans4710987
