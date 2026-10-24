import Mathlib.Algebra.GCDMonoid.Finset
import Mathlib.Data.Fintype.Pi
import Mathlib.Data.Nat.Choose.Basic
import Mathlib.Tactic

/-! Original p=1,k=4,m=1. Mathlib finite functions, finite sums, gcd,
choose and cardinality replace custom positions, lists, BFS and arithmetic. -/
namespace MSE427652
abbrev Position := Fin 4 → Fin 3

def positions : Finset Position := Finset.univ.filter (fun p => ∑ i, (p i).val = 2)
def primitive : Finset Position := positions.filter (fun p => Finset.univ.gcd (fun i => (p i).val) = 1)
def root (p : Position) : Prop := ∃ i, (p i).val = 2
instance (p : Position) : Decidable (root p) := inferInstanceAs (Decidable (∃ i, (p i).val = 2))

def move (p q : Position) : Prop := ∃ i j : Fin 4,
  i ≠ j ∧ 0 < (p j).val ∧ (p j).val ≤ (p i).val ∧
  ∀ r, (q r).val = if r = i then (p i).val - (p j).val else
    if r = j then 2 * (p j).val else (p r).val
instance (p q : Position) : Decidable (move p q) := by unfold move; infer_instance

theorem all_positions_reach_root_in_one : ∀ p ∈ positions,
    root p ∨ ∃ q ∈ positions, move p q ∧ root q := by decide

theorem primitive_count : primitive.card = 6 ∧
    Nat.choose (2^1+4-1) (4-1) - Nat.choose (2^(1-1)+4-1) (4-1) = primitive.card := by decide

theorem certificate :
    (∀ p ∈ positions, root p ∨ ∃ q ∈ positions, move p q ∧ root q) ∧
    primitive.card = 6 ∧ ¬ primitive.card ≤ 4 * (4*(4-1))^(1-1) := by
  exact ⟨all_positions_reach_root_in_one, primitive_count.1, by decide⟩
end MSE427652
