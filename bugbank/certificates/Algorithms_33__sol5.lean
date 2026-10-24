import Mathlib.Combinatorics.SimpleGraph.Connectivity.Finite
set_option autoImplicit false
namespace ProofCerts.Alg33
abbrev V := Fin 3
def G : SimpleGraph V := ⊤
instance : DecidableRel G.Adj := by unfold G; infer_instance
def C1 : Finset (Sym2 V) := {s(0,1),s(0,2)}
def C2 : Finset (Sym2 V) := {s(0,1),s(1,2)}
/-- Edges of the cut induced by the singleton vertex a. -/
def singletonCut (a : V) : Finset (Sym2 V) :=
  G.edgeFinset.filter (fun e => ∃ b : V, b ≠ a ∧ e = s(a,b))
def IsCut (S : Finset (Sym2 V)) : Prop := ¬ (G.deleteEdges (S : Set (Sym2 V))).Connected
instance (S : Finset (Sym2 V)) : Decidable (IsCut S) := by unfold IsCut G; infer_instance
/-- Inclusion minimality quantifies over every proper subset, not just one-edge deletions. -/
def IsMinimal (S : Finset (Sym2 V)) : Prop := IsCut S ∧ ∀ T ∈ S.powerset, T ≠ S → ¬ IsCut T
instance (S : Finset (Sym2 V)) : Decidable (IsMinimal S) := by unfold IsMinimal; infer_instance
set_option maxRecDepth 4096 in
set_option maxHeartbeats 0 in
theorem C1_minimal : IsMinimal C1 := by decide
set_option maxRecDepth 4096 in
set_option maxHeartbeats 0 in
theorem C2_minimal : IsMinimal C2 := by decide
 theorem minimal_cuts_with_common_edge_need_not_be_equal :
    C1 = singletonCut 0 ∧ C2 = singletonCut 1 ∧
    IsMinimal C1 ∧ IsMinimal C2 ∧ (C1 ∩ C2).Nonempty ∧ C1 ≠ C2 := by
  exact ⟨by decide,by decide,C1_minimal,C2_minimal,by decide,by decide⟩
end ProofCerts.Alg33
#print axioms ProofCerts.Alg33.minimal_cuts_with_common_edge_need_not_be_equal
