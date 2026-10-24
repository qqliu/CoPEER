/- P44: Lean check of exactly the supplied witness for line 25,
   "For n=2, x=1, y=1, the left side is 2 while the right side equals 3."
   Line 25 asserts  x + y = sum_{i=0}^{1} (n choose i) * x^i * y^(n-i)
   (line 3: x, y any integers; n the induction variable of line 19). -/
import Mathlib

-- the instantiation n = 2, x = y = 1 : the two sides are 2 and 3
theorem P44_sides :
    ((1 : ℤ) + 1) = 2 ∧
      (∑ i ∈ Finset.range 2, (Nat.choose 2 i : ℤ) * (1 : ℤ) ^ i * (1 : ℤ) ^ (2 - i)) = 3 := by
  refine ⟨by norm_num, ?_⟩
  simp [Finset.sum_range_succ]

-- hence line 25, read as an identity for all n and all integers x, y, is false
theorem P44_line25_false :
    ¬ (∀ (n : ℕ) (x y : ℤ),
        x + y = ∑ i ∈ Finset.range 2, (Nat.choose n i : ℤ) * x ^ i * y ^ (n - i)) := by
  intro h
  have := h 2 1 1
  rw [P44_sides.2] at this
  norm_num at this
