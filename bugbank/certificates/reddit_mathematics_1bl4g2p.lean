import Mathlib.NumberTheory.ArithmeticFunction.Misc
import Mathlib.Tactic.NormNum.Prime
import Mathlib.Tactic.NormNum
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.Ring
import Mathlib.Tactic.FinCases

/- Human-guided audit: Unchanged p=11 generates2^10·23·89, whose divisor sum4421520 differs from2N4192256. Uses Mathlib Nat.Perfect/divisors and divisor-sum multiplicativity instead of an unbridged paired-divisor algorithm.
   Original witness action: KEPT. -/
namespace Audit_reddit_mathematics_1bl4g2p
open scoped BigOperators
theorem certificate : Nat.Prime 11 ∧ ¬ Nat.Perfect (2^(11-1)*(2^11-1)) := by
  constructor
  · norm_num
  · rw [Nat.perfect_iff_sum_divisors_eq_two_mul (by norm_num)]
    have hp2 : Nat.Prime 2 := by norm_num
    have hp23 : Nat.Prime 23 := by norm_num
    have hp89 : Nat.Prime 89 := by norm_num
    rw [show 2^(11-1)*(2^11-1) = (2^10)*23*89 by norm_num]
    rw [Nat.Coprime.sum_divisors_mul (by decide : Nat.Coprime (2^10*23) 89),
      Nat.Coprime.sum_divisors_mul (by decide : Nat.Coprime (2^10) 23)]
    rw [Nat.sum_divisors_prime_pow hp2, hp23.divisors, hp89.divisors]
    norm_num [Finset.sum_range_succ]
end Audit_reddit_mathematics_1bl4g2p
