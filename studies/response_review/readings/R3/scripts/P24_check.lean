import Mathlib
-- P24: exactly the witness supplied by the response (u = 6, m = 5, n = 6) against source line 5,
-- "If u|mn and gcd(u,m) = 1, then m = +or-1": the hypotheses hold and the conclusion fails.
example : (6 : ℤ) ∣ 5 * 6 ∧ Int.gcd 6 5 = 1 ∧ (5 : ℤ) ≠ 1 ∧ (5 : ℤ) ≠ -1 := by
  refine ⟨⟨5, by norm_num⟩, by norm_num, by norm_num, by norm_num⟩

-- and therefore the universally quantified statement of line 5 is false
example : ¬ (∀ u m n : ℤ, u ∣ m * n → Int.gcd u m = 1 → (m = 1 ∨ m = -1)) := by
  intro h
  rcases h 6 5 6 ⟨5, by norm_num⟩ (by norm_num) with h1 | h1 <;> norm_num at h1
