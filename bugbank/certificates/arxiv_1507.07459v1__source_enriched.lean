import Mathlib.Combinatorics.Graph.Basic
import Mathlib.Data.Fintype.Powerset
import Mathlib.Data.Finset.Pairwise
import Mathlib.Data.Rat.Cast.Order
import Mathlib.Tactic

set_option autoImplicit false
set_option maxRecDepth 100000
set_option maxHeartbeats 4000000
namespace Arxiv1507_07459v1Mathlib

abbrev Atom := Fin 9
abbrev Name := Fin 5
/-- Names 0,1 are m1,m2, and names 2,3,4 are f1,f2,f3.
Atoms 0,1,2 are a1,a2,a3; 3,4,5 are b1,b2,b3; 6,7,8 are c1,c2,c3. -/
def sets (i : Name) : Finset Atom :=
  if i = 0 then {0,1,2} else if i = 1 then {3,4,5}
  else if i = 2 then {0,3,6} else if i = 3 then {0,3,7} else {0,3,8}
def M : Finset Name := {0,1}
def F : Finset Name := {2,3,4}
def Packing (B : Finset Name) : Prop :=
  (B : Set Name).Pairwise (fun i j => Disjoint (sets i) (sets j))
instance (B : Finset Name) : Decidable (Packing B) := by
  unfold Packing Set.Pairwise
  infer_instance

def numerator (i : Name) : ℕ := if i ∈ F then 1 else 0
noncomputable def realWeight (i : Name) : ℝ := (numerator i : ℝ) / 3
def neighbors (B : Finset Name) : Finset Name :=
  M.filter (fun m => ∃ i ∈ B, ¬Disjoint (sets i) (sets m))
def replacement (B : Finset Name) : Finset Name := (M \ neighbors B) ∪ B
/-- The source F2 is derived from positive LP support and exactly two intersections with M. -/
def F2 : Finset Name := Finset.univ.filter (fun i =>
  0 < numerator i ∧ (M.filter (fun m => ¬Disjoint (sets i) (sets m))).card = 2)

/-- The actual Mathlib multigraph, with distinct edges indexed by the three f-sets. -/
def H : Graph Name Name := Graph.banana 0 1 (F2 : Set Name)
instance (e u v : Name) : Decidable (H.IsLink e u v) := by
  unfold H Graph.banana
  infer_instance
/-- Internal edges of the induced graph on X, derived by their endpoints. -/
def internalEdges (X : Finset Name) : Finset Name :=
  F2.filter (fun e => ∃ u ∈ X, ∃ v ∈ X, H.IsLink e u v)

/-- The five names denote five distinct 3-element sets. -/
theorem uniform_and_distinct : (∀ i, (sets i).card = 3) ∧ Function.Injective sets := by
  decide

theorem maximum_packing : Packing M ∧ ∀ B : Finset Name, Packing B → B.card ≤ M.card := by
  decide
/-- This verifies every possible finite exchange, hence every local-optimality radius,
including the source radius 8 log₂(5). -/
theorem no_improving_exchange : ∀ B : Finset Name,
    Packing B → (replacement B).card ≤ M.card := by
  decide

/-- Stronger than all intersecting-family and element constraints: every subfamily
has total weight at most one, because the total nonnegative weight is one. -/
theorem numerator_bound : ∀ B : Finset Name, (∑ i ∈ B, numerator i) ≤ 3 := by
  decide

theorem real_feasibility :
    (∀ i, 0 ≤ realWeight i) ∧ ∀ B : Finset Name, (∑ i ∈ B, realWeight i) ≤ 1 := by
  constructor
  · intro i
    unfold realWeight
    positivity
  · intro B
    have h : (∑ i ∈ B, (numerator i : ℝ)) ≤ 3 := by
      exact_mod_cast numerator_bound B
    simp only [realWeight, ← Finset.sum_div]
    linarith

theorem witness_weights :
    realWeight 0 = 0 ∧ realWeight 1 = 0 ∧
    realWeight 2 = 1/3 ∧ realWeight 3 = 1/3 ∧ realWeight 4 = 1/3 := by
  norm_num [realWeight, numerator, F]

theorem source_support :
    (∀ i, 0 < realWeight i ↔ i ∈ F) ∧ F2 = F := by
  constructor
  · intro i
    simp only [realWeight, numerator]
    split_ifs with hi <;> simp_all
  · decide

/-- The auxiliary graph's incidence is exactly positive-F2 membership together
with intersection with both distinct matching sets. Thus the parallel edges
are derived from the packing instance. -/
theorem source_auxiliary_graph :
    H.vertexSet = (M : Set Name) ∧ H.edgeSet = (F2 : Set Name) ∧
    ∀ e u v, H.IsLink e u v ↔
      e ∈ F2 ∧ u ∈ M ∧ v ∈ M ∧ u ≠ v ∧
      ¬Disjoint (sets e) (sets u) ∧ ¬Disjoint (sets e) (sets v) := by
  refine ⟨by ext i; simp [H, M],rfl,?_⟩
  decide

theorem edge_excess_but_not_packing :
    M.card = 2 ∧ (internalEdges M).card = 3 ∧ internalEdges M = F ∧
    M.card < (internalEdges M).card ∧ neighbors (internalEdges M) = M ∧
    (replacement (internalEdges M)).card = 3 ∧ ¬Packing (internalEdges M) := by
  decide

/-- Full original witness: a globally maximum packing, a real feasible LP point,
the source-derived auxiliary multigraph, and its three internal edges on two
vertices, whose represented family fails to be a packing. -/
theorem original_witness_refutes :
    (∀ i, (sets i).card = 3) ∧ Function.Injective sets ∧
    Packing M ∧ (∀ B : Finset Name, Packing B → B.card ≤ M.card) ∧
    (∀ B : Finset Name, Packing B → (replacement B).card ≤ M.card) ∧
    (∀ i, 0 ≤ realWeight i) ∧
    (∀ B : Finset Name, (∑ i ∈ B, realWeight i) ≤ 1) ∧
    F2 = F ∧ M.card = 2 ∧ (internalEdges M).card = 3 ∧
    ¬Packing (internalEdges M) := by
  exact ⟨uniform_and_distinct.1,uniform_and_distinct.2,
    maximum_packing.1,maximum_packing.2,no_improving_exchange,
    real_feasibility.1,real_feasibility.2,source_support.2,
    edge_excess_but_not_packing.1,edge_excess_but_not_packing.2.1,
    edge_excess_but_not_packing.2.2.2.2.2.2⟩

/-- The precise intermediate assertion fails for the original source instance. -/
theorem refutes_edge_excess_implies_improvement :
    ¬ (M.card < (internalEdges M).card →
      Packing (internalEdges M) ∧ M.card < (replacement (internalEdges M)).card) := by
  intro h
  exact edge_excess_but_not_packing.2.2.2.2.2.2
    (h edge_excess_but_not_packing.2.2.2.1).1

end Arxiv1507_07459v1Mathlib
#print axioms Arxiv1507_07459v1Mathlib.original_witness_refutes
