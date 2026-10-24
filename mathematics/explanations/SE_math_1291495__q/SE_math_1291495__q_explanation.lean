import Mathlib

/-!
Explanation census, record SE_math_1291495__q (model-written, no human review).

Source sentence under test (math.stackexchange question 1291495, line 12 of the quoted context):
  "G' is a tree with k-1 edges and k+1 vertices. G has k-1+m edges."
where G is a connected graph on k+1 vertices that contains a cycle, G' is what is left after
deleting m cycle edges, and G' is (correctly) asserted to be a tree.

Documented family  : the sentence fails at EVERY instance (every k, every connected G, every
                     spanning tree G'), both counts being too small by exactly one.
Documented repair  : |E(G')| = k and |E(G)| = k + m.

The released definitions (`graph`, `TreeCount.G`, `TreeCount.H`, the instances, `htree`, `witness`)
are restated verbatim from the released certificate; only the outer namespace is renamed.
The released objects are Mathlib's `SimpleGraph`, `IsTree`, `Connected`, `edgeFinset`, so this
file needs Mathlib; the two-toolchain core check does not apply.
-/
set_option maxRecDepth 10000
set_option maxHeartbeats 4000000

namespace Census_SE_math_1291495__q

/-! ## Released definitions, verbatim -/

def graph (n : ℕ) (es : List (ℕ × ℕ)) : SimpleGraph (Fin n) where
 Adj i j := i ≠ j ∧ ((i.val,j.val) ∈ es ∨ (j.val,i.val) ∈ es)
 symm := by intro i j h; exact ⟨h.1.symm,h.2.symm⟩
 loopless := ⟨fun _ h => h.1 rfl⟩
instance (n : ℕ) (es : List (ℕ × ℕ)) : DecidableRel (graph n es).Adj := fun _ _ => inferInstanceAs (Decidable (_ ∧ _))
namespace TreeCount
def G := graph 3 [(0,1),(0,2),(1,2)]
def H := graph 3 [(0,1),(0,2)]
instance : DecidableRel G.Adj := inferInstanceAs (DecidableRel (graph _ _).Adj)
instance : DecidableRel H.Adj := inferInstanceAs (DecidableRel (graph _ _).Adj)
theorem htree : H.IsTree := by
 rw [SimpleGraph.isTree_iff_connected_and_card]
 constructor
 · decide
 · rw [Nat.card_eq_fintype_card, Nat.card_eq_fintype_card]
   decide
theorem witness : G.Connected ∧ H.IsTree ∧ H ≤ G ∧
    H.edgeFinset.card = 2 ∧ G.edgeFinset.card = 3 ∧
    ¬ H.edgeFinset.card = 1 := ⟨by decide, htree, (by exact (by decide : ∀ i j : Fin 3, H.Adj i j → G.Adj i j)), by decide, by decide, by decide⟩
end TreeCount

/-! ## New definitions (not in the release) -/

open SimpleGraph

/-- `m`, "the number of edges removed": the edges of `G` that are not edges of `G'`. -/
def removed {V : Type} [Fintype V] [DecidableEq V] (G G' : SimpleGraph V)
    [DecidableRel G.Adj] [DecidableRel G'.Adj] : ℕ :=
  (G.edgeFinset \ G'.edgeFinset).card

/-- The source sentence with the edge count of `G'` left as a parameter `c` (an integer, so that
`k - 1` is honest subtraction). The hypotheses are the source's: `G` is connected on `k+1` vertices
and contains a cycle; `G'` is a spanning tree of `G` (the outcome of the cycle-edge removal). -/
def SentenceWith (k : ℕ) (c : ℤ) : Prop :=
  ∀ (V : Type) [Fintype V] [DecidableEq V] (G G' : SimpleGraph V)
    [DecidableRel G.Adj] [DecidableRel G'.Adj],
    Fintype.card V = k + 1 → G.Connected → ¬ G.IsAcyclic → G' ≤ G → G'.IsTree →
      (G'.edgeFinset.card : ℤ) = c ∧ (G.edgeFinset.card : ℤ) = c + (removed G G' : ℤ)

/-- The source sentence as printed: `c = k - 1`. -/
def SourceSentence (k : ℕ) : Prop := SentenceWith k ((k : ℤ) - 1)

/-- The same sentence without the hypothesis that `G` contains a cycle (the dossier's sweep ranges
over all connected graphs, and the family theorem does not need the cycle). -/
def SentenceWithNoCycleHyp (k : ℕ) (c : ℤ) : Prop :=
  ∀ (V : Type) [Fintype V] [DecidableEq V] (G G' : SimpleGraph V)
    [DecidableRel G.Adj] [DecidableRel G'.Adj],
    Fintype.card V = k + 1 → G.Connected → G' ≤ G → G'.IsTree →
      (G'.edgeFinset.card : ℤ) = c ∧ (G.edgeFinset.card : ℤ) = c + (removed G G' : ℤ)

/-! ## Basic counting -/

section Counting
variable {V : Type} [Fintype V] [DecidableEq V] (G G' : SimpleGraph V)
  [DecidableRel G.Adj] [DecidableRel G'.Adj]

/-- `|E(G)| = |E(G')| + m` for a spanning subgraph: pure finite-set counting, no tree needed. -/
theorem card_eq_card_add_removed (hle : G' ≤ G) :
    G.edgeFinset.card = G'.edgeFinset.card + removed G G' := by
  have hsub : G'.edgeFinset ⊆ G.edgeFinset := edgeFinset_subset_edgeFinset.mpr hle
  unfold removed
  rw [Finset.card_sdiff_of_subset hsub]
  have := Finset.card_le_card hsub
  omega

/-- `m = 0` iff nothing was removed (source line 14: "If m=0 then G' = G"). -/
theorem removed_eq_zero_iff (hle : G' ≤ G) : removed G G' = 0 ↔ G' = G := by
  unfold removed
  rw [Finset.card_eq_zero, Finset.sdiff_eq_empty_iff_subset, edgeFinset_subset_edgeFinset]
  exact ⟨fun h => le_antisymm hle h, fun h => h ▸ le_refl _⟩

end Counting

/-! ## (c) The documented repair, universally -/

/-- REPAIR. For every finite vertex type with `k+1` elements, every graph `G` and every spanning
tree `G' ≤ G`: `|E(G')| = k` and `|E(G)| = k + m`. -/
theorem repair {V : Type} [Fintype V] [DecidableEq V] (k : ℕ) (G G' : SimpleGraph V)
    [DecidableRel G.Adj] [DecidableRel G'.Adj]
    (hV : Fintype.card V = k + 1) (hle : G' ≤ G) (hT : G'.IsTree) :
    G'.edgeFinset.card = k ∧ G.edgeFinset.card = k + removed G G' := by
  have h1 : G'.edgeFinset.card = k := by
    have := hT.card_edgeFinset
    omega
  exact ⟨h1, by rw [card_eq_card_add_removed G G' hle, h1]⟩

/-- The repaired sentence in the vocabulary of `SentenceWith`: `c = k` is true at every `k`. -/
theorem repair_sentence (k : ℕ) : SentenceWithNoCycleHyp k (k : ℤ) := by
  intro V _ _ G G' _ _ hV _ hle hT
  obtain ⟨h1, h2⟩ := repair k G G' hV hle hT
  exact ⟨by exact_mod_cast h1, by exact_mod_cast h2⟩

/-! ## (b) The documented family, universally -/

/-- FAMILY (integer reading, no restriction on `k`). At every instance both printed counts are
wrong, and each is too small by exactly one. -/
theorem family {V : Type} [Fintype V] [DecidableEq V] (k : ℕ) (G G' : SimpleGraph V)
    [DecidableRel G.Adj] [DecidableRel G'.Adj]
    (hV : Fintype.card V = k + 1) (hle : G' ≤ G) (hT : G'.IsTree) :
    (G'.edgeFinset.card : ℤ) ≠ (k : ℤ) - 1 ∧
    (G.edgeFinset.card : ℤ) ≠ (k : ℤ) - 1 + (removed G G' : ℤ) ∧
    (G'.edgeFinset.card : ℤ) = ((k : ℤ) - 1) + 1 ∧
    (G.edgeFinset.card : ℤ) = ((k : ℤ) - 1 + (removed G G' : ℤ)) + 1 := by
  obtain ⟨h1, h2⟩ := repair k G G' hV hle hT
  refine ⟨?_, ?_, ?_, ?_⟩ <;> omega

/-- FAMILY (natural-number reading with truncated subtraction): needs `1 ≤ k`, which is the
dossier's own qualifier ("impossible for a tree for every k >= 1"). -/
theorem family_nat {V : Type} [Fintype V] [DecidableEq V] (k : ℕ) (hk : 1 ≤ k)
    (G G' : SimpleGraph V) [DecidableRel G.Adj] [DecidableRel G'.Adj]
    (hV : Fintype.card V = k + 1) (hle : G' ≤ G) (hT : G'.IsTree) :
    G'.edgeFinset.card ≠ k - 1 ∧ G.edgeFinset.card ≠ k - 1 + removed G G' := by
  obtain ⟨h1, h2⟩ := repair k G G' hV hle hT
  constructor <;> omega

/-- The `1 ≤ k` in `family_nat` cannot be dropped: on one vertex (`k = 0`) the tree has `0` edges
and truncated `0 - 1 = 0`. This is an artefact of `ℕ` subtraction, not of the mathematics; the
integer reading `family` has no exception. -/
theorem nat_truncation_at_zero :
    (⊥ : SimpleGraph (Fin 1)).IsTree ∧ (⊥ : SimpleGraph (Fin 1)).edgeFinset.card = 0 - 1 := by
  refine ⟨IsTree.of_subsingleton, ?_⟩
  simp

/-- The source's hypothesis "G contains at least one cycle" forces `k ≥ 2`. -/
theorem cycle_forces_two_le {V : Type} [Fintype V] (k : ℕ) (G : SimpleGraph V)
    (hV : Fintype.card V = k + 1) (hcyc : ¬ G.IsAcyclic) : 2 ≤ k := by
  by_contra hlt
  apply hcyc
  apply IsAcyclic.of_card_le_two
  rw [ENat.card_eq_coe_fintype_card, hV]
  exact_mod_cast (by omega : k + 1 ≤ 2)

/-- The complete graph on `k+1 ≥ 3` vertices is connected and contains a cycle. -/
theorem top_connected_not_acyclic (k : ℕ) (hk : 2 ≤ k) :
    (⊤ : SimpleGraph (Fin (k + 1))).Connected ∧ ¬ (⊤ : SimpleGraph (Fin (k + 1))).IsAcyclic := by
  refine ⟨connected_top, fun hac => ?_⟩
  have hT : (⊤ : SimpleGraph (Fin (k + 1))).IsTree := ⟨connected_top, hac⟩
  have h1 := hT.card_edgeFinset
  rw [card_edgeFinset_top_eq_card_choose_two, Fintype.card_fin] at h1
  have h3 : (k + 1).choose 2 = k.choose 1 + k.choose 2 := Nat.choose_succ_succ' k 1
  rw [Nat.choose_one_right] at h3
  have h2 : k.choose 2 = 0 := by omega
  rw [Nat.choose_eq_zero_iff] at h2
  omega

/-- The family is unbounded and never vacuous: for every `k ≥ 2` there is an instance of the
source's hypotheses on `k+1` vertices, and at every connected graph a spanning tree exists. -/
theorem family_unbounded (k : ℕ) (hk : 2 ≤ k) :
    ∃ G G' : SimpleGraph (Fin (k + 1)),
      G.Connected ∧ ¬ G.IsAcyclic ∧ G' ≤ G ∧ G'.IsTree := by
  obtain ⟨hc, hn⟩ := top_connected_not_acyclic k hk
  obtain ⟨T, hle, hT⟩ := hc.exists_isTree_le
  exact ⟨⊤, T, hc, hn, hle, hT⟩

theorem spanning_tree_exists {V : Type} (G : SimpleGraph V) (hc : G.Connected) :
    ∃ G' ≤ G, G'.IsTree := hc.exists_isTree_le

/-- FAMILY as a statement about the source sentence: it is false for every `k ≥ 2`, i.e. for
every `k` at which the source's hypotheses can be met at all. -/
theorem family_sentence (k : ℕ) (hk : 2 ≤ k) : ¬ SourceSentence k := by
  intro h
  obtain ⟨G, G', hc, hn, hle, hT⟩ := family_unbounded k hk
  classical
  have := (h (Fin (k + 1)) G G' (by simp) hc hn hle hT).1
  exact (family k G G' (by simp) hle hT).1 this

/-- For `k ≤ 1` the source sentence (with its cycle hypothesis) is vacuously true: there is no
connected graph with a cycle on at most two vertices. So `2 ≤ k` in `family_sentence` is sharp. -/
theorem sentence_vacuous_below_two (k : ℕ) (hk : k < 2) (c : ℤ) : SentenceWith k c := by
  intro V _ _ G G' _ _ hV _ hcyc _ _
  have := cycle_forces_two_le k G hV hcyc
  omega

/-- Without the cycle hypothesis the printed sentence is false at EVERY `k`, including 0 and 1. -/
theorem family_sentence_no_cycle_hyp (k : ℕ) : ¬ SentenceWithNoCycleHyp k ((k : ℤ) - 1) := by
  intro h
  have hc : (⊤ : SimpleGraph (Fin (k + 1))).Connected := connected_top
  obtain ⟨T, hle, hT⟩ := hc.exists_isTree_le
  classical
  have := (h (Fin (k + 1)) ⊤ T (by simp) hc hle hT).1
  exact (family k ⊤ T (by simp) hle hT).1 this

/-! ## (a) The refuted local claim, from the released witness -/

/-- The released triangle contains a cycle (the release proves connectedness and the edge count;
the source's cycle hypothesis is derived here). -/
theorem triangle_not_acyclic : ¬ TreeCount.G.IsAcyclic := by
  intro hac
  have hT : TreeCount.G.IsTree := ⟨TreeCount.witness.1, hac⟩
  have h1 := hT.card_edgeFinset
  rw [TreeCount.witness.2.2.2.2.1] at h1
  simp at h1

/-- The released witness has `m = 1`. -/
theorem triangle_removed : removed TreeCount.G TreeCount.H = 1 := by
  have h := card_eq_card_add_removed TreeCount.G TreeCount.H TreeCount.witness.2.2.1
  rw [TreeCount.witness.2.2.2.2.1, TreeCount.witness.2.2.2.1] at h
  omega

/-- CLAIM REFUTED: the source sentence is false at `k = 2`, by the released witness
(triangle `G`, path `H`, `m = 1`): `|E(G')| = 2 ≠ 1` and `|E(G)| = 3 ≠ 1 + 1`. -/
theorem claim_refuted : ¬ SourceSentence 2 := by
  intro h
  have h2 := h (Fin 3) TreeCount.G TreeCount.H (by simp) TreeCount.witness.1
    triangle_not_acyclic TreeCount.witness.2.2.1 TreeCount.witness.2.1
  have := h2.1
  rw [TreeCount.witness.2.2.2.1] at this
  norm_num at this

/-- Both printed counts fail at the released witness (the release certifies only the first). -/
theorem claim_refuted_both :
    (TreeCount.H.edgeFinset.card : ℤ) ≠ (2 : ℤ) - 1 ∧
    (TreeCount.G.edgeFinset.card : ℤ) ≠ (2 : ℤ) - 1 + (removed TreeCount.G TreeCount.H : ℤ) := by
  rw [TreeCount.witness.2.2.2.1, TreeCount.witness.2.2.2.2.1, triangle_removed]
  constructor <;> norm_num

/-! ## (d) Exactness -/

/-- EXACT (per instance): at any instance, a proposed count `c` for `G'` is right iff `c = k`, and
the companion formula `|E(G)| = c + m` is right iff `c = k`. -/
theorem exact_instance {V : Type} [Fintype V] [DecidableEq V] (k : ℕ) (c : ℤ)
    (G G' : SimpleGraph V) [DecidableRel G.Adj] [DecidableRel G'.Adj]
    (hV : Fintype.card V = k + 1) (hle : G' ≤ G) (hT : G'.IsTree) :
    ((G'.edgeFinset.card : ℤ) = c ↔ c = k) ∧
    ((G.edgeFinset.card : ℤ) = c + (removed G G' : ℤ) ↔ c = k) := by
  obtain ⟨h1, h2⟩ := repair k G G' hV hle hT
  constructor <;> constructor <;> intro h <;> omega

/-- EXACT (sentence level, the source's hypotheses, `k ≥ 2`): the sentence "G' is a tree with `c`
edges and `k+1` vertices; G has `c + m` edges" is true iff `c = k`. -/
theorem exact (k : ℕ) (hk : 2 ≤ k) (c : ℤ) : SentenceWith k c ↔ c = k := by
  constructor
  · intro h
    obtain ⟨G, G', hc, hn, hle, hT⟩ := family_unbounded k hk
    classical
    have h1 := (h (Fin (k + 1)) G G' (by simp) hc hn hle hT).1
    exact ((exact_instance k c G G' (by simp) hle hT).1).mp h1
  · rintro rfl
    intro V _ _ G G' _ _ hV hc _ hle hT
    exact repair_sentence k V G G' hV hc hle hT

/-- EXACT (sentence level, no cycle hypothesis, every `k`). -/
theorem exact_no_cycle_hyp (k : ℕ) (c : ℤ) : SentenceWithNoCycleHyp k c ↔ c = k := by
  constructor
  · intro h
    have hc : (⊤ : SimpleGraph (Fin (k + 1))).Connected := connected_top
    obtain ⟨T, hle, hT⟩ := hc.exists_isTree_le
    classical
    have h1 := (h (Fin (k + 1)) ⊤ T (by simp) hc hle hT).1
    exact ((exact_instance k c ⊤ T (by simp) hle hT).1).mp h1
  · rintro rfl
    exact repair_sentence k

/-! ## What the repair buys: it completes the source's own argument -/

/-- Source line 14 ("If m=0 then G' = G and G is a tree") and its converse: `m = 0` iff `G` has
no cycle. -/
theorem removed_eq_zero_iff_acyclic {V : Type} [Fintype V] [DecidableEq V]
    (G G' : SimpleGraph V) [DecidableRel G.Adj] [DecidableRel G'.Adj]
    (hc : G.Connected) (hle : G' ≤ G) (hT : G'.IsTree) :
    removed G G' = 0 ↔ G.IsAcyclic := by
  constructor
  · intro h
    have := (removed_eq_zero_iff G G' hle).mp h
    exact this ▸ hT.isAcyclic
  · intro hac
    have hGT : G.IsTree := ⟨hc, hac⟩
    have h1 := hGT.card_edgeFinset
    have h2 := hT.card_edgeFinset
    have h3 := card_eq_card_add_removed G G' hle
    omega

/-- With the repaired count the source's induction-free argument goes through: a connected graph
on `k+1` vertices with `k` edges has `m = 0`, hence equals its spanning tree, hence is a tree.
(This is the theorem the source set out to prove; Mathlib has it as
`SimpleGraph.isTree_iff_connected_and_card`. Here it is re-derived along the source's route.) -/
theorem source_theorem_via_repair {V : Type} [Fintype V] [DecidableEq V] (k : ℕ)
    (G : SimpleGraph V) [DecidableRel G.Adj]
    (hV : Fintype.card V = k + 1) (hc : G.Connected) (hE : G.edgeFinset.card = k) :
    G.IsTree := by
  obtain ⟨T, hle, hT⟩ := hc.exists_isTree_le
  classical
  obtain ⟨_, h2⟩ := repair k G T hV hle hT
  have hm : removed G T = 0 := by omega
  exact (removed_eq_zero_iff G T hle).mp hm ▸ hT

/-! ## The literal removal process: its outcomes are exactly the spanning trees -/

/-- One step of the source's process: delete one edge of the current graph that lies on a cycle
(equivalently, that is not a bridge). -/
def Step {V : Type} (H H' : SimpleGraph V) : Prop :=
  ∃ e ∈ H.edgeSet, ¬ H.IsBridge e ∧ H' = H.deleteEdges {e}

/-- Running the process from a connected graph keeps a connected spanning subgraph. -/
theorem process_keeps_connected {V : Type} (G H : SimpleGraph V) (hc : G.Connected)
    (hrun : Relation.ReflTransGen Step G H) : H ≤ G ∧ H.Connected := by
  induction hrun with
  | refl => exact ⟨le_refl _, hc⟩
  | tail _ hstep ih =>
    obtain ⟨e, _, hnb, rfl⟩ := hstep
    refine ⟨le_trans (deleteEdges_le _) ih.1, ?_⟩
    induction e using Sym2.ind with
    | _ x y => exact ih.2.connected_delete_edge_of_not_isBridge hnb

/-- Every terminal outcome of the process, started from a connected graph and run in any order,
is a spanning tree of `G`; so `repair` and `family` apply to every outcome under every order. -/
theorem process_outcome_is_spanning_tree {V : Type} (G H : SimpleGraph V) (hc : G.Connected)
    (hrun : Relation.ReflTransGen Step G H) (hstop : ∀ H', ¬ Step H H') :
    H ≤ G ∧ H.IsTree := by
  have key := process_keeps_connected G H hc hrun
  refine ⟨key.1, key.2, ?_⟩
  rw [isAcyclic_iff_forall_edge_isBridge]
  intro e he
  by_contra hnb
  exact hstop _ ⟨e, he, hnb, rfl⟩

/-- A graph without cycles admits no step: every one of its edges is a bridge. -/
theorem acyclic_is_terminal {V : Type} (T : SimpleGraph V) (hT : T.IsAcyclic) :
    ∀ H', ¬ Step T H' := by
  rintro H' ⟨e, he, hnb, -⟩
  exact hnb (isAcyclic_iff_forall_edge_isBridge.mp hT he)

/-- Conversely (finite vertex set): every spanning tree of `G` is reached by some run of the
process, deleting the edges outside the tree one at a time; each of them lies on a cycle of the
current graph because the tree still joins its endpoints. -/
theorem spanning_tree_is_process_outcome {V : Type} [Finite V] (G T : SimpleGraph V)
    (hle : T ≤ G) (hT : T.IsTree) : Relation.ReflTransGen Step G T := by
  generalize hn : (G.edgeSet \ T.edgeSet).ncard = n
  induction n generalizing G with
  | zero =>
    have hfin : (G.edgeSet \ T.edgeSet).Finite := Set.toFinite _
    rw [Set.ncard_eq_zero hfin, Set.diff_eq_empty, edgeSet_subset_edgeSet] at hn
    rw [le_antisymm hle hn]
  | succ n ih =>
    have hne : (G.edgeSet \ T.edgeSet).Nonempty := by
      rw [← Set.ncard_pos (Set.toFinite _)]; omega
    obtain ⟨e, heG, heT⟩ := hne
    have hle1 : T ≤ G.deleteEdges {e} := by
      rw [← edgeSet_subset_edgeSet, edgeSet_deleteEdges]
      intro f hf
      exact ⟨edgeSet_subset_edgeSet.mpr hle hf, fun h => heT (h ▸ hf)⟩
    have hnb : ¬ G.IsBridge e := by
      induction e using Sym2.ind with
      | _ x y =>
        rw [isBridge_iff]
        rintro ⟨-, hnr⟩
        exact hnr ((hT.connected.preconnected x y).mono hle1)
    have hcard : ((G.deleteEdges {e}).edgeSet \ T.edgeSet).ncard = n := by
      have : (G.deleteEdges {e}).edgeSet \ T.edgeSet = (G.edgeSet \ T.edgeSet) \ {e} := by
        rw [edgeSet_deleteEdges]; ext f; simp only [Set.mem_diff, Set.mem_singleton_iff]; tauto
      have hmem : e ∈ G.edgeSet \ T.edgeSet := ⟨heG, heT⟩
      rw [this, Set.ncard_diff_singleton_of_mem hmem, hn]
      rfl
    exact Relation.ReflTransGen.head ⟨e, heG, hnb, rfl⟩ (ih _ hle1 hcard)

/-- The dossier's identification, exactly: for a connected finite graph, the terminal outcomes of
the cycle-edge removal process (over all removal orders) are exactly the spanning trees of `G`,
which are exactly the maximal acyclic spanning subgraphs of `G`. -/
theorem process_outcomes_exact {V : Type} [Finite V] (G H : SimpleGraph V) (hc : G.Connected) :
    ((Relation.ReflTransGen Step G H ∧ ∀ H', ¬ Step H H') ↔ (H ≤ G ∧ H.IsTree)) ∧
    (H ≤ G → (H.IsTree ↔ Maximal (fun F => F ≤ G ∧ F.IsAcyclic) H)) := by
  refine ⟨⟨fun h => process_outcome_is_spanning_tree G H hc h.1 h.2, fun h =>
    ⟨spanning_tree_is_process_outcome G H h.1 h.2, acyclic_is_terminal H h.2.isAcyclic⟩⟩, ?_⟩
  intro hle
  exact (hc.maximal_le_isAcyclic_iff_isTree hle).symm

/-- Hence the repair and the family at every outcome of the process under every removal order. -/
theorem repair_and_family_at_every_process_outcome {V : Type} [Fintype V] [DecidableEq V]
    (k : ℕ) (G H : SimpleGraph V) [DecidableRel G.Adj] [DecidableRel H.Adj]
    (hV : Fintype.card V = k + 1) (hc : G.Connected)
    (hrun : Relation.ReflTransGen Step G H) (hstop : ∀ H', ¬ Step H H') :
    H.edgeFinset.card = k ∧ G.edgeFinset.card = k + removed G H ∧
    (H.edgeFinset.card : ℤ) ≠ (k : ℤ) - 1 ∧
    (G.edgeFinset.card : ℤ) ≠ (k : ℤ) - 1 + (removed G H : ℤ) := by
  obtain ⟨hle, hT⟩ := process_outcome_is_spanning_tree G H hc hrun hstop
  obtain ⟨h1, h2⟩ := repair k G H hV hle hT
  obtain ⟨h3, h4, -, -⟩ := family k G H hV hle hT
  exact ⟨h1, h2, h3, h4⟩

end Census_SE_math_1291495__q

open Census_SE_math_1291495__q in
#print axioms TreeCount.witness
#print axioms Census_SE_math_1291495__q.claim_refuted
#print axioms Census_SE_math_1291495__q.claim_refuted_both
#print axioms Census_SE_math_1291495__q.family
#print axioms Census_SE_math_1291495__q.family_nat
#print axioms Census_SE_math_1291495__q.nat_truncation_at_zero
#print axioms Census_SE_math_1291495__q.cycle_forces_two_le
#print axioms Census_SE_math_1291495__q.family_unbounded
#print axioms Census_SE_math_1291495__q.spanning_tree_exists
#print axioms Census_SE_math_1291495__q.family_sentence
#print axioms Census_SE_math_1291495__q.sentence_vacuous_below_two
#print axioms Census_SE_math_1291495__q.family_sentence_no_cycle_hyp
#print axioms Census_SE_math_1291495__q.card_eq_card_add_removed
#print axioms Census_SE_math_1291495__q.removed_eq_zero_iff
#print axioms Census_SE_math_1291495__q.repair
#print axioms Census_SE_math_1291495__q.repair_sentence
#print axioms Census_SE_math_1291495__q.exact_instance
#print axioms Census_SE_math_1291495__q.exact
#print axioms Census_SE_math_1291495__q.exact_no_cycle_hyp
#print axioms Census_SE_math_1291495__q.removed_eq_zero_iff_acyclic
#print axioms Census_SE_math_1291495__q.source_theorem_via_repair
#print axioms Census_SE_math_1291495__q.process_outcome_is_spanning_tree
#print axioms Census_SE_math_1291495__q.process_keeps_connected
#print axioms Census_SE_math_1291495__q.acyclic_is_terminal
#print axioms Census_SE_math_1291495__q.spanning_tree_is_process_outcome
#print axioms Census_SE_math_1291495__q.process_outcomes_exact
#print axioms Census_SE_math_1291495__q.repair_and_family_at_every_process_outcome
#print axioms Census_SE_math_1291495__q.top_connected_not_acyclic
#print axioms Census_SE_math_1291495__q.triangle_not_acyclic
#print axioms Census_SE_math_1291495__q.triangle_removed
