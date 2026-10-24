import Mathlib.Data.Nat.PrimeFin
import Mathlib.Data.Nat.Factorial.Basic
import Mathlib.Tactic.NormNum

/-!
Source: https://math.stackexchange.com/a/5018766, lines 0003–0006.
The proof treats numbers with two distinct prime divisors and powers of an odd
prime. The composite number 8 is neither, and is not the excluded number 4.
The missing case is a proof-coverage gap: 8 really does divide 7!.
Mathlib primality, prime factors and factorial replace custom algorithms.
-/
namespace MSE164852

def caseA (n : ℕ) : Prop := 2 ≤ n.primeFactors.card
def caseB (n : ℕ) : Prop :=
  ∃ p k : ℕ, Nat.Prime p ∧ Odd p ∧ 2 ≤ k ∧ n = p ^ k

theorem eight_not_odd_prime_power : ¬ caseB 8 := by
  rintro ⟨p, k, hp, hodd, hk, heq⟩
  have hp8 : p ∣ 8 := by
    rw [heq]
    exact dvd_pow_self p (by omega : k ≠ 0)
  have hp2 : p = 2 :=
    (Nat.prime_dvd_prime_iff_eq hp Nat.prime_two).mp
      (hp.dvd_of_dvd_pow (show p ∣ 2 ^ 3 from hp8))
  subst p
  exact (by decide : ¬ Odd (2 : ℕ)) hodd

theorem omitted_even_prime_power :
    2 ≤ (8 : ℕ) ∧ ¬ Nat.Prime 8 ∧ (8 : ℕ) ≠ 4 ∧
    ¬ caseA 8 ∧ ¬ caseB 8 ∧ 8 ∣ Nat.factorial 7 := by
  refine ⟨by decide, by decide, by decide, ?_,
    eight_not_odd_prime_power, by decide⟩
  have hf : (8 : ℕ).primeFactors = {2} :=
    Nat.primeFactors_prime_pow (by decide : (3 : ℕ) ≠ 0) Nat.prime_two
  change ¬ 2 ≤ (8 : ℕ).primeFactors.card
  rw [hf]
  decide

end MSE164852
