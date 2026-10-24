import Mathlib.Combinatorics.SimpleGraph.Paths
import Mathlib.GroupTheory.SpecificGroups.Cyclic.Basic
import Mathlib.GroupTheory.Perm.Basic
import Mathlib.Tactic
set_option autoImplicit false
namespace QEDMissingArxiv2503
abbrev V := Fin 3
def Γ : SimpleGraph V := SimpleGraph.fromEdgeSet ({s(0,1),s(1,2)} : Set (Sym2 V))
instance : DecidableRel Γ.Adj := by unfold Γ; infer_instance
def generators : Set (Equiv.Perm V) := {σ | ∃ u v, Γ.Adj u v ∧ σ = Equiv.swap u v}
def G : Subgroup (Equiv.Perm V) := Subgroup.closure generators
def σ : Equiv.Perm V := Equiv.swap 0 1 * Equiv.swap 1 2
def H : Subgroup (Equiv.Perm V) := Subgroup.zpowers σ
theorem sigma_mem : σ ∈ G := by
  apply Subgroup.mul_mem
  · exact Subgroup.subset_closure ⟨0,1,by decide,rfl⟩
  · exact Subgroup.subset_closure ⟨1,2,by decide,rfl⟩
theorem sigma_order : orderOf σ = 3 := by
  letI : Fact (Nat.Prime 3) := ⟨by decide⟩
  apply orderOf_eq_prime
  · decide
  · decide
theorem no_graph_cycles : ∀ v (p : Γ.Walk v v), ¬p.IsCycle := by
  intro v p hp
  have h := hp.isTrail.length_le_card_edgeFinset
  have hc : Γ.edgeFinset.card = 2 := by decide
  rw [hc] at h
  have h3 := hp.three_le_length
  omega
theorem original_witness_refutes :
    H ≤ G ∧ IsCyclic H ∧ Nat.card H = 3 ∧
    ∀ v (p : Γ.Walk v v), ¬ (p.IsCycle ∧ p.length = 3) := by
  refine ⟨?_,?_,?_,?_⟩
  · exact Subgroup.zpowers_le.mpr sigma_mem
  · unfold H; infer_instance
  · change Nat.card (Subgroup.zpowers σ) = 3
    rw [Nat.card_zpowers, sigma_order]
  · intro v p hp; exact no_graph_cycles v p hp.1
end QEDMissingArxiv2503
#print axioms QEDMissingArxiv2503.original_witness_refutes
