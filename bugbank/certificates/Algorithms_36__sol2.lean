import Mathlib.Combinatorics.SimpleGraph.Acyclic
import Mathlib.Combinatorics.SimpleGraph.Connectivity.Finite
set_option autoImplicit false
namespace ProofCerts.Alg36
namespace Small
def G : SimpleGraph (Fin 2) := ⊤
def e : Sym2 (Fin 2) := s(0,1)
instance : DecidableRel G.Adj := by unfold G; infer_instance
theorem isTree : G.IsTree := by
  rw [SimpleGraph.isTree_iff_connected_and_card]
  constructor
  · decide
  · rw [Nat.card_eq_fintype_card, Nat.card_eq_fintype_card]; decide

theorem sol2_refutation :
    G.IsTree ∧ e ∈ G.edgeFinset ∧ insert e G.edgeFinset = G.edgeFinset ∧
    (insert e G.edgeFinset).card ≠ 2 := by
  exact ⟨isTree,by decide,by decide,by decide⟩

def path : G.Walk 0 1 := .cons (by decide) .nil
theorem sol4_refutation :
    G.IsTree ∧ path.IsPath ∧ e ∈ path.edges ∧ e ∈ G.edgeFinset ∧
    ¬ (G.deleteEdges {e}).Reachable 0 1 := by
  refine ⟨isTree,?_,?_,?_,?_⟩
  · simp [path, SimpleGraph.Walk.isPath_def]
  all_goals decide
end Small
namespace Large
abbrev V := Fin 4
def t1Edges : Finset (Sym2 V) := {s(0,3),s(0,1),s(3,2)}
def t2Edges : Finset (Sym2 V) := {s(0,2),s(2,1),s(1,3)}
def T1 : SimpleGraph V := SimpleGraph.fromEdgeSet (t1Edges : Set (Sym2 V))
def T2 : SimpleGraph V := SimpleGraph.fromEdgeSet (t2Edges : Set (Sym2 V))
instance : DecidableRel T1.Adj := by unfold T1 t1Edges; infer_instance
instance : DecidableRel T2.Adj := by unfold T2 t2Edges; infer_instance
def e : Sym2 V := s(0,3)
def f : Sym2 V := s(1,2)
def path : T2.Walk 0 3 := .cons (show T2.Adj 0 2 by decide) (.cons (show T2.Adj 2 1 by decide) (.cons (show T2.Adj 1 3 by decide) .nil))
theorem t1_tree : T1.IsTree := by
  rw [SimpleGraph.isTree_iff_connected_and_card]
  constructor
  · decide
  · rw [Nat.card_eq_fintype_card, Nat.card_eq_fintype_card]; decide
theorem t2_tree : T2.IsTree := by
  rw [SimpleGraph.isTree_iff_connected_and_card]
  constructor
  · decide
  · rw [Nat.card_eq_fintype_card, Nat.card_eq_fintype_card]; decide
set_option maxRecDepth 4096 in
set_option maxHeartbeats 0 in
theorem sol3_refutation :
    T1.IsTree ∧ T2.IsTree ∧ e ∈ T1.edgeFinset ∧
    path.IsPath ∧ f ∈ path.edges ∧
    (T1.deleteEdges {e}).Reachable 0 1 ∧ (T1.deleteEdges {e}).Reachable 3 2 ∧
    ¬ (T2.deleteEdges {f}).Reachable 1 0 ∧ ¬ (T2.deleteEdges {f}).Reachable 2 3 := by
  refine ⟨t1_tree,t2_tree,?_,?_,?_,?_,?_,?_,?_⟩
  · decide
  · simp [path, SimpleGraph.Walk.isPath_def]
  all_goals decide
end Large
end ProofCerts.Alg36
#print axioms ProofCerts.Alg36.Small.sol2_refutation
#print axioms ProofCerts.Alg36.Large.sol3_refutation
#print axioms ProofCerts.Alg36.Small.sol4_refutation
