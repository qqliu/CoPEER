import Mathlib.Data.Nat.PrimeFin
import Mathlib.NumberTheory.Divisors
import Mathlib.Tactic.NormNum

/-!
Source: https://math.stackexchange.com/a/1452726, Lemma 2.
At m=2,n=3, 6 does not divide n, but 1+2^3=9 has one distinct
prime factor and n has two divisors. The author's variant counting only primes
above 4 also fails. Mathlib primeFactors/divisors replace handwritten factoring.
-/
namespace MSE1449690

def omegaStd (n : ℕ) : ℕ := n.primeFactors.card
def omegaGt4 (n : ℕ) : ℕ := (n.primeFactors.filter (4 < ·)).card
def dCount (n : ℕ) : ℕ := n.divisors.card

theorem lemma_two_counterexample :
    2 ≤ (2 : ℕ) ∧ 1 ≤ (3 : ℕ) ∧ ¬ 6 ∣ (3 : ℕ) ∧
    omegaStd (1 + 2 ^ 3) = 1 ∧ dCount 3 = 2 ∧
    ¬ dCount 3 ≤ omegaStd (1 + 2 ^ 3) ∧
    ¬ dCount 3 ≤ omegaGt4 (1 + 2 ^ 3) := by
  have hf : (1 + 2 ^ 3 : ℕ).primeFactors = {3} := by
    exact Nat.primeFactors_prime_pow (by decide : (2 : ℕ) ≠ 0) (by decide : Nat.Prime 3)
  change (9 : ℕ).primeFactors = {3} at hf
  have hd : dCount 3 = 2 := by decide
  norm_num [omegaStd, omegaGt4, hf, hd] <;> decide

theorem even_exponent_counterexample :
    ¬ 6 ∣ (2 : ℕ) ∧ omegaStd (1 + 2 ^ 2) = 1 ∧ dCount 2 = 2 := by
  have hf : (1 + 2 ^ 2 : ℕ).primeFactors = {5} :=
    Nat.Prime.primeFactors (by decide : Nat.Prime 5)
  change (5 : ℕ).primeFactors = {5} at hf
  have hd : dCount 2 = 2 := by decide
  norm_num [omegaStd, hf, hd]

end MSE1449690
