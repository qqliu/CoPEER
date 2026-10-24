import Mathlib.Combinatorics.SimpleGraph.Connectivity.Finite
import Mathlib.Tactic.FinCases
set_option autoImplicit false
namespace ProofCerts.Alg33b
abbrev V := Fin 4
def cycleEdges : Finset (Sym2 V) := {s(0,1),s(1,2),s(2,3),s(3,0)}
def G : SimpleGraph V := SimpleGraph.fromEdgeSet (cycleEdges : Set (Sym2 V))
instance : DecidableRel G.Adj := by unfold G cycleEdges; infer_instance
def F : Finset (Sym2 V) := {s(1,2),s(3,0)}
def HA : Finset (Sym2 V) := {s(0,1)}
def A : Set V := {0,1}
instance : DecidablePred A := fun x => inferInstanceAs (Decidable (x = 0 ∨ x = 1))
def IsCut (S : Finset (Sym2 V)) : Prop := ¬ (G.deleteEdges (S : Set (Sym2 V))).Connected
instance (S : Finset (Sym2 V)) : Decidable (IsCut S) := by unfold IsCut G cycleEdges; infer_instance
/-- Standard connectivity of the actual induced subgraph. -/
def IsCutA (S : Finset (Sym2 V)) : Prop := ¬ ((G.deleteEdges (S : Set (Sym2 V))).induce A).Connected
instance (S : Finset (Sym2 V)) : Decidable (IsCutA S) := by unfold IsCutA A G cycleEdges; infer_instance

def IsMinimalCut (S : Finset (Sym2 V)) : Prop := IsCut S ∧ ∀ T ∈ S.powerset, T ≠ S → ¬ IsCut T
instance (S : Finset (Sym2 V)) : Decidable (IsMinimalCut S) := by unfold IsMinimalCut; infer_instance
def IsMinimalCutA (S : Finset (Sym2 V)) : Prop := IsCutA S ∧ ∀ T ∈ S.powerset, T ≠ S → ¬ IsCutA T
instance (S : Finset (Sym2 V)) : Decidable (IsMinimalCutA S) := by unfold IsMinimalCutA; infer_instance
set_option maxRecDepth 20000 in
set_option maxHeartbeats 0 in
theorem minimal_cut_of_induced_part_need_not_cut_G :
    G.Connected ∧ IsMinimalCut F ∧
    (∀ v : V, (G.deleteEdges (F : Set (Sym2 V))).Reachable 0 v ↔ v ∈ A) ∧
    IsMinimalCutA HA ∧ ¬ IsCut HA := by
  refine ⟨?_,?_,?_,?_,?_⟩
  · unfold G cycleEdges
    decide
  · decide
  · intro v
    fin_cases v <;> unfold A G cycleEdges F <;> decide
  · decide
  · decide
end ProofCerts.Alg33b
#print axioms ProofCerts.Alg33b.minimal_cut_of_induced_part_need_not_cut_G
