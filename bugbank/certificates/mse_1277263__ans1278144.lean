import Mathlib.Data.Nat.Choose.Basic
import Mathlib.Data.Fintype.Pi
import Mathlib.Algebra.BigOperators.Group.Finset.Basic

/-!
Source: https://math.stackexchange.com/a/1278144, lines 0015 and 0019.
The answer counts binary m-tuples of weight u by choose u m instead of choose m u.
With m=2,u=1, exactly two tuples exist and choose 1 2=0.
The displayed identity also fails at n=m=2: its sides are 1 and 3.
This is a local inversion of binomial arguments; the answer's final count is
correct. Nat.choose replaces a hand-coded Pascal triangle.
-/
namespace MSE1277263
open scoped BigOperators

def binaryWeightOne : Finset (Fin 2 → Fin 2) :=
  Finset.univ.filter (fun t => (t 0).val + (t 1).val = 1)

/-- Count the binary vectors using their ordinary natural-number weight. -/
theorem wrong_binomial_count :
    binaryWeightOne.card = 2 ∧ Nat.choose 1 2 = 0 ∧
    binaryWeightOne.card ≠ Nat.choose 1 2 := by decide

/-- The n=m=2 summation has u=0 and u=2 as its only even-parity indices. -/
theorem displayed_identity_is_false :
    Nat.choose 0 2 * Nat.choose 2 1 + Nat.choose 2 2 * Nat.choose 1 0 = 1 ∧
    Nat.choose 3 2 = 3 ∧
    Nat.choose 0 2 * Nat.choose 2 1 + Nat.choose 2 2 * Nat.choose 1 0 ≠ Nat.choose 3 2 := by
  decide

end MSE1277263
