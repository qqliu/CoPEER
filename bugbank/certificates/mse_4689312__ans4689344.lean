import Mathlib.GroupTheory.SpecificGroups.Alternating
import Mathlib.Tactic

/-! Retains both original seven-cycles. The source's standalone classification
of subgroups of S7 is false; its graph-theoretic conclusion is not refuted.
Use actual Mathlib permutations, subgroup closure, element order, Lagrange's
theorem and the alternating-group cardinality. A word of order five excludes
orders 7 and 168; evenness excludes 5040. No search-algorithm correctness
assumption or custom permutation representation is needed. -/
namespace MSE4689312
open Equiv
set_option maxRecDepth 4000
set_option maxHeartbeats 2000000
instance : Fact (Nat.Prime 7) := ⟨by decide⟩
instance : Fact (Nat.Prime 5) := ⟨by decide⟩

def a : Perm (Fin 7) where
  toFun := ![1,2,3,4,5,6,0]
  invFun := ![6,0,1,2,3,4,5]
  left_inv := by decide
  right_inv := by decide

def b : Perm (Fin 7) where
  toFun := ![1,2,3,4,6,0,5]
  invFun := ![5,0,1,2,3,6,4]
  left_inv := by decide
  right_inv := by decide

def generated : Subgroup (Perm (Fin 7)) := Subgroup.closure {a,b}

theorem a_mem : a ∈ generated := Subgroup.subset_closure (by simp)
theorem b_mem : b ∈ generated := Subgroup.subset_closure (by simp)

theorem seven_cycles : orderOf a = 7 ∧ orderOf b = 7 := by
  constructor <;> apply orderOf_eq_prime <;> decide

theorem generated_even : generated ≤ alternatingGroup (Fin 7) := by
  apply (Subgroup.closure_le _).mpr
  intro x hx
  rcases Set.mem_insert_iff.mp hx with rfl | hx
  · change Equiv.Perm.sign a = 1
    decide
  · have : x = b := Set.mem_singleton_iff.mp hx
    subst x
    change Equiv.Perm.sign b = 1
    decide

def word : generated := ⟨a^5*b, generated.mul_mem (generated.pow_mem a_mem 5) b_mem⟩

theorem word_order : orderOf word = 5 := by
  apply orderOf_eq_prime
  · apply Subtype.ext
    change (a^5*b)^5 = 1
    decide
  · intro h
    have h' := congrArg Subtype.val h
    change a^5*b = 1 at h'
    exact (by decide : a^5*b ≠ 1) h'

theorem order_constraints : 5 ∣ Nat.card generated ∧ Nat.card generated ≤ 2520 := by
  refine ⟨word_order ▸ orderOf_dvd_natCard word, ?_⟩
  have h := Nat.card_le_card_of_injective
    (f := fun x : generated => (⟨x.val, generated_even x.property⟩ : alternatingGroup (Fin 7)))
    (by intro x y h; exact Subtype.ext (congrArg (fun z : alternatingGroup (Fin 7) => z.val) h))
  have hc : Nat.card (alternatingGroup (Fin 7)) = 2520 := by
    rw [nat_card_alternatingGroup, Nat.card_fin]
    norm_num [Nat.factorial]
  rw [hc] at h
  exact h

theorem certificate : orderOf a = 7 ∧ orderOf b = 7 ∧
    Nat.card generated ≠ 7 ∧ Nat.card generated ≠ 168 ∧ Nat.card generated ≠ 5040 := by
  refine ⟨seven_cycles.1,seven_cycles.2,?_,?_,?_⟩
  · intro h; have hd := order_constraints.1; rw [h] at hd; norm_num at hd
  · intro h; have hd := order_constraints.1; rw [h] at hd; norm_num at hd
  · have := order_constraints.2
    omega
end MSE4689312
