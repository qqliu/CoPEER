import Mathlib

/-! The asserted divisibility by every n is stronger than the valid
prime-characteristic fact. The witness n=4 is also a prime power, 2^2.
Use Nat.choose and ordinary divisibility, not a bespoke factorial engine. -/
namespace G3refPnv275
theorem refutes_universal_binomial_divisibility :
    1 ≤ (2 : ℕ) ∧ 2 < (4 : ℕ) ∧ 4 = (2 : ℕ)^2 ∧
    Nat.choose 4 2 = 6 ∧ ¬ (4 : ℕ) ∣ Nat.choose 4 2 := by
  decide

theorem negative_control_k_one_is_divisible :
    (4 : ℕ) ∣ Nat.choose 4 1 := by decide

theorem characteristic_two_only_needs_two :
    (2 : ℕ) ∣ Nat.choose 4 2 := by decide
end G3refPnv275
