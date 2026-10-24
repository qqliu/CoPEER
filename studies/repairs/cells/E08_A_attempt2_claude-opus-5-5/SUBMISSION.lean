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
def max_edges (p : ℕ) : ℕ := p / 2 * (p - p / 2)

/-- The corrected sentence for every `p`: `max_edges p` is the greatest element of `BipCounts p`, an
attained maximum (shape fixed). -/
def CorrectedClaim : Prop := ∀ p : ℕ, IsGreatest (BipCounts p) (max_edges p)
-- ===== END FIXED PART =====

open SimpleGraph

theorem ab_le (p a b : ℕ) (h : a + b ≤ p) : a * b ≤ p / 2 * (p - p / 2) := by
  obtain ⟨k, hk | hk⟩ : ∃ k, p = 2 * k ∨ p = 2 * k + 1 := ⟨p / 2, by omega⟩
  · have h1 : p / 2 = k := by omega
    have h2 : p - p / 2 = k := by omega
    rw [h2, h1]
    by_contra hc
    push_neg at hc
    have : (a:ℤ) + b ≤ 2 * k := by exact_mod_cast (hk ▸ h)
    have hc' : (k:ℤ) * k < a * b := by exact_mod_cast hc
    nlinarith [sq_nonneg ((a:ℤ) - b), (Nat.cast_nonneg a : (0:ℤ) ≤ a), (Nat.cast_nonneg b : (0:ℤ) ≤ b)]
  · have h1 : p / 2 = k := by omega
    have h2 : p - p / 2 = k + 1 := by omega
    rw [h2, h1]
    by_contra hc
    push_neg at hc
    have : (a:ℤ) + b ≤ 2 * k + 1 := by exact_mod_cast (hk ▸ h)
    have hc' : (k:ℤ) * (k + 1) + 1 ≤ a * b := by exact_mod_cast hc
    nlinarith [sq_nonneg ((a:ℤ) - b), (Nat.cast_nonneg a : (0:ℤ) ≤ a), (Nat.cast_nonneg b : (0:ℤ) ≤ b)]

theorem upper (p : ℕ) (G : SimpleGraph (Fin p)) (hG : G.IsBipartite) :
    edges G ≤ max_edges p := by
  obtain ⟨s, t, h⟩ := isBipartite_iff_exists_isBipartiteWith.mp hG
  have hsub : G.edgeSet ⊆ (fun x : Fin p × Fin p => s(x.1, x.2)) '' (s ×ˢ t) := by
    intro e he
    induction e using Sym2.ind with
    | h v w =>
      rcases h.mem_of_adj he with ⟨hv, hw⟩ | ⟨hv, hw⟩
      · exact ⟨(v, w), ⟨hv, hw⟩, rfl⟩
      · exact ⟨(w, v), ⟨hw, hv⟩, Sym2.eq_swap⟩
  have h1 : edges G ≤ s.ncard * t.ncard := by
    unfold edges
    calc G.edgeSet.ncard ≤ ((fun x : Fin p × Fin p => s(x.1, x.2)) '' (s ×ˢ t)).ncard :=
          Set.ncard_le_ncard hsub (Set.toFinite _)
      _ ≤ (s ×ˢ t).ncard := Set.ncard_image_le (Set.toFinite _)
      _ = s.ncard * t.ncard := Set.ncard_prod
  have h2 : s.ncard + t.ncard ≤ p := by
    rw [← Set.ncard_union_eq h.disjoint (Set.toFinite _) (Set.toFinite _)]
    calc (s ∪ t).ncard ≤ (Set.univ : Set (Fin p)).ncard :=
          Set.ncard_le_ncard (Set.subset_univ _) (Set.toFinite _)
      _ = p := by simp
  exact h1.trans (ab_le p _ _ h2)

def emb (p : ℕ) : Fin (p / 2) × Fin (p - p / 2) → Sym2 (Fin p) :=
  fun x => s((⟨x.1.val, by omega⟩ : Fin p), (⟨p / 2 + x.2.val, by omega⟩ : Fin p))

theorem emb_inj (p : ℕ) : Function.Injective (emb p) := by
  rintro ⟨i, j⟩ ⟨i', j'⟩ h
  simp only [emb, Sym2.eq_iff, Fin.mk.injEq] at h
  rcases h with ⟨h1, h2⟩ | ⟨h1, h2⟩
  · ext <;> simp <;> omega
  · omega

theorem lower (p : ℕ) : max_edges p ∈ BipCounts p := by
  refine ⟨SimpleGraph.fromEdgeSet (Set.range (emb p)), ?_, ?_⟩
  · refine IsBipartiteWith.isBipartite (s := {v | v.val < p / 2}) (t := {v | ¬ v.val < p / 2}) ⟨?_, ?_⟩
    · exact Set.disjoint_left.mpr (fun v hv hv' => hv' hv)
    · intro v w hvw
      rw [fromEdgeSet_adj] at hvw
      obtain ⟨⟨⟨i, j⟩, hij⟩, _⟩ := hvw
      simp only [emb, Sym2.eq_iff] at hij
      rcases hij with ⟨rfl, rfl⟩ | ⟨rfl, rfl⟩
      · left; simp
      · right; simp
  · unfold edges
    rw [edgeSet_fromEdgeSet]
    have : Set.range (emb p) \ Sym2.diagSet = Set.range (emb p) := by
      apply sdiff_eq_left.mpr
      rw [Set.disjoint_left]
      rintro e ⟨⟨i, j⟩, rfl⟩ hd
      first
        | (simp [emb] at hd; omega)
        | (simp [emb, Sym2.diagSet, Sym2.IsDiag] at hd; omega)
        | (rw [Sym2.mem_diagSet_iff_isDiag] at hd; simp [emb] at hd; omega)
    rw [this, ← Set.image_univ, Set.ncard_image_of_injective _ (emb_inj p)]
    simp [max_edges]

theorem repair_statement : ∀ p : ℕ, IsGreatest (Census_SE_math_1868681__q.BipCounts p) (Census_SE_math_1868681__q.max_edges p) := by
  intro p
  refine ⟨lower p, ?_⟩
  rintro m ⟨G, hG, rfl⟩
  exact upper p G hG

theorem repair_nonvacuous : ∃ p : ℕ, (Census_SE_math_1868681__q.max_edges p : ℚ) ≠ (p : ℚ) ^ 2 / 4 := by
  refine ⟨1, ?_⟩
  simp [max_edges]

theorem final_theorem : ∀ p : ℕ, IsGreatest (Census_SE_math_1868681__q.BipCounts p) (Census_SE_math_1868681__q.max_edges p) :=
  repair_statement

end Census_SE_math_1868681__q
