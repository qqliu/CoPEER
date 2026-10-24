import Mathlib.Data.Nat.Prime.Basic

/-!
Source: https://math.stackexchange.com/a/1261609, line 0015.
The author lists (32,5) as a counterexample to a perfect-fifth-power conclusion.
Since 32=2^5, this pair cannot be a counterexample under any hypothesis.
The original certificate substituted four n=2 congruences for a universal
hypothesis; the repaired theorem directly negates the necessary conclusion.
The genuine counterexamples mentioned elsewhere in the answer are unaffected.
-/
namespace MSE1261062

def OriginalHypothesis (a p : ℕ) : Prop :=
  1 < a ∧ ¬ Nat.Prime a ∧ Nat.Prime p ∧ Odd p ∧ Nat.Coprime a p ∧
  ∀ n : ℕ, 2 ≤ n → a ^ (p ^ (n - 2) * (p - 1)) % p ^ n = 1 % p ^ n

def IsCounterexample (a p : ℕ) : Prop :=
  OriginalHypothesis a p ∧ ¬ ∃ z : ℕ, 0 < z ∧ a = z ^ p

theorem listed_32_is_not_a_counterexample : ¬ IsCounterexample 32 5 := by
  intro h
  exact h.2 ⟨2, by decide, by decide⟩

end MSE1261062
