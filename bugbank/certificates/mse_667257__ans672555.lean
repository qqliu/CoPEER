import Mathlib

/-! The written sum includes the multiplicity choose(k,j) outside the tenth
power. We refute that literal sufficient bound only: the actual existence of
17 sum-distinct vectors is not disproved. Standard binomial coefficients,
rational powers and finite sums replace the bespoke Pascal/list arithmetic. -/
namespace MSE667257
open scoped BigOperators

def term (k j : ℕ) : ℚ :=
  Nat.choose 17 k * Nat.choose k j * ((Nat.choose k j : ℚ) / 2^k)^10

def unionBound : ℚ := ∑ k ∈ Finset.Icc 1 17, ∑ j ∈ Finset.range (k+1), term k j

theorem term_nonneg (k j : ℕ) : 0 ≤ term k j := by
  unfold term
  positivity

theorem single_term_value :
    term 10 5 = 150845028992571913896897 / 37778931862957161709568 := by
  norm_num [term, Nat.choose]

theorem single_term_exceeds_one : 1 < term 10 5 := by
  rw [single_term_value]
  norm_num

theorem single_term_le_sum : term 10 5 ≤ unionBound := by
  calc
    term 10 5 ≤ ∑ j ∈ Finset.range (10+1), term 10 j := by
      exact Finset.single_le_sum (fun j _ => term_nonneg 10 j) (by decide)
    _ ≤ unionBound := by
      exact Finset.single_le_sum
        (fun k _ => Finset.sum_nonneg (fun j _ => term_nonneg k j)) (by decide)

theorem certificate : 1 < unionBound :=
  lt_of_lt_of_le single_term_exceeds_one single_term_le_sum

theorem main_refutation : ¬ unionBound < 1 := not_lt.mpr (le_of_lt certificate)
end MSE667257
