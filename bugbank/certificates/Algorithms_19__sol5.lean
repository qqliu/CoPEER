import Mathlib

namespace QEDReview19sol5

abbrev V := Fin 3

def graph : SimpleGraph V := ⊤

def tree : SimpleGraph V where
  Adj a b := a ≠ b ∧ (a = 2 ∨ b = 2)
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
def cut : Finset (Sym2 V) := graph.edgeFinset.filter (fun e => (0 : V) ∈ e)
theorem refuted : IsMST tree ∧ s(0,1) ∈ cut ∧
    (∀ f ∈ cut, edgeWeight s(0,1) ≤ edgeWeight f) ∧
    s(0,1) ∉ tree.edgeFinset := by
  exact ⟨tree_isMST, by decide, by decide, by decide⟩
end QEDReview19sol5
