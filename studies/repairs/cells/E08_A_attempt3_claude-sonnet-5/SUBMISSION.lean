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

open SimpleGraph Finset

/-- The balanced split value `p / 2`. -/
private def half (p : ℕ) : ℕ := p / 2

private lemma half_le (p : ℕ) : half p ≤ p := Nat.div_le_self p 2

/-- The "first `half p`" indices, as a `Finset (Fin p)`. -/
private def leftSet (p : ℕ) : Finset (Fin p) :=
  Finset.image (Fin.castLE (half_le p)) Finset.univ

private lemma leftSet_card (p : ℕ) : (leftSet p).card = half p := by
  rw [leftSet, Finset.card_image_of_injective _ (Fin.castLE_injective (half_le p))]
  simp

private lemma mem_leftSet (p : ℕ) (v : Fin p) : v ∈ leftSet p ↔ v.val < half p := by
  simp only [leftSet, Finset.mem_image, Finset.mem_univ, true_and]
  constructor
  · rintro ⟨a, rfl⟩
    exact a.isLt
  · intro hv
    exact ⟨⟨v.val, hv⟩, rfl⟩

private lemma mem_rightSet (p : ℕ) (v : Fin p) :
    v ∈ (leftSet p)ᶜ ↔ ¬ v.val < half p := by
  rw [Finset.mem_compl, mem_leftSet]

private lemma rightSet_card (p : ℕ) : ((leftSet p)ᶜ).card = p - half p := by
  rw [Finset.card_compl, leftSet_card]
  simp

/-- The concrete bipartite graph achieving the balanced split, on `Fin p`. -/
private def balGraph (p : ℕ) : SimpleGraph (Fin p) :=
  (⊤ : SimpleGraph (Fin p)).between (↑(leftSet p) : Set (Fin p)) (↑((leftSet p)ᶜ) : Set (Fin p))

private lemma balGraph_isBipartiteWith (p : ℕ) :
    (balGraph p).IsBipartiteWith (leftSet p) ((leftSet p)ᶜ) :=
  SimpleGraph.between_isBipartiteWith (Finset.disjoint_coe.mpr disjoint_compl_right)

private lemma balGraph_isBipartite (p : ℕ) : (balGraph p).IsBipartite :=
  (balGraph_isBipartiteWith p).isBipartite

private instance (p : ℕ) : DecidableRel (balGraph p).Adj := by
  unfold balGraph SimpleGraph.between
  infer_instance

private lemma balGraph_degree_left (p : ℕ) (v : Fin p) (hv : v ∈ leftSet p) :
    (balGraph p).degree v = p - half p := by
  classical
  have hnf : (balGraph p).neighborFinset v = {w ∈ (leftSet p)ᶜ | (balGraph p).Adj v w} :=
    isBipartiteWith_neighborFinset (balGraph_isBipartiteWith p) hv
  have hall : ∀ w ∈ (leftSet p)ᶜ, (balGraph p).Adj v w := by
    intro w hw
    have hvne : v ≠ w := by
      intro h
      subst h
      exact (Finset.mem_compl.mp hw) hv
    exact ⟨hvne, Or.inl ⟨hv, hw⟩⟩
  have hfilter : ({w ∈ (leftSet p)ᶜ | (balGraph p).Adj v w} : Finset (Fin p)) = (leftSet p)ᶜ :=
    Finset.filter_true_of_mem hall
  rw [← SimpleGraph.card_neighborFinset_eq_degree, hnf, hfilter, rightSet_card]

private lemma balGraph_edges (p : ℕ) : edges (balGraph p) = half p * (p - half p) := by
  classical
  have hsum : ∑ v ∈ leftSet p, (balGraph p).degree v = (balGraph p).edgeFinset.card :=
    isBipartiteWith_sum_degrees_eq_card_edges (balGraph_isBipartiteWith p)
  have hsum' : ∑ v ∈ leftSet p, (balGraph p).degree v = half p * (p - half p) := by
    rw [Finset.sum_congr rfl (fun v hv => balGraph_degree_left p v hv)]
    rw [Finset.sum_const, leftSet_card]
    ring
  have hedges : edges (balGraph p) = (balGraph p).edgeFinset.card := by
    rw [edges, ← SimpleGraph.coe_edgeFinset, Set.ncard_coe_Finset]
  rw [hedges, ← hsum, hsum']

private lemma half_mul_sub_half_eq (p : ℕ) : half p * (p - half p) = p ^ 2 / 4 := by
  rcases Nat.even_or_odd p with ⟨m, hm⟩ | ⟨m, hm⟩ <;> subst hm
  · have h1 : half (m + m) = m := by
      unfold half; omega
    rw [h1]
    have h2 : m + m - m = m := by omega
    rw [h2]
    have h3 : (m + m) ^ 2 = 4 * m ^ 2 := by ring
    rw [h3]
    rw [Nat.mul_div_cancel_left _ (by norm_num)]
    ring
  · have h1 : half (2 * m + 1) = m := by
      unfold half; omega
    rw [h1]
    have h2 : 2 * m + 1 - m = m + 1 := by omega
    rw [h2]
    have h3 : (2 * m + 1) ^ 2 = 4 * (m * (m + 1)) + 1 := by ring
    rw [h3]
    rw [Nat.add_mul_div_left _ _ (by norm_num : (0:ℕ) < 4)]
    simp

private lemma balGraph_edges_eq (p : ℕ) : edges (balGraph p) = max_edges p := by
  rw [balGraph_edges, half_mul_sub_half_eq, max_edges]

private lemma mem_bipCounts (p : ℕ) : max_edges p ∈ BipCounts p :=
  ⟨balGraph p, balGraph_isBipartite p, balGraph_edges_eq p⟩

private lemma upper_bound (p : ℕ) : ∀ m ∈ BipCounts p, m ≤ max_edges p := by
  intro m hm
  obtain ⟨G, hG, hedges⟩ := hm
  have hfin : G.edgeSet.Finite := Set.toFinite _
  have hcast : (m : ℕ∞) = G.edgeSet.encard := by
    rw [← hedges, edges, ← hfin.cast_ncard_eq]
  have hbound := hG.four_mul_encard_edgeSet_le
  rw [← hcast] at hbound
  have hp : ENat.card (Fin p) = (p : ℕ∞) := by
    simp [ENat.card_eq_coe_natCard, Nat.card_eq_fintype_card]
  rw [hp] at hbound
  have hbound' : 4 * m ≤ p ^ 2 := by exact_mod_cast hbound
  rw [max_edges, Nat.le_div_iff_mul_le (by norm_num : (0:ℕ) < 4)]
  omega

-- ===== OBLIGATIONS =====

theorem repair_statement : ∀ p : ℕ, IsGreatest (Census_SE_math_1868681__q.BipCounts p) (Census_SE_math_1868681__q.max_edges p) := by
  intro p
  exact ⟨mem_bipCounts p, upper_bound p⟩

theorem repair_nonvacuous : ∃ p : ℕ, (Census_SE_math_1868681__q.max_edges p : ℚ) ≠ (p : ℚ) ^ 2 / 4 := by
  refine ⟨3, ?_⟩
  norm_num [max_edges]

theorem final_theorem : ∀ p : ℕ, IsGreatest (Census_SE_math_1868681__q.BipCounts p) (Census_SE_math_1868681__q.max_edges p) := repair_statement

end Census_SE_math_1868681__q
