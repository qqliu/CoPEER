import Mathlib

namespace QEDReview18ties

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

/-- The original triangle has weight 1 on edge 01 and weight 2 on edges 02 and 12. -/
noncomputable def weight (H : SimpleGraph V) : ℕ := by
  classical
  exact H.edgeFinset.card + (H.edgeFinset \ {s(0,1)}).card

def IsMST (H : SimpleGraph V) : Prop :=
  H.IsTree ∧ ∀ K : SimpleGraph V, K.IsTree → weight H ≤ weight K

lemma tree_edgeSet : ∀ e : Sym2 V,
    e ∈ tree.edgeSet ↔ e = s(0,1) ∨ e = s(1,2) := by decide
lemma tree_weight : weight tree = 3 := by
  unfold weight
  convert (show ({s(0,1),s(1,2)} : Finset (Sym2 V)).card +
      ({s(0,1),s(1,2)} \ {s(0,1)} : Finset (Sym2 V)).card = 3 by decide) using 1 <;>
    congr 2 <;> ext e <;>
    simp only [SimpleGraph.mem_edgeFinset, tree_edgeSet, Finset.mem_sdiff,
      Finset.mem_insert, Finset.mem_singleton]

lemma lower_bound (H : SimpleGraph V) (h : H.IsTree) : 3 ≤ weight H := by
  classical
  have hc := h.card_edgeFinset
  simp only [Fintype.card_fin] at hc
  have hc' : H.edgeFinset.card = 2 := by omega
  have hd : 0 < (H.edgeFinset \ {s(0,1)}).card := by
    by_contra hh
    have hz : (H.edgeFinset \ {s(0,1)}).card = 0 := by omega
    have hs := Finset.sdiff_eq_empty_iff_subset.mp (Finset.card_eq_zero.mp hz)
    have hle := Finset.card_le_card hs
    simp only [Finset.card_singleton] at hle
    omega
  unfold weight
  omega

theorem tree_isMST : IsMST tree := by
  refine ⟨tree_isTree, fun H hH => ?_⟩
  rw [tree_weight]
  exact lower_bound H hH

def cycle : graph.Walk 0 0 :=
  .cons (by decide : graph.Adj 0 1)
    (.cons (by decide : graph.Adj 1 2) (.cons (by decide : graph.Adj 2 0) .nil))

lemma cycle_isCycle : cycle.IsCycle := by
  simp [cycle, SimpleGraph.Walk.isCycle_def, SimpleGraph.Walk.isTrail_def]

def edgeWeight (e : Sym2 V) : ℕ := if e = s(0,1) then 1 else 2

lemma weight_eq_sum (H : SimpleGraph V) :
    weight H = ∑ e ∈ H.edgeFinset, edgeWeight e := by
  classical
  rw [weight, Finset.sdiff_eq_filter, Finset.card_filter, Finset.card_eq_sum_ones,
    ← Finset.sum_add_distrib]
  congr 1
  · ext e
    simp only [SimpleGraph.mem_edgeFinset]
  · funext e
    simp only [Finset.mem_singleton, edgeWeight]
    split_ifs <;> omega

def IsCycleMaxEdge (e : Sym2 V) : Prop :=
  e ∈ cycle.edges ∧ ∀ f ∈ cycle.edges, edgeWeight f ≤ edgeWeight e

lemma max12 : IsCycleMaxEdge s(1, 2) := by unfold IsCycleMaxEdge; decide
lemma edge12_in_tree : s(1, 2) ∈ tree.edgeFinset := by decide

/-- A cycle-maximum edge belongs to an MST; ties violate the target problem claim. -/
theorem cycle_max_can_be_in_MST :
    IsMST tree ∧ cycle.IsCycle ∧ IsCycleMaxEdge s(1, 2) ∧
      s(1, 2) ∈ tree.edgeFinset :=
  ⟨tree_isMST, cycle_isCycle, max12, edge12_in_tree⟩

end QEDReview18ties
