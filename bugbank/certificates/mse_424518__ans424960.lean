import Mathlib.Tactic
import Mathlib.Order.Defs.PartialOrder
import Mathlib.Data.Fin.Basic
import Mathlib.Data.Set.Lattice

/-! A genuine preorder with 0 equivalent to 1 and with 2 incomparable
has no antisymmetric extension, hence no linear-order extension.
The second counterexample checks the actual empty intersection of
relations for a two-element chain. Mathlib order structures and sets
replace handwritten truth-table models. -/
namespace mse_424518__ans424960

def related (x y : Fin 3) : Prop := x = y ∨ (x < 2 ∧ y < 2)
instance : DecidableRel related := fun x y => inferInstanceAs (Decidable (x = y ∨ (x < 2 ∧ y < 2)))

@[reducible] def witnessPreorder : Preorder (Fin 3) where
  le := related
  lt := fun x y => related x y ∧ ¬ related y x
  le_refl := by decide
  le_trans := by decide

theorem incomparable_pair : ¬ related 0 2 ∧ ¬ related 2 0 := by decide

theorem mse_424518__ans424960_existence_step_fails :
    ¬ ∃ L : PartialOrder (Fin 3), ∀ x y, related x y → L.le x y := by
  rintro ⟨L, h⟩
  have h01 := h 0 1 (by decide)
  have h10 := h 1 0 (by decide)
  have heq : (0 : Fin 3) = 1 := L.le_antisymm 0 1 h01 h10
  exact (by decide : (0 : Fin 3) ≠ 1) heq

def chain : Set (Fin 2 × Fin 2) := {p | p.1 ≤ p.2}
def incomparable : Set (Fin 2 × Fin 2) := {p | ¬ p.1 ≤ p.2 ∧ ¬ p.2 ≤ p.1}

theorem no_incomparable_pairs : incomparable = ∅ := by
  ext p
  change (¬ p.1 ≤ p.2 ∧ ¬ p.2 ≤ p.1) ↔ False
  constructor
  · intro hp
    exact hp.1 (le_of_not_ge hp.2)
  · exact False.elim

/-- There are no indices, so every pair is in the intersection. -/
theorem mse_424518__ans424960_intersection_identity_fails
    (extensions : incomparable → Set (Fin 2 × Fin 2)) :
    (⋂ p, extensions p) ≠ chain := by
  intro h
  have hm : ((1 : Fin 2), (0 : Fin 2)) ∈ ⋂ p, extensions p := by
    apply Set.mem_iInter.mpr
    intro p
    have hp := p.property
    have hn : ∀ q : Fin 2 × Fin 2, ¬ (¬ q.1 ≤ q.2 ∧ ¬ q.2 ≤ q.1) := by
      intro q
      omega
    exact False.elim (hn p.val hp)
  rw [h] at hm
  exact (by decide : ¬ ((1 : Fin 2) ≤ 0)) hm

end mse_424518__ans424960
