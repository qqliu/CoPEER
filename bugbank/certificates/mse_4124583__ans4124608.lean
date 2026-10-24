import Mathlib.Data.Nat.Choose.Basic
import Mathlib.Tactic.NormNum

/-! The original worked example is retained: 119 residents in 120 apartments.
After 19 people move into 19 different occupied apartments, the actual count
is 19*choose(6,2)+choose(5,2)=295, not the printed 310. The termination argument
and its monotonicity conclusion are unaffected by this arithmetic typo. -/
namespace MSE4124583

def before : ℕ := Nat.choose 19 2 + 20 * Nat.choose 5 2 + 99 * Nat.choose 0 2
def after : ℕ := Nat.choose 0 2 + 19 * Nat.choose 6 2 + Nat.choose 5 2 + 99 * Nat.choose 0 2

theorem certificate :
    19 + 20 * 5 = 119 ∧ 1 + 20 + 99 = 120 ∧
    19 * 6 + 5 = 119 ∧ 1 + 19 + 1 + 99 = 120 ∧
    before = 371 ∧ after = 295 ∧ after ≠ 310 ∧ after < before := by
  norm_num [before, after, Nat.choose]
end MSE4124583
