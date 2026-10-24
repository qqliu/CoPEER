import Mathlib.GroupTheory.Sylow
import Mathlib.GroupTheory.Perm.Fin
import Mathlib.GroupTheory.GroupAction.Quotient
import Mathlib.Tactic.NormNum
import Mathlib.Tactic.FinCases

namespace RedditAskmath1tiz0hm
open Equiv
open scoped Pointwise
abbrev G := Perm (Fin 3)
def P : Subgroup G := MulAction.stabilizer G (2 : Fin 3)
def H : Subgroup G := MulAction.stabilizer G (0 : Fin 3)
def g : G := swap 0 1 * swap 1 2
def h : G := swap 1 2
instance : DecidablePred (· ∈ P) := fun x => inferInstanceAs (Decidable (x 2 = 2))
instance : DecidablePred (· ∈ H) := fun x => inferInstanceAs (Decidable (x 0 = 0))
instance : Fact (Nat.Prime 2) := ⟨by decide⟩

theorem cardP : Nat.card P = 2 := by
  rw [Nat.card_eq_fintype_card]
  decide

def PSylow : Sylow 2 G :=
  (IsPGroup.of_card (G:=P) (n:=1) (by simpa only [pow_one] using cardP)).toSylow (by
    have hx := P.card_mul_index
    have hg : Nat.card G = 6 := by norm_num [G, Nat.card_eq_fintype_card, Fintype.card_perm, Nat.factorial]
    rw [cardP,hg] at hx
    have hi : P.index = 3 := by omega
    rw [hi]
    decide)

theorem audited_counterexample :
    (PSylow : Subgroup G) = P ∧ IsPGroup 2 H ∧ h ∈ H ∧
    (∀ k ∈ H, (k*g) • (P : Set G) = g • (P : Set G)) ∧
    g⁻¹*h*g ∈ P ∧ g*h*g⁻¹ ∉ P := by
  refine ⟨rfl, ?_, by decide, ?_, by decide, by decide⟩
  · apply IsPGroup.of_card (n:=1)
    rw [Nat.card_eq_fintype_card]
    decide
  · intro k hk
    rw [leftCoset_eq_iff]
    change ((k*g)⁻¹*g) 2 = 2
    have hk0 : k 0 = 0 := hk
    have hki : k⁻¹ 0 = 0 := by
      apply k.injective
      simpa using hk0.symm
    change g⁻¹ (k⁻¹ (g 2)) = 2
    rw [show g 2 = 0 by decide, hki]
    decide
end RedditAskmath1tiz0hm
