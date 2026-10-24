import Mathlib.Data.ZMod.Basic
import Mathlib.Data.Nat.Prime.Basic

/-! The claimed removal of primality of the exponent fails for p=4,q=7.
The field and powers below are Mathlib's ZMod; q's primality and the
nonzero input restrictions are part of the certified statement. -/
namespace MSE_57162_ans57165

theorem mse_57162__ans57165_refutation :
    Nat.Prime 7 ∧ ¬ Nat.Prime 4 ∧
    7 % 4 ≠ 1 ∧ ¬ Nat.Coprime 4 (7 - 1) ∧
    (3 : ZMod 7) ≠ 0 ∧ (4 : ZMod 7) ≠ 0 ∧
    (3 : ZMod 7) ≠ 4 ∧ (3 : ZMod 7) ^ 4 = (4 : ZMod 7) ^ 4 ∧
    ¬ Function.Injective (fun x : ZMod 7 => x ^ 4) := by
  decide

/-- The prime-exponent control really is injective on the whole field. -/
theorem mse_57162__ans57165_negative_control :
    Nat.Prime 5 ∧ Nat.Coprime 5 (7 - 1) ∧
    Function.Injective (fun x : ZMod 7 => x ^ 5) := by
  decide
end MSE_57162_ans57165
