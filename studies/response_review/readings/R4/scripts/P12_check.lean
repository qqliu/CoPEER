-- P12: kernel check of exactly the witness supplied by the critic's response:
--   "For x=1, the left side equals 3/4 while the right side equals 3."
-- Left side  = |(1/x^2) - (1/4)|                (the quantity line 13 starts from)
-- Right side = |x-2| * |x+2| / (x^2)            (the expression line 13 ends with)
import Mathlib

namespace P12

theorem lhs_at_one : |(1 : ℚ) / 1 ^ 2 - 1 / 4| = 3 / 4 := by norm_num

theorem rhs_at_one : |(1 : ℚ) - 2| * |(1 : ℚ) + 2| / 1 ^ 2 = 3 := by norm_num

theorem line13_fails_at_one :
    |(1 : ℚ) / 1 ^ 2 - 1 / 4| ≠ |(1 : ℚ) - 2| * |(1 : ℚ) + 2| / 1 ^ 2 := by norm_num

-- for completeness: the correct denominator 4x^2 does give equality at x = 1,
-- i.e. the discrepancy is exactly the dropped factor 4.
theorem with_four : |(1 : ℚ) / 1 ^ 2 - 1 / 4| = |(1 : ℚ) - 2| * |(1 : ℚ) + 2| / (4 * 1 ^ 2) := by
  norm_num

end P12
