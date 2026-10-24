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
def max_edges (p : ℕ) : ℕ := p^2/4

/-- The corrected sentence for every `p`: `max_edges p` is the greatest element of `BipCounts p`, an
attained maximum (shape fixed). -/
def CorrectedClaim : Prop := ∀ p : ℕ, IsGreatest (BipCounts p) (max_edges p)
-- ===== END FIXED PART =====

open SimpleGraph

/-- `max_edges p` equals `(p/2) * (p - p/2)` (the balanced product identity). -/
theorem max_edges_eq (p : ℕ) : max_edges p = p / 2 * (p - p / 2) := by
  have hk : p / 2 ≤ p := Nat.div_le_self p 2
  have hdm : 2 * (p / 2) + p % 2 = p := Nat.div_add_mod p 2
  have hr : p % 2 < 2 := Nat.mod_lt p (by norm_num)
  have hsub : p - p / 2 = p / 2 + p % 2 := by omega
  have hsq : p ^ 2 = (p % 2) ^ 2 + 4 * (p / 2 * (p - p / 2)) := by
    rw [hsub]
    have : p = 2 * (p / 2) + p % 2 := by omega
    nlinarith [this]
  have hlt : (p % 2) ^ 2 < 4 := by nlinarith [hr]
  show p ^ 2 / 4 = p / 2 * (p - p / 2)
  rw [hsq, Nat.add_mul_div_left _ _ (by norm_num : 0 < 4), Nat.div_eq_of_lt hlt]

/-- Every bipartite simple graph on `Fin p` has at most `max_edges p` edges. -/
theorem bip_edges_le {p : ℕ} {G : SimpleGraph (Fin p)} (hG : G.IsBipartite) :
    edges G ≤ max_edges p := by
  have h4 := hG.four_mul_encard_edgeSet_le
  rw [ENat.card_eq_coe_fintype_card, Fintype.card_fin] at h4
  have hfin : G.edgeSet.Finite := Set.toFinite _
  have heq : G.edgeSet.encard = (edges G : ℕ∞) := (Set.Finite.encard_eq_coe hfin)
  rw [heq] at h4
  have h4' : (4 * edges G : ℕ) ≤ p ^ 2 := by exact_mod_cast h4
  show edges G ≤ p ^ 2 / 4
  rw [Nat.le_div_iff_mul_le (by norm_num : 0 < 4)]
  omega

/-- There exists a bipartite simple graph on `Fin p` with exactly `max_edges p` edges. -/
theorem bip_edges_exists (p : ℕ) : ∃ G : SimpleGraph (Fin p), G.IsBipartite ∧ edges G = max_edges p := by
  classical
  set k := p / 2 with hk_def
  set l := p - k with hl_def
  have hkl : k + l = p := by omega
  let e : Fin k ⊕ Fin l ≃ Fin p := finSumFinEquiv.trans (finCongr hkl)
  let C : SimpleGraph (Fin k ⊕ Fin l) := completeBipartiteGraph (Fin k) (Fin l)
  let G : SimpleGraph (Fin p) := C.map e.toEmbedding
  have hCbip : C.IsBipartiteWith {v : Fin k ⊕ Fin l | v.isLeft} {v : Fin k ⊕ Fin l | v.isRight} := by
    constructor
    · rw [Set.disjoint_left]
      rintro v hv1 hv2
      cases v <;> simp_all
    · intro v w h
      rcases h with ⟨hv, hw⟩ | ⟨hv, hw⟩
      · left; exact ⟨hv, hw⟩
      · right; exact ⟨hv, hw⟩
  have hGbip : G.IsBipartiteWith (e '' {v : Fin k ⊕ Fin l | v.isLeft})
      (e '' {v : Fin k ⊕ Fin l | v.isRight}) := by
    constructor
    · exact Set.disjoint_image_of_injective e.injective hCbip.disjoint
    · intro v w hvw
      obtain ⟨a, b, hab, ha, hb⟩ := (SimpleGraph.map_adj e.toEmbedding C v w).mp hvw
      rcases hCbip.mem_of_adj hab with ⟨has, hbt⟩ | ⟨hat, hbs⟩
      · left; exact ⟨ha ▸ Set.mem_image_of_mem e has, hb ▸ Set.mem_image_of_mem e hbt⟩
      · right; exact ⟨ha ▸ Set.mem_image_of_mem e hat, hb ▸ Set.mem_image_of_mem e hbs⟩
  refine ⟨G, hGbip.isBipartite, ?_⟩
  have hcard : #G.edgeFinset = #C.edgeFinset := SimpleGraph.card_edgeFinset_map e.toEmbedding C
  have heG : edges G = #G.edgeFinset := by
    rw [SimpleGraph.edges, Set.ncard_eq_toFinset_card' G.edgeSet, SimpleGraph.edgeFinset]
  have heC : edges C = #C.edgeFinset := by
    rw [SimpleGraph.edges, Set.ncard_eq_toFinset_card' C.edgeSet, SimpleGraph.edgeFinset]
  have hCedges : edges C = k * l := by
    have hh := SimpleGraph.encard_edgeSet_completeBipartiteGraph (V := Fin k) (W := Fin l)
    rw [ENat.card_eq_coe_fintype_card, ENat.card_eq_coe_fintype_card, Fintype.card_fin,
      Fintype.card_fin] at hh
    have hfin : C.edgeSet.Finite := Set.toFinite _
    have heq : C.edgeSet.encard = (edges C : ℕ∞) := (Set.Finite.encard_eq_coe hfin)
    rw [heq] at hh
    exact_mod_cast hh
  rw [heG, hcard, ← heC, hCedges, max_edges_eq]

theorem repair_statement : ∀ p : ℕ, IsGreatest (Census_SE_math_1868681__q.BipCounts p) (Census_SE_math_1868681__q.max_edges p) := by
  intro p
  constructor
  · obtain ⟨G, hG, hedges⟩ := bip_edges_exists p
    exact ⟨G, hG, hedges⟩
  · rintro m ⟨G, hG, rfl⟩
    exact bip_edges_le hG

theorem repair_nonvacuous : ∃ p : ℕ, (Census_SE_math_1868681__q.max_edges p : ℚ) ≠ (p : ℚ) ^ 2 / 4 := by
  refine ⟨3, ?_⟩
  norm_num [max_edges]

theorem final_theorem : ∀ p : ℕ, IsGreatest (Census_SE_math_1868681__q.BipCounts p) (Census_SE_math_1868681__q.max_edges p) := repair_statement

end Census_SE_math_1868681__q
