import Mathlib.Data.Nat.PrimeFin
import Mathlib.NumberTheory.PrimeCounting
import Mathlib.Order.Interval.Finset.Nat

/-!
Source: https://math.stackexchange.com/a/2583979, line 0005.
At k=3,n=6=lcm(1,2,3), only 7 in [6,9] has a prime factor >3.
The claimed lower bound is 3+1-π(3)=2. This is the equality boundary in n≥lcm.
Mathlib primality, primeCounting, lcm and Finset.Icc replace custom algorithms.
-/
namespace mse_2128949__ans2583979

def hasBigPrimeFactor (k m : ℕ) : Prop := ∃ p ∈ Finset.Icc (k + 1) m, Nat.Prime p ∧ p ∣ m
instance (k m : ℕ) : Decidable (hasBigPrimeFactor k m) := inferInstanceAs
  (Decidable (∃ p ∈ Finset.Icc (k + 1) m, Nat.Prime p ∧ p ∣ m))

def bigCount (k n : ℕ) : ℕ :=
  ((Finset.Icc n (n + k)).filter (hasBigPrimeFactor k)).card

theorem boundary_counterexample :
    Nat.lcm (Nat.lcm 1 2) 3 = 6 ∧
    Nat.primeCounting 3 = 2 ∧
    ((Finset.Icc 6 9).filter (hasBigPrimeFactor 3)) = {7} ∧
    bigCount 3 6 = 1 ∧ ¬ 3 + 1 - Nat.primeCounting 3 ≤ bigCount 3 6 := by
  decide

end mse_2128949__ans2583979
