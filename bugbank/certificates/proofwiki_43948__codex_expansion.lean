import Mathlib.Combinatorics.SimpleGraph.Acyclic
import Mathlib.Combinatorics.SimpleGraph.Connectivity.Finite
import Mathlib.Tactic

/-!
Human-review repair of proofwiki_43948__codex_expansion.

Source snapshot: ProofWiki, "Edge is Minimum Weight Bridge iff in All Minimum
Spanning Trees", stored in records_proofwiki_codex_expansion.jsonl. The source
THEOREM states the biconditional. Its sufficient-direction proof is marked
"proof wanted"; that marker is not a mathematical claim and must not be the
challenged quotation. This certificate refutes the right-to-left implication
of the theorem as written, where the source explicitly links "bridge" to the
graph-theoretic bridge definition.

The original witness is unchanged: the triangle on vertices 0,1,2 has weights
01 ↦ 1, 12 ↦ 2, 02 ↦ 3. Its three spanning trees cost 3,4,5; hence 01 belongs
to its unique minimum spanning tree, but removing 01 leaves a connected graph.

All graph, edge, connectivity, spanning-tree, and bridge notions are Mathlib's:
SimpleGraph, Sym2, Connected, IsTree, and IsBridge. The finite classification
below ranges over EVERY SimpleGraph on these same vertices, and the weight is
summed over Mathlib's edgeFinset. Mathlib's finite-graph reachability decision
procedure and isTree_iff_connected_and_card establish the tree classification.
IsMST merely states the defining optimization over all spanning trees; no
minimum-spanning-tree definition was found in the pinned Mathlib graph library.
All finite checks use kernel `decide`, without native_decide or extra axioms.
-/

namespace ProofWiki43948CodexExpansion
open SimpleGraph
abbrev V := Fin 3

def graph (a b c : Bool) : SimpleGraph V where
  Adj x y := (a = true ∧ ((x = 0 ∧ y = 1) ∨ (x = 1 ∧ y = 0))) ∨
    (b = true ∧ ((x = 1 ∧ y = 2) ∨ (x = 2 ∧ y = 1))) ∨
    (c = true ∧ ((x = 0 ∧ y = 2) ∨ (x = 2 ∧ y = 0)))
  symm := fun x y h => by aesop
  loopless := ⟨fun x => by fin_cases x <;> simp⟩

instance (a b c : Bool) : DecidableRel (graph a b c).Adj := by
  unfold graph; infer_instance

def triangle : SimpleGraph V := graph true true true
def tree0112 : SimpleGraph V := graph true true false
def tree0102 : SimpleGraph V := graph true false true
def tree1202 : SimpleGraph V := graph false true true

instance : DecidableRel triangle.Adj := by unfold triangle; infer_instance
instance : DecidableRel tree0112.Adj := by unfold tree0112; infer_instance
instance : DecidableRel tree0102.Adj := by unfold tree0102; infer_instance
instance : DecidableRel tree1202.Adj := by unfold tree1202; infer_instance


noncomputable def weight (e : Sym2 V) : ℕ :=
  if e = s(0,1) then 1 else if e = s(1,2) then 2 else if e = s(0,2) then 3 else 0
noncomputable def cost (H : SimpleGraph V) : ℕ := by
  classical
  exact ∑ e ∈ H.edgeFinset, weight e

def IsMST (H : SimpleGraph V) : Prop :=
  H ≤ triangle ∧ H.IsTree ∧ ∀ K : SimpleGraph V, K ≤ triangle → K.IsTree → cost H ≤ cost K

lemma tree_test (a b c : Bool) : (graph a b c).IsTree ↔
    (graph a b c).Connected ∧ Fintype.card (graph a b c).edgeSet + 1 = 3 := by
  rw [isTree_iff_connected_and_card, Nat.card_eq_fintype_card, Nat.card_eq_fintype_card]
  rfl

lemma graph_enumeration (H : SimpleGraph V) : ∃ a b c, H = graph a b c := by
  classical
  refine ⟨decide (H.Adj 0 1), decide (H.Adj 1 2), decide (H.Adj 0 2), ?_⟩
  ext x y
  fin_cases x <;> fin_cases y <;> simp [graph] <;> exact H.adj_comm _ _

lemma graph_eq_iff (a b c d e f : Bool) :
    graph a b c = graph d e f ↔ a = d ∧ b = e ∧ c = f := by
  constructor
  · intro h
    have h01 := congrArg (fun H : SimpleGraph V => H.Adj 0 1) h
    have h12 := congrArg (fun H : SimpleGraph V => H.Adj 1 2) h
    have h02 := congrArg (fun H : SimpleGraph V => H.Adj 0 2) h
    simp [graph] at h01 h12 h02
    exact ⟨h01, h12, h02⟩
  · rintro ⟨rfl,rfl,rfl⟩; rfl

lemma spanning_tree_enumeration (H : SimpleGraph V) :
    H.IsTree ↔ H = tree0112 ∨ H = tree0102 ∨ H = tree1202 := by
  obtain ⟨a,b,c,rfl⟩ := graph_enumeration H
  unfold tree0112 tree0102 tree1202
  simp_rw [graph_eq_iff]
  cases a <;> cases b <;> cases c <;>
    rw [tree_test] <;> decide

lemma edgeFinset_graph (a b c : Bool) [Fintype (graph a b c).edgeSet] :
    (graph a b c).edgeFinset =
      (if a then {s(0,1)} else ∅) ∪ (if b then {s(1,2)} else ∅) ∪
        (if c then {s(0,2)} else ∅) := by
  ext e
  induction e using Sym2.ind with | _ x y =>
    fin_cases x <;> fin_cases y <;> cases a <;> cases b <;> cases c <;>
      simp [graph]

lemma costs : cost tree0112 = 3 ∧ cost tree0102 = 4 ∧ cost tree1202 = 5 := by
  simp [cost, tree0112, tree0102, tree1202, edgeFinset_graph, weight]

lemma triangle_eq_top : triangle = ⊤ := by
  ext x y
  fin_cases x <;> fin_cases y <;> decide

lemma isMST_iff (H : SimpleGraph V) : IsMST H ↔ H = tree0112 := by
  have htree : tree0112.IsTree := (spanning_tree_enumeration _).mpr (.inl rfl)
  have hle : tree0112 ≤ triangle := by rw [triangle_eq_top]; exact le_top
  constructor
  · rintro ⟨_, ht, hmin⟩
    rcases (spanning_tree_enumeration H).mp ht with h | h | h
    · exact h
    · have := hmin tree0112 hle htree
      rw [h, costs.1, costs.2.1] at this
      omega
    · have := hmin tree0112 hle htree
      rw [h, costs.1, costs.2.2] at this
      omega
  · rintro rfl
    refine ⟨hle, htree, ?_⟩
    intro K _ hK
    rcases (spanning_tree_enumeration K).mp hK with rfl | rfl | rfl
    · exact le_rfl
    · rw [costs.1, costs.2.1]; decide
    · rw [costs.1, costs.2.2]; decide

lemma triangle_connected : triangle.Connected := by
  change (graph true true true).Connected
  decide

lemma connected_after_deleting_01 :
    (triangle.deleteEdges {s(0,1)}).Connected := by
  change ((graph true true true).deleteEdges {s(0,1)}).Connected
  decide

lemma edge01_not_bridge : ¬ triangle.IsBridge s(0,1) := by
  rw [SimpleGraph.isBridge_iff]
  exact fun h => h.2 (connected_after_deleting_01.preconnected 0 1)

lemma distinct_edge_weights :
    ∀ e ∈ triangle.edgeSet, ∀ f ∈ triangle.edgeSet, weight e = weight f → e = f := by
  change ∀ e ∈ (graph true true true).edgeSet,
    ∀ f ∈ (graph true true true).edgeSet, weight e = weight f → e = f
  decide

/-- The graph, weights, unique minimum spanning tree, universal membership,
and false bridge conclusion all refer to Mathlib graphs and trees. -/
theorem refutes_every_mst_implies_minimum_weight_bridge :
    triangle.Connected ∧
    (∀ e ∈ triangle.edgeSet, ∀ f ∈ triangle.edgeSet, weight e = weight f → e = f) ∧
    weight s(0,1) = 1 ∧ weight s(1,2) = 2 ∧ weight s(0,2) = 3 ∧
    (∃! H : SimpleGraph V, IsMST H) ∧
    IsMST tree0112 ∧
    cost tree0112 = 3 ∧ cost tree0102 = 4 ∧ cost tree1202 = 5 ∧
    (∀ H : SimpleGraph V, IsMST H → H.Adj 0 1) ∧
    (triangle.deleteEdges {s(0,1)}).Connected ∧
    ¬ triangle.IsBridge s(0,1) := by
  refine ⟨triangle_connected, distinct_edge_weights, by decide, by decide, by decide,
    ⟨tree0112, (isMST_iff _).mpr rfl, fun H h => (isMST_iff H).mp h⟩,
    (isMST_iff _).mpr rfl, costs.1, costs.2.1, costs.2.2, ?_,
    connected_after_deleting_01, edge01_not_bridge⟩
  intro H h
  rw [(isMST_iff H).mp h]
  decide

theorem negative_control_e02_fails_antecedent :
    IsMST tree0112 ∧ ¬ tree0112.Adj 0 2 ∧
    ¬ (∀ H : SimpleGraph V, IsMST H → H.Adj 0 2) := by
  refine ⟨(isMST_iff _).mpr rfl, by decide, ?_⟩
  intro h
  have hf : ¬ tree0112.Adj 0 2 := by decide
  exact hf (h tree0112 ((isMST_iff _).mpr rfl))

end ProofWiki43948CodexExpansion
