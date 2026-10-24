import Mathlib

/- Explanation census, record SE_math_1868681__q (model-written; no human review).
The released definitions and the released witness are restated verbatim below
(text from `def graph` to `end OddBipartite`), inside a new namespace.  Everything after the
line `-- CENSUS ADDITIONS` is new.  Mathlib is used because the released certificate states its
witness over Mathlib's `SimpleGraph`. -/
set_option maxRecDepth 10000
set_option maxHeartbeats 4000000

namespace Census_SE_math_1868681__q
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
namespace OddBipartite
abbrev G := TreeCount.H
instance : DecidableRel G.Adj := inferInstanceAs (DecidableRel (graph _ _).Adj)
theorem witness : G.edgeFinset.card = 2 ∧
    (∀ i j : Fin 3, G.Adj i j → (i = 0) ≠ (j = 0)) ∧
    (G.edgeFinset.card : ℚ) ≠ (3:ℚ)^2/4 ∧
    (∀ m : ℕ, (m : ℚ) ≠ (3:ℚ)^2/4) := by
 refine ⟨by decide, by decide, ?_, ?_⟩
 · have hc : G.edgeFinset.card = 2 := by decide
   norm_num [hc]
 · intro m hm
   have h : (m : ℚ) * 4 = 9 := by linarith
   have hnat : m * 4 = 9 := by exact_mod_cast h
   omega
end OddBipartite

-- CENSUS ADDITIONS

open SimpleGraph

/-! ## Objects of the source sentence -/

/-- Number of edges of a simple graph, free of decidability instances. -/
noncomputable def edges {V : Type*} (G : SimpleGraph V) : ℕ := G.edgeSet.ncard

/-- `edges` is the released certificate's `edgeFinset.card`. -/
theorem edges_eq_card_edgeFinset {V : Type*} (G : SimpleGraph V) [Fintype G.edgeSet] :
    edges G = G.edgeFinset.card := by
  unfold edges
  rw [Set.ncard_eq_toFinset_card']
  rfl

/-- The edge counts of the bipartite (2-colourable, Mathlib `IsBipartite`) simple graphs on
`p` labelled vertices.  Colour classes may be empty. -/
def BipCounts (p : ℕ) : Set ℕ :=
  {m | ∃ G : SimpleGraph (Fin p), G.IsBipartite ∧ edges G = m}

/-- The source sentence at `p`: "the greatest number of edges on a bipartite graph on p
[vertices] is p^2/4", as an exact statement in the rationals (no floor). -/
def SourceClaim (p : ℕ) : Prop :=
  IsGreatest ((fun m : ℕ => (m : ℚ)) '' BipCounts p) ((p : ℚ) ^ 2 / 4)

/-- The repaired sentence at `p`: the greatest number of edges is `⌊p^2/4⌋`
(natural-number division). -/
def RepairedClaim (p : ℕ) : Prop := IsGreatest (BipCounts p) (p ^ 2 / 4)

/-! ## (a) The claim is refuted at the released witness -/

/-- The released graph is bipartite in Mathlib's sense (from the released second conjunct). -/
theorem released_bipartite : OddBipartite.G.IsBipartite := by
  refine ⟨SimpleGraph.Coloring.mk (fun i : Fin 3 => if i = 0 then (0 : Fin 2) else 1) ?_⟩
  intro i j hij
  have h := OddBipartite.witness.2.1 i j hij
  by_cases hi : i = 0 <;> by_cases hj : j = 0 <;> simp_all

/-- The released graph contributes the edge count 2 to `BipCounts 3`. -/
theorem released_count : 2 ∈ BipCounts 3 :=
  ⟨OddBipartite.G, released_bipartite, by
    rw [edges_eq_card_edgeFinset]; exact OddBipartite.witness.1⟩

/-- The source sentence is false at p = 3, using only the released witness's last conjunct. -/
theorem claim_refuted : ¬ SourceClaim 3 := by
  rintro ⟨⟨m, _, hm⟩, _⟩
  exact OddBipartite.witness.2.2.2 m (by simpa using hm)

/-! ## (b) The documented family: every odd p -/

/-- "For odd p, p^2/4 is not an integer": no natural number equals p^2/4. -/
theorem family_arith (p : ℕ) (hp : Odd p) (m : ℕ) : (m : ℚ) ≠ (p : ℚ) ^ 2 / 4 := by
  intro hm
  have h : (m : ℚ) * 4 = (p : ℚ) ^ 2 := by rw [hm]; ring
  have hnat : m * 4 = p ^ 2 := by exact_mod_cast h
  obtain ⟨k, rfl⟩ := hp
  have h2 : (2 * k + 1) ^ 2 = 4 * (k * k + k) + 1 := by ring
  omega

/-- "so the edge count (an integer) can never equal it": no simple graph at all on any vertex
type, bipartite or not, has p^2/4 edges when p is odd. -/
theorem family_no_graph (p : ℕ) (hp : Odd p) {V : Type*} (G : SimpleGraph V) :
    (edges G : ℚ) ≠ (p : ℚ) ^ 2 / 4 := family_arith p hp (edges G)

/-- "the claim is false for every odd p". -/
theorem family (p : ℕ) (hp : Odd p) : ¬ SourceClaim p := by
  rintro ⟨⟨m, _, hm⟩, _⟩
  exact family_arith p hp m hm

/-- The family is unbounded: above every bound there is a p at which the claim fails. -/
theorem family_unbounded (N : ℕ) : ∃ p, N ≤ p ∧ ¬ SourceClaim p :=
  ⟨2 * N + 1, by omega, family _ ⟨N, rfl⟩⟩

/-! ## (c) The documented repair -/

/-- "at most a(p-a) edges", set form: a graph bipartite with parts `s`, `t` has at most
`|s| * |t|` edges (Mathlib `IsBipartiteWith.encard_edgeSet_le`, brought down to ℕ). -/
theorem repair_parts {V : Type*} [Finite V] {G : SimpleGraph V} {s t : Set V}
    (h : G.IsBipartiteWith s t) : edges G ≤ s.ncard * t.ncard := by
  have h1 := h.encard_edgeSet_le
  rw [← (Set.toFinite G.edgeSet).cast_ncard_eq, ← s.toFinite.cast_ncard_eq,
    ← t.toFinite.cast_ncard_eq] at h1
  unfold edges
  exact_mod_cast h1

/-- "Any bipartite graph on p vertices has its vertex set split into colour classes of sizes a
and p-a ... and has at most a(p-a) edges": for EVERY proper 2-colouring `c`, with `a` the size
of the colour class 0. -/
theorem repair_colouring {V : Type*} [Fintype V] {G : SimpleGraph V} (c : G.Coloring (Fin 2)) :
    edges G ≤ {v | c v = 0}.ncard * (Fintype.card V - {v | c v = 0}.ncard) := by
  have hb : G.IsBipartiteWith {v | c v = 0} {v | c v = 0}ᶜ := by
    refine ⟨disjoint_compl_right, fun v w hvw => ?_⟩
    have hne : c v ≠ c w := c.valid hvw
    have key : ∀ a b : Fin 2, a ≠ b → (a = 0 ∧ b ≠ 0) ∨ (a ≠ 0 ∧ b = 0) := by decide
    simpa using key _ _ hne
  have h1 := repair_parts hb
  have h2 := Set.ncard_add_ncard_compl {v | c v = 0}
  rw [Nat.card_eq_fintype_card] at h2
  have h3 : ({v | c v = 0}ᶜ : Set V).ncard = Fintype.card V - {v | c v = 0}.ncard := by omega
  rwa [h3] at h1

/-- The dossier's K_{a,p-a} on given colour classes: the complete bipartite graph with parts
`s` and its complement, as a graph on the same vertex set. -/
def Kparts {V : Type*} (s : Set V) : SimpleGraph V := (⊤ : SimpleGraph V).between s sᶜ

/-- "so it is a subgraph of K_{a,p-a}": for every proper 2-colouring, G is a spanning subgraph
of the complete bipartite graph on its colour classes. -/
theorem repair_subgraph {V : Type*} {G : SimpleGraph V} (c : G.Coloring (Fin 2)) :
    G ≤ Kparts {v | c v = 0} := by
  intro v w h
  have hne : c v ≠ c w := c.valid h
  have key : ∀ a b : Fin 2, a ≠ b → (a = 0 ∧ b ≠ 0) ∨ (a ≠ 0 ∧ b = 0) := by decide
  refine between_adj.mpr ⟨h.ne, ?_⟩
  simpa using key _ _ hne

/-- K_{a,p-a} on parts `s` and `sᶜ` has exactly a(p-a) edges, a = |s|. -/
theorem edges_Kparts {V : Type*} [Fintype V] (s : Set V) :
    edges (Kparts s) = s.ncard * (Fintype.card V - s.ncard) := by
  have h2 := Set.ncard_add_ncard_compl s
  rw [Nat.card_eq_fintype_card] at h2
  have h3 : Fintype.card V - s.ncard = sᶜ.ncard := by omega
  rw [h3]
  apply le_antisymm
  · exact repair_parts (between_isBipartiteWith disjoint_compl_right)
  · unfold edges
    rw [← Nat.card_coe_set_eq, ← Nat.card_coe_set_eq, ← Nat.card_coe_set_eq, ← Nat.card_prod]
    let f : s × (sᶜ : Set V) → (Kparts s).edgeSet := fun x =>
      ⟨s(x.1.1, x.2.1), by
        rw [mem_edgeSet]
        exact between_adj.mpr ⟨fun h => x.2.2 (h ▸ x.1.2), Or.inl ⟨x.1.2, x.2.2⟩⟩⟩
    apply Nat.card_le_card_of_injective f
    rintro ⟨⟨x, hx⟩, ⟨y, hy⟩⟩ ⟨⟨x', hx'⟩, ⟨y', hy'⟩⟩ h
    have h' : s(x, y) = s(x', y') := congrArg Subtype.val h
    rcases Sym2.eq_iff.mp h' with ⟨rfl, rfl⟩ | ⟨rfl, rfl⟩
    · rfl
    · exact absurd hx hy'

/-- "the maximum over a is floor(p^2/4)", upper half: a(p-a) ≤ ⌊p^2/4⌋ for every a
(truncated subtraction; for a > p the left side is 0). -/
theorem classes_le_floor (p a : ℕ) : a * (p - a) ≤ p ^ 2 / 4 := by
  rw [Nat.le_div_iff_mul_le (by norm_num)]
  rcases le_total a p with h | h
  · obtain ⟨b, rfl⟩ := Nat.exists_eq_add_of_le h
    rw [Nat.add_sub_cancel_left]
    have := four_mul_le_sq_add a b
    nlinarith
  · simp [Nat.sub_eq_zero_of_le h]

/-- "the maximum over a is floor(p^2/4)", attained half: a = ⌊p/2⌋. -/
theorem classes_attained (p : ℕ) : (p / 2) * (p - p / 2) = p ^ 2 / 4 := by
  rcases Nat.even_or_odd' p with ⟨k, rfl | rfl⟩
  · have h1 : 2 * k / 2 = k := by omega
    have h2 : (2 * k) ^ 2 = 4 * (k * k) := by ring
    rw [h1, h2, Nat.mul_div_cancel_left _ (by norm_num : 0 < 4)]
    congr 1; omega
  · have h1 : (2 * k + 1) / 2 = k := by omega
    have h2 : (2 * k + 1) ^ 2 = 4 * (k * (k + 1)) + 1 := by ring
    have h3 : 2 * k + 1 - k = k + 1 := by omega
    rw [h1, h2, h3]
    omega

/-- The maximum over a of a(p-a), as a greatest element. -/
theorem classes_isGreatest (p : ℕ) :
    IsGreatest {n | ∃ a, a ≤ p ∧ n = a * (p - a)} (p ^ 2 / 4) :=
  ⟨⟨p / 2, Nat.div_le_self p 2, (classes_attained p).symm⟩,
    fun _ ⟨a, _, hn⟩ => hn ▸ classes_le_floor p a⟩

/-- Repair, upper bound, any finite vertex type: a bipartite graph on p vertices has at most
⌊p^2/4⌋ edges.  Proved along the dossier's route (colour classes, then the maximum over a). -/
theorem repair_upper {V : Type*} [Fintype V] {G : SimpleGraph V} (h : G.IsBipartite) :
    edges G ≤ Fintype.card V ^ 2 / 4 := by
  obtain ⟨c⟩ := h
  exact (repair_colouring c).trans (classes_le_floor _ _)

/-- Transport of a graph along a bijection of vertex types keeps the edge count. -/
theorem edges_map_equiv {W V : Type*} (e : W ≃ V) (H : SimpleGraph W) :
    edges (H.map e.toEmbedding) = edges H := by
  unfold edges
  rw [← Nat.card_coe_set_eq, ← Nat.card_coe_set_eq]
  exact (Nat.card_congr (SimpleGraph.Iso.map e H).mapEdgeSet).symm

/-- K_{a,b} has exactly a*b edges (Mathlib `encard_edgeSet_completeBipartiteGraph`). -/
theorem edges_completeBipartite (a b : ℕ) :
    edges (completeBipartiteGraph (Fin a) (Fin b)) = a * b := by
  have h := encard_edgeSet_completeBipartiteGraph (W₁ := Fin a) (W₂ := Fin b)
  rw [← (Set.toFinite _).cast_ncard_eq, ENat.card_eq_coe_fintype_card,
    ENat.card_eq_coe_fintype_card, Fintype.card_fin, Fintype.card_fin] at h
  unfold edges
  exact_mod_cast h

/-- Every a(p-a) with a ≤ p is the edge count of a bipartite graph on Fin p: the dossier's
K_{a,p-a}, relabelled onto Fin p. -/
theorem complete_bipartite_count (p a : ℕ) (ha : a ≤ p) : a * (p - a) ∈ BipCounts p := by
  have hp : a + (p - a) = p := by omega
  let e : Fin a ⊕ Fin (p - a) ≃ Fin p := finSumFinEquiv.trans (finCongr hp)
  refine ⟨(completeBipartiteGraph (Fin a) (Fin (p - a))).map e.toEmbedding, ?_, ?_⟩
  · have hc : (completeBipartiteGraph (Fin a) (Fin (p - a))).Colorable 2 := by
      simpa using (CompleteBipartiteGraph.bicoloring (Fin a) (Fin (p - a))).colorable
    exact hc.of_hom (SimpleGraph.Iso.map e _).symm.toHom
  · rw [edges_map_equiv, edges_completeBipartite]

/-- The documented repair: the greatest number of edges of a bipartite graph on p vertices is
⌊p^2/4⌋, for every p (including p = 0 and p = 1). -/
theorem repair (p : ℕ) : RepairedClaim p := by
  refine ⟨?_, ?_⟩
  · have h := complete_bipartite_count p (p / 2) (Nat.div_le_self p 2)
    rwa [classes_attained] at h
  · rintro m ⟨G, hG, rfl⟩
    simpa using repair_upper hG

/-- Variant reading of "bipartite" (both groups M, N non-empty, M ∪ N = V, as the source's
rectangle picture suggests): for p ≥ 2 the maximum ⌊p^2/4⌋ is still attained, so the repair is
the same under that reading; for p < 2 no such bipartition exists. -/
theorem repair_attained_nonempty_parts (p : ℕ) (hp : 2 ≤ p) :
    ∃ (G : SimpleGraph (Fin p)) (M N : Set (Fin p)), M.Nonempty ∧ N.Nonempty ∧
      M ∪ N = Set.univ ∧ G.IsBipartiteWith M N ∧ edges G = p ^ 2 / 4 := by
  let M : Set (Fin p) := {i | (i : ℕ) < p / 2}
  have hM : M.ncard = p / 2 := by
    rw [Set.ncard_eq_toFinset_card', Set.toFinset_setOf, Fin.card_filter_val_lt]
    omega
  refine ⟨Kparts M, M, Mᶜ, ⟨⟨0, by omega⟩, ?_⟩, ⟨⟨p - 1, by omega⟩, ?_⟩,
    Set.union_compl_self M, between_isBipartiteWith disjoint_compl_right, ?_⟩
  · show (0 : ℕ) < p / 2
    omega
  · show ¬ ((p - 1 : ℕ) < p / 2)
    omega
  · rw [edges_Kparts, hM, Fintype.card_fin, classes_attained]

/-- For p < 2 there is no bipartition of Fin p into two non-empty groups. -/
theorem no_nonempty_parts_below_two (p : ℕ) (hp : p < 2) (M N : Set (Fin p))
    (hM : M.Nonempty) (hN : N.Nonempty) : ¬ Disjoint M N := by
  obtain ⟨x, hx⟩ := hM
  obtain ⟨y, hy⟩ := hN
  have hxy : x = y := by
    apply Fin.ext
    have := x.isLt
    have := y.isLt
    omega
  subst hxy
  exact fun h => Set.disjoint_left.mp h hx hy

/-- "which equals p^2/4 only when p is even" (both directions). -/
theorem floor_eq_iff_even (p : ℕ) : ((p ^ 2 / 4 : ℕ) : ℚ) = (p : ℚ) ^ 2 / 4 ↔ Even p := by
  constructor
  · intro h
    by_contra hodd
    exact family_arith p (Nat.not_even_iff_odd.mp hodd) _ h
  · rintro ⟨k, rfl⟩
    have h2 : (k + k) ^ 2 = 4 * (k * k) := by ring
    rw [h2, Nat.mul_div_cancel_left _ (by norm_num : 0 < 4)]
    push_cast
    ring

/-- "each by a defect of exactly 1/4": for odd p, p^2/4 - ⌊p^2/4⌋ = 1/4. -/
theorem defect_quarter (p : ℕ) (hp : Odd p) :
    (p : ℚ) ^ 2 / 4 - ((p ^ 2 / 4 : ℕ) : ℚ) = 1 / 4 := by
  obtain ⟨k, rfl⟩ := hp
  have h2 : (2 * k + 1) ^ 2 = 4 * (k * (k + 1)) + 1 := by ring
  have h3 : (2 * k + 1) ^ 2 / 4 = k * (k + 1) := by rw [h2]; omega
  rw [h3]
  push_cast
  ring

/-! ## (d) Exactness -/

/-- The source sentence holds at p exactly when p is even. -/
theorem exact (p : ℕ) : SourceClaim p ↔ Even p := by
  constructor
  · intro h
    by_contra hodd
    exact family p (Nat.not_even_iff_odd.mp hodd) h
  · intro hp
    have hr := repair p
    have hq := (floor_eq_iff_even p).mpr hp
    refine ⟨⟨p ^ 2 / 4, hr.1, hq⟩, ?_⟩
    rintro _ ⟨m, hm, rfl⟩
    rw [← hq]
    have hle : m ≤ p ^ 2 / 4 := hr.2 hm
    show (m : ℚ) ≤ ((p ^ 2 / 4 : ℕ) : ℚ)
    exact_mod_cast hle

/-- The source sentence and the repaired sentence agree exactly on the even p: the repair loses
nothing where the source was right. -/
theorem exact_true_max (p : ℕ) :
    IsGreatest ((fun m : ℕ => (m : ℚ)) '' BipCounts p) ((p ^ 2 / 4 : ℕ) : ℚ) := by
  have hr := repair p
  refine ⟨⟨_, hr.1, rfl⟩, ?_⟩
  rintro _ ⟨m, hm, rfl⟩
  have hle : m ≤ p ^ 2 / 4 := hr.2 hm
  show (m : ℚ) ≤ ((p ^ 2 / 4 : ℕ) : ℚ)
  exact_mod_cast hle

/-- At the released witness: the true maximum at p = 3 is 2, attained by the released graph. -/
theorem released_is_extremal : IsGreatest (BipCounts 3) 2 := by
  have h := repair 3
  have : (3 ^ 2 / 4 : ℕ) = 2 := by norm_num
  rwa [RepairedClaim, this] at h

/-! ## Readings under which the source sentence is true -/

/-- If "greatest number" is weakened to "upper bound", the printed formula is TRUE for every p:
a bipartite graph on p vertices has at most p^2/4 edges, in ℚ.  The refutation therefore needs
the exact ("greatest", attained) reading, which is the one the dossier states. -/
theorem upper_bound_reading_is_true {V : Type*} [Fintype V] {G : SimpleGraph V}
    (h : G.IsBipartite) : (edges G : ℚ) ≤ (Fintype.card V : ℚ) ^ 2 / 4 := by
  have h1 := repair_upper h
  have h2 : 4 * edges G ≤ Fintype.card V ^ 2 := by
    have := Nat.div_mul_le_self (Fintype.card V ^ 2) 4
    omega
  have h3 : ((4 * edges G : ℕ) : ℚ) ≤ ((Fintype.card V ^ 2 : ℕ) : ℚ) := by exact_mod_cast h2
  push_cast at h3
  linarith

/-! ## Formalisation hazard (second true reading) -/

/-- If the printed formula p^2/4 is read with natural-number division, the source sentence is
TRUE for every p: the refutation depends on reading the formula in ℚ (or ℝ), as the released
certificate does. -/
theorem nat_division_reading_is_true (p : ℕ) : IsGreatest (BipCounts p) (p ^ 2 / 4) := repair p

end Census_SE_math_1868681__q

#print axioms Census_SE_math_1868681__q.TreeCount.htree
#print axioms Census_SE_math_1868681__q.TreeCount.witness
#print axioms Census_SE_math_1868681__q.OddBipartite.witness
#print axioms Census_SE_math_1868681__q.edges_eq_card_edgeFinset
#print axioms Census_SE_math_1868681__q.released_bipartite
#print axioms Census_SE_math_1868681__q.released_count
#print axioms Census_SE_math_1868681__q.claim_refuted
#print axioms Census_SE_math_1868681__q.family_arith
#print axioms Census_SE_math_1868681__q.family_no_graph
#print axioms Census_SE_math_1868681__q.family
#print axioms Census_SE_math_1868681__q.family_unbounded
#print axioms Census_SE_math_1868681__q.repair_parts
#print axioms Census_SE_math_1868681__q.repair_colouring
#print axioms Census_SE_math_1868681__q.repair_subgraph
#print axioms Census_SE_math_1868681__q.edges_Kparts
#print axioms Census_SE_math_1868681__q.classes_le_floor
#print axioms Census_SE_math_1868681__q.classes_attained
#print axioms Census_SE_math_1868681__q.classes_isGreatest
#print axioms Census_SE_math_1868681__q.repair_upper
#print axioms Census_SE_math_1868681__q.edges_map_equiv
#print axioms Census_SE_math_1868681__q.edges_completeBipartite
#print axioms Census_SE_math_1868681__q.complete_bipartite_count
#print axioms Census_SE_math_1868681__q.repair
#print axioms Census_SE_math_1868681__q.repair_attained_nonempty_parts
#print axioms Census_SE_math_1868681__q.no_nonempty_parts_below_two
#print axioms Census_SE_math_1868681__q.floor_eq_iff_even
#print axioms Census_SE_math_1868681__q.defect_quarter
#print axioms Census_SE_math_1868681__q.exact
#print axioms Census_SE_math_1868681__q.exact_true_max
#print axioms Census_SE_math_1868681__q.released_is_extremal
#print axioms Census_SE_math_1868681__q.upper_bound_reading_is_true
#print axioms Census_SE_math_1868681__q.nat_division_reading_is_true
