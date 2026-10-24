/-
Explanation census, record SE_math_782216__q (Stack Exchange, question arm).
Source: "Is my induction proof of the handshake lemma correct? (Graph Theory)".
Quoted claim (base case): "Since there aren't any edge the number of vertices must be equal to 1 or 0."

Released certificate (not modified):
  qedbench_certificate_availability_triage/validation/human_review_20260915/lean/SE_math_782216__q.lean
  selected declaration SE_math_782216_q.mathlib_source_counterexample
The released file is stated over Mathlib's `SimpleGraph`; it is restated verbatim below in a new
namespace, so this file needs Mathlib (compile with `lake env lean` inside the project
`qedbench_certificate_availability_triage/lean_certificates`, read-only).

Model-written; no human review. Forbidden-construct scan: see RECEIPT.json.

Part 1  base case (the quoted claim; the roster's family and repair evidence are about this part):
        claim_refuted, family, family_general, family_complete, repair, repair_connected,
        exact, exact_claim, exact_connected, slack_mathlib_connected.
Part 2  induction step (second paragraph of the dossier's explanation):
        step_pair_iff, step_iff_K2, K2_is_component, step_connected_never,
        P3_refutes_step, P3_connected, P3_isTree, C3_no_degree_one.
-/
import Mathlib

namespace SE_math_782216_q_Census
open SimpleGraph Finset

/-! ## Released theorem, restated verbatim (only the namespace differs) -/

theorem mathlib_source_counterexample :
    (⊥ : SimpleGraph (Fin 2)).IsAcyclic ∧
    (⊥ : SimpleGraph (Fin 2)).edgeFinset.card = 0 ∧
    ¬ Fintype.card (Fin 2) ≤ 1 := by
 exact ⟨SimpleGraph.isAcyclic_bot, by simp, by decide⟩

/-! ## Part 1: the base-case claim -/

/-- The source's base-case sentence at a finite simple graph `G`:
"since there aren't any edges the number of vertices must be 1 or 0". -/
def BaseClaim {V : Type*} [Fintype V] (G : SimpleGraph V) [Fintype G.edgeSet] : Prop :=
  G.edgeFinset.card = 0 → Fintype.card V ≤ 1

/-- (a) The quoted claim, read as the universal statement the source needs, is false.
The refuting instance is the released witness. -/
theorem claim_refuted :
    ¬ ∀ (V : Type) [Fintype V] (G : SimpleGraph V) [Fintype G.edgeSet], BaseClaim G := by
  intro h
  exact mathlib_source_counterexample.2.2 (h (Fin 2) ⊥ mathlib_source_counterexample.2.1)

/-- (b) The documented family, in the shape of the released theorem: for every `k ≥ 2` the edgeless
graph on `k` vertices is acyclic, has 0 edges and more than 1 vertex. `k = 2` is the released
witness. -/
theorem family (k : ℕ) (hk : 2 ≤ k) :
    (⊥ : SimpleGraph (Fin k)).IsAcyclic ∧
    (⊥ : SimpleGraph (Fin k)).edgeFinset.card = 0 ∧
    ¬ Fintype.card (Fin k) ≤ 1 := by
  refine ⟨SimpleGraph.isAcyclic_bot, by simp, ?_⟩
  rw [Fintype.card_fin]; omega

theorem family_instance_is_released_witness :
    family 2 (le_refl 2) = mathlib_source_counterexample := rfl

section
variable {V : Type*} [Fintype V] (G : SimpleGraph V) [Fintype G.edgeSet]

omit [Fintype V] in
theorem edgeless_iff : G.edgeFinset.card = 0 ↔ G = ⊥ := by
  rw [Finset.card_eq_zero, edgeFinset_eq_empty]

/-- The family is ALL the failures: the claim fails at `G` exactly when `G` is the edgeless graph
on at least two vertices. -/
theorem family_complete : ¬ BaseClaim G ↔ (G = ⊥ ∧ 2 ≤ Fintype.card V) := by
  unfold BaseClaim
  rw [edgeless_iff]
  constructor
  · intro h
    by_contra hc
    apply h
    intro hb
    by_contra h1
    exact hc ⟨hb, by omega⟩
  · rintro ⟨hb, h2⟩ h
    have := h hb
    omega

/-- (c) The documented repair: under connectedness the claim holds, for every finite graph.
`Preconnected` = any two vertices are joined by a walk (the null graph qualifies). -/
theorem repair (hc : G.Preconnected) : BaseClaim G := by
  intro he
  have hb : G = ⊥ := (edgeless_iff G).mp he
  rw [hb] at hc
  have := preconnected_bot_iff_subsingleton.mp hc
  exact Fintype.card_le_one_iff_subsingleton.mpr this

/-- The repair under Mathlib's `Connected` (preconnected AND nonempty): the vertex count is then
exactly 1, never 0. -/
theorem repair_connected (hc : G.Connected) (he : G.edgeFinset.card = 0) :
    Fintype.card V = 1 := by
  have h1 := repair G hc.preconnected he
  have := hc.nonempty
  have h2 : 0 < Fintype.card V := Fintype.card_pos
  omega

/-- (d) Exactness: among zero-edge graphs, "at most one vertex" is EQUIVALENT to preconnectedness.
This is the formal content of the dossier's "it is true only under an unstated connectedness
assumption". -/
theorem exact (he : G.edgeFinset.card = 0) :
    Fintype.card V ≤ 1 ↔ G.Preconnected := by
  constructor
  · intro h
    have := Fintype.card_le_one_iff_subsingleton.mp h
    exact Preconnected.of_subsingleton
  · intro hc
    exact repair G hc he

/-- Exactness at the level of the claim itself. -/
theorem exact_claim : BaseClaim G ↔ (G.edgeFinset.card = 0 → G.Preconnected) := by
  constructor
  · intro h he
    exact (exact G he).mp (h he)
  · intro h he
    exact (exact G he).mpr (h he)

/-- Exactness under Mathlib's `Connected`: the null graph has to be added by hand. -/
theorem exact_connected (he : G.edgeFinset.card = 0) :
    Fintype.card V ≤ 1 ↔ (G.Connected ∨ IsEmpty V) := by
  rw [exact G he]
  constructor
  · intro hp
    rcases isEmpty_or_nonempty V with h | h
    · exact Or.inr h
    · exact Or.inl ⟨hp⟩
  · rintro (h | h)
    · exact h.preconnected
    · intro u; exact (h.false u).elim

end

/-- The family over an arbitrary finite vertex type. -/
theorem family_general {V : Type*} [Fintype V] [Fintype (⊥ : SimpleGraph V).edgeSet]
    (h : 2 ≤ Fintype.card V) : ¬ BaseClaim (⊥ : SimpleGraph V) :=
  (family_complete ⊥).mpr ⟨rfl, h⟩

/-- Slack under the convention that a connected graph is nonempty (Mathlib's `Connected`): the null
graph has 0 edges and satisfies the claim's conclusion (its "or 0" case) but is not `Connected`.
So "true ONLY under connectedness" is false under that convention. -/
theorem slack_mathlib_connected :
    (⊥ : SimpleGraph (Fin 0)).edgeFinset.card = 0 ∧
    Fintype.card (Fin 0) ≤ 1 ∧
    (⊥ : SimpleGraph (Fin 0)).Preconnected ∧
    ¬ (⊥ : SimpleGraph (Fin 0)).Connected := by
  refine ⟨by simp, by simp, fun u => u.elim0, fun h => ?_⟩
  obtain ⟨x⟩ := h.nonempty
  exact x.elim0

/-- "the script verifies the witness is disconnected". -/
theorem witness_disconnected : ¬ (⊥ : SimpleGraph (Fin 2)).Preconnected :=
  not_preconnected_bot

/-- Every member of the family is disconnected. -/
theorem family_disconnected (k : ℕ) (hk : 2 ≤ k) : ¬ (⊥ : SimpleGraph (Fin k)).Preconnected := by
  rw [preconnected_bot_iff_subsingleton]
  intro h
  have := Fintype.card_le_one_iff_subsingleton.mpr h
  rw [Fintype.card_fin] at this; omega

section
variable {V : Type*} [Fintype V] (G : SimpleGraph V) [DecidableRel G.Adj]

/-- What the source's base case actually needs: `P(0)` holds for EVERY edgeless graph, with no
statement about the number of vertices (and no connectedness). -/
theorem base_case_needs_no_vertex_count (he : G.edgeFinset.card = 0) :
    ∑ v, G.degree v = 0 := by
  rw [sum_degrees_eq_twice_card_edges, he]

/-- The ambient theorem (handshake lemma) is true; only the local sentence is refuted. -/
theorem ambient_handshake : ∑ v, G.degree v = 2 * G.edgeFinset.card :=
  sum_degrees_eq_twice_card_edges G

end

/-! ## Part 2: the induction step, as the dossier formalises it

"G with e ≥ 1 edges has two degree-1 vertices u, v with |E(G − u − v)| = e − 1".
`G − u − v` is modelled on the same vertex type by deleting every edge at `u` and then every edge
at `v`; `edgesAfterDeleting_eq_induce` certifies that this is the edge count of the induced
subgraph on the complement of `{u, v}`. `x = e − 1` is written `x + 1 = e` (equivalent for `e ≥ 1`,
and free of truncated subtraction). -/

section Step
variable {V : Type*} [Fintype V] [DecidableEq V] (G : SimpleGraph V) [DecidableRel G.Adj]

def edgesAfterDeleting (u v : V) : ℕ :=
  #((G.deleteIncidenceSet u).deleteIncidenceSet v).edgeFinset

theorem card_edgeFinset_congr {W : Type*} {G₁ G₂ : SimpleGraph W} [Fintype G₁.edgeSet]
    [Fintype G₂.edgeSet] (h : G₁ = G₂) : #G₁.edgeFinset = #G₂.edgeFinset := by
  rw [edgeFinset_card, edgeFinset_card]
  exact Fintype.card_congr (Equiv.setCongr (by rw [h]))

theorem edgesAfterDeleting_eq_induce (u v : V) :
    #(G.induce ({u, v}ᶜ : Set V)).edgeFinset = edgesAfterDeleting G u v := by
  unfold edgesAfterDeleting
  have hsupp : ((G.deleteIncidenceSet u).deleteIncidenceSet v).support ⊆ ({u, v}ᶜ : Set V) := by
    intro w hw
    obtain ⟨x, hx⟩ := hw
    have hx' : ((G.deleteIncidenceSet u).deleteIncidenceSet v).Adj w x := hx
    rw [deleteIncidenceSet_adj, deleteIncidenceSet_adj] at hx'
    simp only [Set.mem_compl_iff, Set.mem_insert_iff, Set.mem_singleton_iff, not_or]
    exact ⟨hx'.1.2.1, hx'.2.1⟩
  rw [← card_edgeFinset_induce_of_support_subset hsupp]
  apply card_edgeFinset_congr
  ext a b
  simp only [comap_adj, Function.Embedding.coe_subtype, deleteIncidenceSet_adj]
  have ha := a.prop
  have hb := b.prop
  simp only [Set.mem_compl_iff, Set.mem_insert_iff, Set.mem_singleton_iff, not_or] at ha hb
  tauto

/-- The conclusion of the step claim at `G`. -/
def StepHolds : Prop :=
  ∃ u v, u ≠ v ∧ G.degree u = 1 ∧ G.degree v = 1 ∧
    edgesAfterDeleting G u v + 1 = #G.edgeFinset

/-- The step claim at `G`, exactly as the dossier's witness field formalises it. -/
def StepClaim : Prop := 1 ≤ #G.edgeFinset → StepHolds G

variable {G}

omit [DecidableEq V] in
theorem unique_nbr {u v w : V} (h : G.degree u = 1) (hv : G.Adj u v) (hw : G.Adj u w) : w = v := by
  obtain ⟨x, _, hux⟩ := degree_eq_one_iff_existsUnique_adj.mp h
  exact (hux w hw).trans (hux v hv).symm

theorem degree_after_adj {u v : V} (hv : G.degree v = 1) (hadj : G.Adj u v) :
    (G.deleteIncidenceSet u).degree v = 0 := by
  rw [← card_neighborFinset_eq_degree, Finset.card_eq_zero]
  ext w
  simp only [mem_neighborFinset, deleteIncidenceSet_adj, Finset.notMem_empty, iff_false]
  rintro ⟨h1, _, h3⟩
  exact h3 (unique_nbr hv hadj.symm h1)

theorem degree_after_not_adj {u v : V} (huv : u ≠ v) (hv : G.degree v = 1) (hadj : ¬ G.Adj u v) :
    (G.deleteIncidenceSet u).degree v = 1 := by
  rw [← hv, ← card_neighborFinset_eq_degree, ← card_neighborFinset_eq_degree]
  congr 1
  ext w
  simp only [mem_neighborFinset, deleteIncidenceSet_adj]
  constructor
  · exact fun h => h.1
  · intro h
    refine ⟨h, huv.symm, ?_⟩
    rintro rfl
    exact hadj h.symm

/-- For two distinct degree-1 vertices, deleting both loses exactly one edge IFF they are adjacent. -/
theorem step_pair_iff {u v : V} (huv : u ≠ v) (hu : G.degree u = 1) (hv : G.degree v = 1) :
    edgesAfterDeleting G u v + 1 = #G.edgeFinset ↔ G.Adj u v := by
  unfold edgesAfterDeleting
  rw [card_edgeFinset_deleteIncidenceSet, card_edgeFinset_deleteIncidenceSet, hu]
  have hE : 1 ≤ #G.edgeFinset := hu ▸ G.degree_le_card_edgeFinset u
  by_cases hadj : G.Adj u v
  · rw [degree_after_adj hv hadj]
    simp only [hadj, iff_true]
    omega
  · have h1 := degree_after_not_adj huv hv hadj
    have h2 := (G.deleteIncidenceSet u).degree_le_card_edgeFinset v
    rw [h1, card_edgeFinset_deleteIncidenceSet, hu] at h2
    rw [h1]
    simp only [hadj, iff_false]
    omega

/-- "in which case they add 1 edge". -/
theorem deleting_adjacent_leaves_removes_one {u v : V} (hu : G.degree u = 1) (hv : G.degree v = 1)
    (hadj : G.Adj u v) : edgesAfterDeleting G u v + 1 = #G.edgeFinset :=
  (step_pair_iff hadj.ne hu hv).mpr hadj

/-- "adds exactly 2 edges unless the two new vertices are joined to each other". -/
theorem deleting_nonadjacent_leaves_removes_two {u v : V} (huv : u ≠ v) (hu : G.degree u = 1)
    (hv : G.degree v = 1) (hadj : ¬ G.Adj u v) : edgesAfterDeleting G u v + 2 = #G.edgeFinset := by
  unfold edgesAfterDeleting
  rw [card_edgeFinset_deleteIncidenceSet, card_edgeFinset_deleteIncidenceSet, hu]
  have h1 := degree_after_not_adj huv hv hadj
  have h2 := (G.deleteIncidenceSet u).degree_le_card_edgeFinset v
  rw [h1, card_edgeFinset_deleteIncidenceSet, hu] at h2
  rw [h1]
  omega

/-- The dossier's "only if G has a K2 connected component" is in fact an IFF:
the step conclusion holds at `G` exactly when `G` has two adjacent vertices of degree 1. -/
theorem step_iff_K2 :
    StepHolds G ↔ ∃ u v, G.Adj u v ∧ G.degree u = 1 ∧ G.degree v = 1 := by
  constructor
  · rintro ⟨u, v, huv, hu, hv, h⟩
    exact ⟨u, v, (step_pair_iff huv hu hv).mp h, hu, hv⟩
  · rintro ⟨u, v, hadj, hu, hv⟩
    exact ⟨u, v, hadj.ne, hu, hv, (step_pair_iff hadj.ne hu hv).mpr hadj⟩

omit [DecidableEq V] in
/-- Two adjacent degree-1 vertices form a connected component: nothing else is reachable. -/
theorem K2_is_component {u v : V} (hadj : G.Adj u v) (hu : G.degree u = 1) (hv : G.degree v = 1)
    (w : V) (hw : G.Reachable u w) : w = u ∨ w = v := by
  rw [reachable_iff_reflTransGen] at hw
  induction hw with
  | refl => exact Or.inl rfl
  | tail _ hbc ih =>
    rcases ih with rfl | rfl
    · exact Or.inr (unique_nbr hu hadj hbc)
    · exact Or.inl (unique_nbr hv hadj.symm hbc)

/-- "a connected G with e ≥ 2 edges never can". -/
theorem step_connected_never (hc : G.Connected) (he : 2 ≤ #G.edgeFinset) : ¬ StepHolds G := by
  rw [step_iff_K2]
  rintro ⟨u, v, hadj, hu, hv⟩
  have hall : ∀ w, w = u ∨ w = v := fun w => K2_is_component hadj hu hv w (hc.preconnected u w)
  have hsub : G.edgeFinset ⊆ {s(u, v)} := by
    intro e he'
    induction e using Sym2.ind with
    | _ a b =>
      rw [mem_edgeFinset, mem_edgeSet] at he'
      have hne := he'.ne
      rw [Finset.mem_singleton]
      rcases hall a with ha | ha <;> rcases hall b with hb | hb
      · exact absurd (ha.trans hb.symm) hne
      · rw [ha, hb]
      · rw [ha, hb]; exact Sym2.eq_swap
      · exact absurd (ha.trans hb.symm) hne
  have := Finset.card_le_card hsub
  rw [Finset.card_singleton] at this
  omega

/-- The step claim fails at EVERY connected graph with at least two edges
(the family for the induction step). -/
theorem step_family (hc : G.Connected) (he : 2 ≤ #G.edgeFinset) : ¬ StepClaim G :=
  fun h => step_connected_never hc he (h (by omega))

end Step

/-- The dossier's P3: vertices 0, 1, 2 and edges 01, 02. -/
def P3 : SimpleGraph (Fin 3) where
  Adj a b := (a = 0 ∧ b ≠ 0) ∨ (a ≠ 0 ∧ b = 0)

instance : DecidableRel P3.Adj := fun a b => by unfold P3; infer_instance

theorem P3_data : #P3.edgeFinset = 2 ∧ P3.degree 0 = 2 ∧ P3.degree 1 = 1 ∧ P3.degree 2 = 1 := by
  decide

theorem P3_edges : P3.Adj 0 1 ∧ P3.Adj 0 2 ∧ ¬ P3.Adj 1 2 := by decide

theorem P3_refutes_step : ¬ StepClaim P3 := by
  intro h
  have h1 : 1 ≤ #P3.edgeFinset := by rw [P3_data.1]; omega
  have := (step_iff_K2).mp (h h1)
  revert this
  decide

theorem P3_connected : P3.Connected := by
  rw [connected_iff_exists_forall_reachable]
  refine ⟨0, fun w => ?_⟩
  by_cases hw : w = 0
  · rw [hw]
  · exact (show P3.Adj 0 w from Or.inl ⟨rfl, hw⟩).reachable

/-- P3 is a member of the step family (second, independent proof of `P3_refutes_step`). -/
theorem P3_in_step_family : ¬ StepClaim P3 :=
  step_family P3_connected (by rw [P3_data.1])

theorem P3_isTree : P3.IsTree := by
  rw [isTree_iff_connected_and_card]
  refine ⟨P3_connected, ?_⟩
  rw [Nat.card_eq_fintype_card, Nat.card_eq_fintype_card, ← edgeFinset_card, P3_data.1,
    Fintype.card_fin]

/-- The triangle: 3 edges, connected, and no vertex of degree 1 (readings B2 and B3 fail). -/
theorem C3_data : #(⊤ : SimpleGraph (Fin 3)).edgeFinset = 3 ∧ (⊤ : SimpleGraph (Fin 3)).Connected := by
  refine ⟨by decide, ?_⟩
  exact connected_top

theorem C3_no_degree_one : ∀ v : Fin 3, (⊤ : SimpleGraph (Fin 3)).degree v ≠ 1 := by
  intro v
  rw [complete_graph_degree]
  simp

end SE_math_782216_q_Census

#print axioms SE_math_782216_q_Census.mathlib_source_counterexample
#print axioms SE_math_782216_q_Census.claim_refuted
#print axioms SE_math_782216_q_Census.family
#print axioms SE_math_782216_q_Census.family_general
#print axioms SE_math_782216_q_Census.family_complete
#print axioms SE_math_782216_q_Census.repair
#print axioms SE_math_782216_q_Census.repair_connected
#print axioms SE_math_782216_q_Census.exact
#print axioms SE_math_782216_q_Census.exact_claim
#print axioms SE_math_782216_q_Census.exact_connected
#print axioms SE_math_782216_q_Census.slack_mathlib_connected
#print axioms SE_math_782216_q_Census.witness_disconnected
#print axioms SE_math_782216_q_Census.family_disconnected
#print axioms SE_math_782216_q_Census.base_case_needs_no_vertex_count
#print axioms SE_math_782216_q_Census.ambient_handshake
#print axioms SE_math_782216_q_Census.edgesAfterDeleting_eq_induce
#print axioms SE_math_782216_q_Census.step_pair_iff
#print axioms SE_math_782216_q_Census.deleting_adjacent_leaves_removes_one
#print axioms SE_math_782216_q_Census.deleting_nonadjacent_leaves_removes_two
#print axioms SE_math_782216_q_Census.step_iff_K2
#print axioms SE_math_782216_q_Census.K2_is_component
#print axioms SE_math_782216_q_Census.step_connected_never
#print axioms SE_math_782216_q_Census.step_family
#print axioms SE_math_782216_q_Census.P3_data
#print axioms SE_math_782216_q_Census.P3_edges
#print axioms SE_math_782216_q_Census.P3_refutes_step
#print axioms SE_math_782216_q_Census.P3_in_step_family
#print axioms SE_math_782216_q_Census.P3_connected
#print axioms SE_math_782216_q_Census.P3_isTree
#print axioms SE_math_782216_q_Census.C3_data
#print axioms SE_math_782216_q_Census.C3_no_degree_one
