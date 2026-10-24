import Mathlib
/-! Uses Mathlib primality, divisibility and Euler's totient. -/
namespace ProofWiki130200CodexExpansion

def LargestPrimeFactor (p n : ℕ) : Prop :=
  Nat.Prime p ∧ p ∣ n ∧ ∀ q : ℕ, Nat.Prime q → q ∣ n → q ≤ p

theorem lpf_four : LargestPrimeFactor 2 4 := by
  refine ⟨by norm_num, by norm_num, ?_⟩
  intro q hq hd
  have hb := Nat.le_of_dvd (by norm_num : 0 < 4) hd
  interval_cases q <;> norm_num at *

theorem refutes_strict_lpf_step_at_four :
    1 < (4 : ℕ) ∧ LargestPrimeFactor 2 4 ∧ Nat.totient 4 = 2 ∧
    LargestPrimeFactor 2 (Nat.totient 4) ∧
    ¬ (∀ q, Nat.Prime q → q ∣ Nat.totient 4 → q < 2) := by
  have ht : Nat.totient 4 = 2 := by decide
  refine ⟨by norm_num, lpf_four, ht, ?_, ?_⟩
  · rw [ht]
    exact ⟨by norm_num, dvd_refl _, fun q _ hd => Nat.le_of_dvd (by norm_num) hd⟩
  · intro h
    have := h 2 (by norm_num) (by norm_num [ht])
    omega
end ProofWiki130200CodexExpansion
