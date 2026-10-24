import Mathlib.Tactic

/-!
Source: https://math.stackexchange.com/a/2414126, lines 0015–0019.
The third listed candidate has values [3,1,1,5,4,5,...]. At n=3 its left side
is f(f(3))+f(4)=3+5=8, whereas 2n=6. We prove failure for every function
with the recorded values, so no tail convention can repair that prefix.
This refutes the third candidate, not existence of other valid functions.
-/
namespace MSE_2414023_ans2414126

def satisfies (f : ℕ → ℕ) : Prop :=
  ∀ n : ℕ, 0 < n → f (f n) + f (n + 1) = 2 * n

theorem third_candidate_fails (f : ℕ → ℕ)
    (h1 : f 1 = 3) (h3 : f 3 = 1) (h4 : f 4 = 5) : ¬ satisfies f := by
  intro h
  have hP3 := h 3 (by decide)
  rw [h3, h1] at hP3
  change 3 + f 4 = 6 at hP3
  omega

theorem P3_forces_f4 (f : ℕ → ℕ) (h1 : f 1 = 3) (h3 : f 3 = 1)
    (h : satisfies f) : f 4 = 3 := by
  have hP3 := h 3 (by decide)
  rw [h3, h1] at hP3
  change 3 + f 4 = 6 at hP3
  omega

end MSE_2414023_ans2414126
