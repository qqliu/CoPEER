import Mathlib

/-!
# Algorithms 18, solution 3: counterexample to the target problem statement

The problem prompt omits the strict-maximum assumption. The supplied solution's
Theorem 1 explicitly restores it; this certificate does not refute that theorem.
The unit-weight triangle refutes only the unqualified target statement.
All graphs, spanning trees, cycles and edge cardinalities use Mathlib definitions.
-/
namespace ProofCerts.Alg18

abbrev V := Fin 3

def graph : SimpleGraph V := ⊤

def tree : SimpleGraph V where
  Adj a b := a ≠ b ∧ (a = 1 ∨ b = 1)
  symm := by intro a b h; exact ⟨h.1.symm, h.2.symm⟩
  loopless := ⟨fun a h => h.1 rfl⟩

instance : DecidableRel tree.Adj := fun _ _ => inferInstanceAs (Decidable (_ ∧ _))
instance : DecidableRel graph.Adj := inferInstanceAs (DecidableRel (⊤ : SimpleGraph V).Adj)

lemma tree_connected : tree.Connected := by decide
lemma tree_card : tree.edgeFinset.card = 2 := by decide

lemma tree_isTree : tree.IsTree := by
  apply SimpleGraph.isTree_iff_connected_and_card.mpr
  refine ⟨tree_connected, ?_⟩
  rw [Nat.card_eq_fintype_card, ← SimpleGraph.edgeFinset_card, tree_card]
  norm_num [Nat.card_eq_fintype_card]

/-- Every edge has unit weight, so the standard total weight is the edge count. -/
noncomputable def weight (H : SimpleGraph V) : ℕ := by
  classical
  exact ∑ _e ∈ H.edgeFinset, 1

def IsMST (H : SimpleGraph V) : Prop :=
  H.IsTree ∧ ∀ K : SimpleGraph V, K.IsTree → weight H ≤ weight K

lemma tree_weight (H : SimpleGraph V) (h : H.IsTree) : weight H = 2 := by
  classical
  have hc := h.card_edgeFinset
  simp only [Fintype.card_fin] at hc
  simp only [weight, Finset.sum_const, smul_eq_mul, mul_one]
  omega

theorem tree_isMST : IsMST tree := by
  refine ⟨tree_isTree, fun H hH => ?_⟩
  rw [tree_weight tree tree_isTree, tree_weight H hH]

def cycle : graph.Walk 0 0 :=
  .cons (by decide : graph.Adj 0 1)
    (.cons (by decide : graph.Adj 1 2) (.cons (by decide : graph.Adj 2 0) .nil))

lemma cycle_isCycle : cycle.IsCycle := by
  simp [cycle, SimpleGraph.Walk.isCycle_def, SimpleGraph.Walk.isTrail_def]

def edgeWeight (_e : Sym2 V) : ℕ := 1

def IsCycleMaxEdge (e : Sym2 V) : Prop :=
  e ∈ cycle.edges ∧ ∀ f ∈ cycle.edges, edgeWeight f ≤ edgeWeight e

lemma max01 : IsCycleMaxEdge s(0, 1) := by unfold IsCycleMaxEdge; decide
lemma edge01_in_tree : s(0, 1) ∈ tree.edgeFinset := by decide

/-- A cycle-maximum edge belongs to an MST; ties violate the target problem claim. -/
theorem cycle_max_can_be_in_MST :
    IsMST tree ∧ cycle.IsCycle ∧ IsCycleMaxEdge s(0, 1) ∧
      s(0, 1) ∈ tree.edgeFinset :=
  ⟨tree_isMST, cycle_isCycle, max01, edge01_in_tree⟩

/-- The counterexample does not satisfy the strict hypothesis in the solution's theorem. -/
theorem no_strict_maximum :
    ¬ ∃ e ∈ cycle.edges, ∀ f ∈ cycle.edges, f ≠ e → edgeWeight f < edgeWeight e := by
  decide

end ProofCerts.Alg18
