-- P42: kernel check of exactly the witness supplied by the critic's response:
--   x = -pi/2 has tan(x/2) = -1 (nonzero), yet x lies in no interval (2*pi*n, 2*pi*n + pi).
-- Lines 4-5 of the source assert: for all n in Z, 2*pi*n < x < 2*pi*n + pi.
import Mathlib

open Real

namespace P42

-- (a) the witness satisfies the source's standing hypothesis (line 2 / P3): tan (x/2) != 0
theorem tan_half_ne_zero : Real.tan ((-(π / 2)) / 2) ≠ 0 := by
  have h : (-(π / 2)) / 2 = -(π / 4) := by ring
  rw [h, Real.tan_neg, Real.tan_pi_div_four]
  norm_num

-- (b) yet no integer n puts the witness in the asserted interval
theorem not_in_interval (n : ℤ) :
    ¬ (2 * π * (n : ℝ) < -(π / 2) ∧ -(π / 2) < 2 * π * (n : ℝ) + π) := by
  rintro ⟨h1, h2⟩
  have hp : (0 : ℝ) < π := Real.pi_pos
  have hlt : ((n : ℝ)) < 0 := by nlinarith [hp, h1]
  have hgt : (-1 : ℝ) < ((n : ℝ)) := by nlinarith [hp, h2]
  have hn1 : n < 0 := by exact_mod_cast hlt
  have hn2 : (-1 : ℤ) < n := by exact_mod_cast hgt
  omega

end P42
