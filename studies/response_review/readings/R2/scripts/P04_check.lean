import Mathlib

/- P04: the witness supplied by the critic's response, f x = x + 1 and g x = max 0 (x - 1)
   on ℕ, against line 14 ("functions with g ∘ f injective but g not injective do not exist").
   Note ℕ subtraction is truncated, so `max 0 (x - 1)` is literally the response's g. -/
theorem P04_witness :
    Function.Injective (fun x : ℕ => max 0 ((x + 1) - 1)) ∧
      ¬ Function.Injective (fun x : ℕ => max 0 (x - 1)) := by
  refine ⟨fun a b h => by simpa using h, fun hg => ?_⟩
  have h : (0 : ℕ) = 1 := hg (by decide)
  exact absurd h (by decide)
