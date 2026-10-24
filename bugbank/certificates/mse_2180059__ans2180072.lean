import Mathlib.Data.ZMod.Basic
import Mathlib.GroupTheory.OrderOfElement
import Mathlib.Tactic.IntervalCases
import Mathlib.Tactic.NormNum

/-!
Source: https://math.stackexchange.com/a/2180072, line 0003.
Modulo p=5, g=2 is a generator, a=g^3=3 has order k=4, and g^(km)=1
but km=12≠4=p-1. Both minimality requirements are proved with Mathlib
orderOf on ZMod 5, replacing a custom bounded modular-order search.
The secondary gcd(p,q) claim also fails with q=2: g^2=4 has order 2.
-/
namespace mse_2180059__ans2180072

theorem order_two_mod_five : orderOf (2 : ZMod 5) = 4 := by
  apply (orderOf_eq_iff (by decide : 0 < (4 : ℕ))).2
  refine ⟨by decide, ?_⟩
  intro m hm hpos
  interval_cases m <;> first | omega | decide

theorem order_three_mod_five : orderOf (3 : ZMod 5) = 4 := by
  apply (orderOf_eq_iff (by decide : 0 < (4 : ℕ))).2
  refine ⟨by decide, ?_⟩
  intro m hm hpos
  interval_cases m <;> first | omega | decide

theorem generator_exponent_equality_is_false :
    Nat.Prime 5 ∧ orderOf (2 : ZMod 5) = 5 - 1 ∧
    (2 : ZMod 5) ^ 3 = 3 ∧ orderOf (3 : ZMod 5) = 4 ∧
    (2 : ZMod 5) ^ (4 * 3) = 1 ∧ (4 * 3 : ℕ) ≠ 5 - 1 := by
  exact ⟨by decide, order_two_mod_five, by decide, order_three_mod_five,
    by decide, by decide⟩

theorem secondary_coprimality_claim_fails :
    Nat.Coprime 5 2 ∧ orderOf (2 : ZMod 5) = 4 ∧
    orderOf ((2 : ZMod 5) ^ 2) = 2 := by
  refine ⟨by decide, order_two_mod_five, ?_⟩
  apply (orderOf_eq_iff (by decide : 0 < (2 : ℕ))).2
  refine ⟨by decide, ?_⟩
  intro m hm hpos
  interval_cases m <;> first | omega | decide

end mse_2180059__ans2180072
