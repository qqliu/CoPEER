import Mathlib.Topology.Separation.Basic
import Mathlib.Tactic.NormNum
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.Ring
import Mathlib.Tactic.FinCases

/- Human-guided audit: Same Sierpinski topology on two points is now an actual TopologicalSpace. Every intersection is open and T0 holds, yet{0} is not open. Replaces bespoke topology/separation flags.
   Original witness action: KEPT. -/
namespace Audit_reddit_math_f2hec
-- Bool labels false=0,true=1. The upper-set topology is exactly ∅,{1},{0,1}.
@[reducible] def sierpinski : TopologicalSpace Bool where
  IsOpen s := false ∈ s → true ∈ s
  isOpen_univ := by simp
  isOpen_inter := by intro s t hs ht h; exact ⟨hs h.1,ht h.2⟩
  isOpen_sUnion := by
    intro S hS h
    rcases h with ⟨s,hs,h⟩
    exact ⟨s,hs,hS s hs h⟩
local instance : TopologicalSpace Bool := sierpinski
lemma sep : ∀ x y : Bool, x ≠ y → ∃ s : Set Bool, IsOpen s ∧ ¬ (x ∈ s ↔ y ∈ s) := by
  intro x y h
  cases x <;> cases y <;> simp_all
  all_goals exact ⟨{true}, by intro h; exact Bool.noConfusion h, by simp⟩
theorem certificate : T0Space Bool ∧
    (∀ S : Set (Set Bool), (∀ s ∈ S, IsOpen s) → IsOpen (⋂₀ S)) ∧
    ¬ DiscreteTopology Bool := by
  refine ⟨?_,?_,?_⟩
  · rw [t0Space_iff_exists_isOpen_xor_mem]
    intro x y h
    obtain ⟨s,hs,hh⟩ := sep x y h
    exact ⟨s,hs,by simpa only [xor_iff_not_iff] using hh⟩
  · intro S hS h s hs; exact hS s hs (h s hs)
  · intro h
    have ht := @isOpen_discrete Bool sierpinski h {false}
    change (false ∈ ({false} : Set Bool) → true ∈ ({false} : Set Bool)) at ht
    simpa using ht (by simp)
end Audit_reddit_math_f2hec
