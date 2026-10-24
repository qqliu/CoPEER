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
def max_edges (p : ℕ) : ℕ := p^2 / 4

/-- The corrected sentence for every `p`: `max_edges p` is the greatest element of `BipCounts p`, an
attained maximum (shape fixed). -/
def CorrectedClaim : Prop := ∀ p : ℕ, IsGreatest (BipCounts p) (max_edges p)
-- ===== END FIXED PART =====

open SimpleGraph

/-- A "left" subset of `Fin p` of size `p / 2`, obtained by casting `Fin (p / 2)` into `Fin p`. -/
def leftSet (p : ℕ) : Finset (Fin p) :=
  (Finset.univ : Finset (Fin (p/2))).map (Fin.castLEOrderEmb (Nat.div_le_self p 2)).toEmbedding

lemma leftSet_card (p : ℕ) : (leftSet p).card = p / 2 := by
  simp [leftSet]

lemma card_formula (p : ℕ) : (p/2) * (p - p/2) = p^2/4 := by
  rcases Nat.even_or_odd p with ⟨k,hk⟩ | ⟨k,hk⟩
  · subst hk
    have h1 : (k+k)/2 = k := by omega
    have h2 : (k+k) - k = k := by omega
    rw [h1, h2]
    have h3 : (k+k)^2 = 4*(k*k) := by ring
    rw [h3]
    omega
  · subst hk
    have h1 : (2*k+1)/2 = k := by omega
    have h2 : (2*k+1) - k = k+1 := by omega
    rw [h1, h2]
    have h3 : (2*k+1)^2 = 4*(k*(k+1)) + 1 := by ring
    rw [h3]
    omega

lemma max_edges_mem (p : ℕ) : max_edges p ∈ BipCounts p := by
  classical
  set sL : Finset (Fin p) := leftSet p with hsL
  set G : SimpleGraph (Fin p) := (⊤ : SimpleGraph (Fin p)).between (↑sL) (↑sL)ᶜ with hG
  have hdisj : Disjoint (↑sL : Set (Fin p)) (↑sL : Set (Fin p))ᶜ := disjoint_compl_right
  have hbip : G.IsBipartite := between_isBipartite hdisj
  refine ⟨G, hbip, ?_⟩
  have hbw : G.IsBipartiteWith (↑sL : Set (Fin p)) (↑sL : Set (Fin p))ᶜ := between_isBipartiteWith hdisj
  have hcoe : ((sLᶜ : Finset (Fin p)) : Set (Fin p)) = (↑sL : Set (Fin p))ᶜ := Finset.coe_compl sL
  have hbw2 : G.IsBipartiteWith sL (sLᶜ : Finset (Fin p)) := hcoe ▸ hbw
  have hsum := isBipartiteWith_sum_degrees_eq_card_edges hbw2
  have hdeg : ∀ v ∈ sL, G.degree v = (sLᶜ : Finset (Fin p)).card := by
    intro v hv
    have hnb := isBipartiteWith_neighborFinset hbw2 hv
    have hfilter : ({w ∈ (sLᶜ : Finset (Fin p)) | G.Adj v w}) = (sLᶜ : Finset (Fin p)) := by
      apply Finset.filter_true_of_mem
      intro w hw
      have hwc : w ∉ (↑sL : Set (Fin p)) := Finset.mem_compl.mp hw
      have hvw : v ≠ w := fun he => hwc (he ▸ hv)
      exact ⟨hvw, Or.inl ⟨hv, hwc⟩⟩
    rw [← card_neighborFinset_eq_degree, hnb, hfilter]
  have hsum2 : ∑ v ∈ sL, G.degree v = sL.card * (sLᶜ : Finset (Fin p)).card := by
    rw [Finset.sum_congr rfl hdeg, Finset.sum_const, smul_eq_mul]
  rw [hsum2] at hsum
  have hcardL : sL.card = p / 2 := leftSet_card p
  have hcardR : (sLᶜ : Finset (Fin p)).card = p - p/2 := by
    rw [Finset.card_compl, hcardL, Fintype.card_fin]
  show G.edgeSet.ncard = max_edges p
  rw [Set.ncard_eq_toFinset_card' G.edgeSet]
  have : G.edgeSet.toFinset = G.edgeFinset := rfl
  rw [this, ← hsum, hcardL, hcardR, card_formula]
  rfl

lemma max_edges_isUB (p : ℕ) : max_edges p ∈ upperBounds (BipCounts p) := by
  rintro b ⟨H, hHbip, hHedges⟩
  have h4 : 4 * H.edgeSet.encard ≤ (ENat.card (Fin p))^2 := hHbip.four_mul_encard_edgeSet_le
  have hcard : ENat.card (Fin p) = (p:ℕ∞) := by
    rw [ENat.card_eq_coe_fintype_card]
    simp
  rw [hcard] at h4
  have hfin : H.edgeSet.Finite := Set.toFinite _
  have hHedges' : H.edgeSet.ncard = b := hHedges
  have hb : (b : ℕ∞) = H.edgeSet.encard := by rw [← hHedges']; exact hfin.cast_ncard_eq
  rw [← hb] at h4
  have h4' : 4 * b ≤ p^2 := by exact_mod_cast h4
  have : b ≤ p^2/4 := (Nat.le_div_iff_mul_le (by norm_num)).mpr (by linarith)
  simpa [max_edges] using this

theorem repair_statement : ∀ p : ℕ, IsGreatest (Census_SE_math_1868681__q.BipCounts p) (Census_SE_math_1868681__q.max_edges p) :=
  fun p => ⟨max_edges_mem p, max_edges_isUB p⟩

theorem repair_nonvacuous : ∃ p : ℕ, (Census_SE_math_1868681__q.max_edges p : ℚ) ≠ (p : ℚ) ^ 2 / 4 := by
  use 3
  simp [max_edges]
  norm_num

theorem final_theorem : ∀ p : ℕ, IsGreatest (Census_SE_math_1868681__q.BipCounts p) (Census_SE_math_1868681__q.max_edges p) := repair_statement

end Census_SE_math_1868681__q
