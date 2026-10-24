import defs_only
/-!
Record E08: correction template.
Fill the ONE hole `«HOLE»` in the FIXED PART (nothing else in the fixed part may change), then prove
the OBLIGATIONS below with exactly these names and statements. Helper lemmas may be added between the
fixed part and the obligations, inside the namespace. Import nothing else.
-/
namespace Census_SE_math_1868681__q

-- ===== FIXED PART: only the hole «HOLE» may be edited =====
/-- The corrected greatest number of edges of a bipartite simple graph on `p` labelled vertices, as a
natural-number expression in `p` (the source prints `p^2/4`, read in ℚ). The hole must be a closed
expression in `p`: no reference to `BipCounts`, `edges`, `IsGreatest`, `sSup`, `Set`, `Finset`, `SimpleGraph`;
no `if`/`match`. -/
def max_edges (p : ℕ) : ℕ := p ^ 2 / 4

/-- The corrected sentence for every `p`: `max_edges p` is the greatest element of `BipCounts p`, an
attained maximum (shape fixed). -/
def CorrectedClaim : Prop := ∀ p : ℕ, IsGreatest (BipCounts p) (max_edges p)
-- ===== END FIXED PART =====

open SimpleGraph

theorem parts_bound {V : Type*} [Finite V] {G : SimpleGraph V} {s t : Set V}
    (h : G.IsBipartiteWith s t) : edges G ≤ s.ncard * t.ncard := by
  have h1 := h.encard_edgeSet_le
  rw [← (Set.toFinite G.edgeSet).cast_ncard_eq, ← s.toFinite.cast_ncard_eq,
    ← t.toFinite.cast_ncard_eq] at h1
  unfold edges
  exact_mod_cast h1

theorem colouring_bound {V : Type*} [Fintype V] {G : SimpleGraph V} (c : G.Coloring (Fin 2)) :
    edges G ≤ {v | c v = 0}.ncard * (Fintype.card V - {v | c v = 0}.ncard) := by
  have hb : G.IsBipartiteWith {v | c v = 0} {v | c v = 0}ᶜ := by
    refine ⟨disjoint_compl_right, fun v w hvw => ?_⟩
    have hne : c v ≠ c w := c.valid hvw
    have key : ∀ a b : Fin 2, a ≠ b → (a = 0 ∧ b ≠ 0) ∨ (a ≠ 0 ∧ b = 0) := by decide
    simpa using key _ _ hne
  have h1 := parts_bound hb
  have h2 := Set.ncard_add_ncard_compl {v | c v = 0}
  rw [Nat.card_eq_fintype_card] at h2
  have h3 : ({v | c v = 0}ᶜ : Set V).ncard = Fintype.card V - {v | c v = 0}.ncard := by omega
  rwa [h3] at h1

theorem classes_le_floor (p a : ℕ) : a * (p - a) ≤ p ^ 2 / 4 := by
  rw [Nat.le_div_iff_mul_le (by norm_num)]
  rcases le_total a p with h | h
  · obtain ⟨b, rfl⟩ := Nat.exists_eq_add_of_le h
    rw [Nat.add_sub_cancel_left]
    have := four_mul_le_sq_add a b
    nlinarith
  · simp [Nat.sub_eq_zero_of_le h]

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

theorem upper {V : Type*} [Fintype V] {G : SimpleGraph V} (h : G.IsBipartite) :
    edges G ≤ Fintype.card V ^ 2 / 4 := by
  obtain ⟨c⟩ := h
  exact (colouring_bound c).trans (classes_le_floor _ _)

theorem edges_map_equiv {W V : Type*} (e : W ≃ V) (H : SimpleGraph W) :
    edges (H.map e.toEmbedding) = edges H := by
  unfold edges
  rw [← Nat.card_coe_set_eq, ← Nat.card_coe_set_eq]
  exact (Nat.card_congr (SimpleGraph.Iso.map e H).mapEdgeSet).symm

theorem edges_completeBipartite (a b : ℕ) :
    edges (completeBipartiteGraph (Fin a) (Fin b)) = a * b := by
  have h := encard_edgeSet_completeBipartiteGraph (W₁ := Fin a) (W₂ := Fin b)
  rw [← (Set.toFinite _).cast_ncard_eq, ENat.card_eq_coe_fintype_card,
    ENat.card_eq_coe_fintype_card, Fintype.card_fin, Fintype.card_fin] at h
  unfold edges
  exact_mod_cast h

theorem complete_bipartite_count (p a : ℕ) (ha : a ≤ p) : a * (p - a) ∈ BipCounts p := by
  have hp : a + (p - a) = p := by omega
  let e : Fin a ⊕ Fin (p - a) ≃ Fin p := finSumFinEquiv.trans (finCongr hp)
  refine ⟨(completeBipartiteGraph (Fin a) (Fin (p - a))).map e.toEmbedding, ?_, ?_⟩
  · have hc : (completeBipartiteGraph (Fin a) (Fin (p - a))).Colorable 2 := by
      simpa using (CompleteBipartiteGraph.bicoloring (Fin a) (Fin (p - a))).colorable
    exact hc.of_hom (SimpleGraph.Iso.map e _).symm.toHom
  · rw [edges_map_equiv, edges_completeBipartite]

-- ===== OBLIGATIONS: keep the names and statements; replace each `sorry` by a proof =====
/-- Universal: for every `p`, `max_edges p` is attained by a bipartite graph on `Fin p` and bounds every
bipartite edge count on `Fin p`. -/
theorem repair_statement : ∀ p : ℕ, IsGreatest (Census_SE_math_1868681__q.BipCounts p) (Census_SE_math_1868681__q.max_edges p) := by
  intro p
  refine ⟨?_, ?_⟩
  · have h := complete_bipartite_count p (p / 2) (Nat.div_le_self p 2)
    unfold max_edges
    rwa [classes_attained] at h
  · rintro m ⟨G, hG, rfl⟩
    unfold max_edges
    simpa using upper hG

/-- Non-vacuity: the corrected value differs from the printed `p^2/4` (in ℚ) for some `p`. -/
theorem repair_nonvacuous : ∃ p : ℕ, (Census_SE_math_1868681__q.max_edges p : ℚ) ≠ (p : ℚ) ^ 2 / 4 := ⟨3, by unfold max_edges; norm_num⟩

/-- The endpoint of this record is the corrected universal statement itself; restate it here, e.g.
`:= repair_statement`. If you cannot, replace this declaration (this doc comment included) by the single
line `-- CANNOT: <reason>`. -/
theorem final_theorem : ∀ p : ℕ, IsGreatest (Census_SE_math_1868681__q.BipCounts p) (Census_SE_math_1868681__q.max_edges p) := repair_statement
-- ===== END OBLIGATIONS =====
end Census_SE_math_1868681__q
