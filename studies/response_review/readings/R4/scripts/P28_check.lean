-- P28: kernel check of exactly the witness supplied by the critic's response:
--   u = 2, m = 3, n = 2 : u | m*n and gcd(u,m) = 1, yet m is neither 1 nor -1.
-- Line 5 asserts: if u | m*n and gcd(u,m) = 1 then m = 1 or m = -1 (u, m, n integers, line 1).
import Mathlib

namespace P28

theorem witness :
    (2 : ℤ) ∣ 3 * 2 ∧ Int.gcd 2 3 = 1 ∧ (3 : ℤ) ≠ 1 ∧ (3 : ℤ) ≠ -1 := by
  refine ⟨⟨3, by ring⟩, by decide, by decide, by decide⟩

-- the same, phrased as the failure of the line-5 implication at this instance
theorem line5_fails :
    ¬ (∀ u m n : ℤ, u ∣ m * n → Int.gcd u m = 1 → m = 1 ∨ m = -1) := by
  intro h
  rcases h 2 3 2 ⟨3, by ring⟩ (by decide) with h1 | h2
  · exact absurd h1 (by decide)
  · exact absurd h2 (by decide)

end P28
