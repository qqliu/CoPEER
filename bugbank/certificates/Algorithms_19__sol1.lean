import Mathlib

/-!
# Algorithms 19, solution 1: a unique MST with tied cycle maxima

The ambient graph is Mathlib's complete simple graph on four vertices. The star
at vertex zero has weight-one edges; the remaining triangle has weight-two edges.
Spanning trees are `SimpleGraph.IsTree`, and minimality ranges over every simple
graph on this vertex set. There is no bounded reachability or subset-code surrogate.
-/
namespace ProofCerts.Alg19

abbrev V := Fin 4

def graph : SimpleGraph V := ⊤

def star : SimpleGraph V where
  Adj a b := a ≠ b ∧ (a = 0 ∨ b = 0)
  symm := by intro a b h; exact ⟨h.1.symm, h.2.symm⟩
  loopless := ⟨fun a h => h.1 rfl⟩

instance : DecidableRel star.Adj := fun _ _ => inferInstanceAs (Decidable (_ ∧ _))
instance : DecidableRel graph.Adj := inferInstanceAs (DecidableRel (⊤ : SimpleGraph V).Adj)

lemma star_connected : star.Connected := by decide
lemma star_card : star.edgeFinset.card = 3 := by decide

lemma star_isTree : star.IsTree := by
  apply SimpleGraph.isTree_iff_connected_and_card.mpr
  refine ⟨star_connected, ?_⟩
  rw [Nat.card_eq_fintype_card, ← SimpleGraph.edgeFinset_card, star_card]
  norm_num [Nat.card_eq_fintype_card]

lemma tree_card (H : SimpleGraph V) [Fintype H.edgeSet] (h : H.IsTree) :
    H.edgeFinset.card = 3 := by
  have := h.card_edgeFinset
  simp only [Fintype.card_fin] at this
  omega

/-- The total weight: one for every edge, plus one more for every non-star edge. -/
noncomputable def weight (H : SimpleGraph V) : ℕ := by
  classical
  exact H.edgeFinset.card + (H.edgeFinset \ star.edgeFinset).card

/-- This is exactly the usual sum of weights, with star edges of weight one and others two. -/
lemma weight_eq_sum (H : SimpleGraph V) :
    weight H = ∑ e ∈ H.edgeFinset, (if e ∈ star.edgeFinset then 1 else 2 : ℕ) := by
  classical
  rw [weight, Finset.sdiff_eq_filter, Finset.card_filter, Finset.card_eq_sum_ones,
    ← Finset.sum_add_distrib]
  congr 1
  · ext e
    simp only [SimpleGraph.mem_edgeFinset]
  · funext e
    split_ifs <;> omega

def IsMST (H : SimpleGraph V) : Prop :=
  H.IsTree ∧ ∀ K : SimpleGraph V, K.IsTree → weight H ≤ weight K

lemma star_weight : weight star = 3 := by
  rw [weight_eq_sum]
  have hs : (∑ e ∈ star.edgeFinset, (if e ∈ star.edgeFinset then 1 else 2 : ℕ)) =
      star.edgeFinset.card := by
    rw [Finset.card_eq_sum_ones]
    apply Finset.sum_congr rfl
    intro e he
    have hm : e ∈ star.edgeSet := SimpleGraph.mem_edgeFinset.mp he
    simp only [SimpleGraph.mem_edgeFinset, hm, ite_true]
  convert hs.trans star_card using 1
  congr 1
  ext e
  simp only [SimpleGraph.mem_edgeFinset]

theorem star_isMST : IsMST star := by
  classical
  refine ⟨star_isTree, fun H hH => ?_⟩
  rw [star_weight, weight, tree_card H hH]
  omega

theorem mst_unique (H : SimpleGraph V) (hH : IsMST H) : H = star := by
  classical
  have hle := hH.2 star star_isTree
  rw [star_weight, weight, tree_card H hH.1] at hle
  have hz : (H.edgeFinset \ star.edgeFinset).card = 0 := by omega
  have hs : H.edgeFinset ⊆ star.edgeFinset :=
    Finset.sdiff_eq_empty_iff_subset.mp (Finset.card_eq_zero.mp hz)
  apply SimpleGraph.edgeFinset_inj.mp
  exact Finset.eq_of_subset_of_card_le hs (by rw [star_card, tree_card H hH.1])

theorem unique_mst : ∃! H : SimpleGraph V, IsMST H :=
  ⟨star, star_isMST, mst_unique⟩

/-- The heavy triangle is an actual Mathlib walk in the ambient graph. -/
def cycle : graph.Walk 1 1 :=
  .cons (by decide : graph.Adj 1 2)
    (.cons (by decide : graph.Adj 2 3) (.cons (by decide : graph.Adj 3 1) .nil))

lemma cycle_isCycle : cycle.IsCycle := by
  simp [cycle, SimpleGraph.Walk.isCycle_def, SimpleGraph.Walk.isTrail_def]

def edgeWeight (e : Sym2 V) : ℕ := if e ∈ star.edgeFinset then 1 else 2

def IsCycleMaxEdge (e : Sym2 V) : Prop :=
  e ∈ cycle.edges ∧ ∀ f ∈ cycle.edges, edgeWeight f ≤ edgeWeight e

lemma max12 : IsCycleMaxEdge s(1, 2) := by unfold IsCycleMaxEdge; decide
lemma max23 : IsCycleMaxEdge s(2, 3) := by unfold IsCycleMaxEdge; decide

theorem cycle_max_not_unique : ¬ ∃! e : Sym2 V, IsCycleMaxEdge e := by
  rintro ⟨e, he, hu⟩
  have h := (hu _ max12).trans (hu _ max23).symm
  exact (by decide : (s(1, 2) : Sym2 V) ≠ s(2, 3)) h

/-- Unique MST, but a genuine cycle has several maximum-weight edges. -/
theorem unique_mst_but_cycle_max_not_unique :
    (∃! H : SimpleGraph V, IsMST H) ∧ cycle.IsCycle ∧
      ¬ (∃! e : Sym2 V, IsCycleMaxEdge e) :=
  ⟨unique_mst, cycle_isCycle, cycle_max_not_unique⟩

end ProofCerts.Alg19
