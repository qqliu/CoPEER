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
def max_edges (p : ℕ) : ℕ := p * p / 4

/-- The corrected sentence for every `p`: `max_edges p` is the greatest element of `BipCounts p`, an
attained maximum (shape fixed). -/
def CorrectedClaim : Prop := ∀ p : ℕ, IsGreatest (BipCounts p) (max_edges p)
-- ===== END FIXED PART =====

open SimpleGraph

theorem ncard_lt (p k : ℕ) (hk : k ≤ p) : ({i : Fin p | i.val < k} : Set (Fin p)).ncard = k := by
  have : ({i : Fin p | i.val < k} : Set (Fin p)) = Fin.val ⁻¹' (Set.Iio k) := rfl
  rw [this, Set.ncard_preimage_of_injective_subset_range Fin.val_injective]
  · simp
  · intro x hx
    exact ⟨⟨x, by simp at hx; omega⟩, rfl⟩

theorem ncard_ge (p k : ℕ) (hk : k ≤ p) : ({i : Fin p | k ≤ i.val} : Set (Fin p)).ncard = p - k := by
  have h := Set.ncard_add_ncard_compl ({i : Fin p | i.val < k} : Set (Fin p))
  have : ({i : Fin p | i.val < k} : Set (Fin p))ᶜ = {i : Fin p | k ≤ i.val} := by
    ext i; simp
  rw [this, ncard_lt p k hk] at h
  simp at h
  omega

theorem arith_ub (a b : ℕ) : a * b ≤ (a + b) * (a + b) / 4 := by
  rw [Nat.le_div_iff_mul_le (by norm_num)]
  have : ((a:ℤ) - b)^2 ≥ 0 := sq_nonneg _
  have h2 : (a * b * 4 : ℤ) ≤ (a + b) * (a + b) := by nlinarith
  exact_mod_cast h2

theorem arith_eq (p : ℕ) : p / 2 * (p - p / 2) = p * p / 4 := by
  obtain ⟨m, rfl | rfl⟩ := Nat.even_or_odd' p
  · have h1 : 2 * m / 2 = m := by omega
    have h2 : 2 * m * (2 * m) = 4 * (m * m) := by ring
    rw [h1, h2]
    have : 2 * m - m = m := by omega
    rw [this]; omega
  · have h1 : (2 * m + 1) / 2 = m := by omega
    have h2 : (2 * m + 1) * (2 * m + 1) = 1 + 4 * (m * m + m) := by ring
    rw [h1, h2, Nat.add_mul_div_left _ _ (by norm_num)]
    have : 2 * m + 1 - m = m + 1 := by omega
    rw [this]; ring_nf

theorem upper (p : ℕ) (G : SimpleGraph (Fin p)) (hG : G.IsBipartite) : edges G ≤ p * p / 4 := by
  obtain ⟨C⟩ := hG
  set A : Set (Fin p) := {v | C v = 0}
  have hsub : G.edgeSet ⊆ (fun x : Fin p × Fin p => s(x.1, x.2)) '' (A ×ˢ Aᶜ) := by
    intro e he
    induction e using Sym2.ind with
    | _ u v =>
      have hadj : G.Adj u v := he
      have hne := C.valid hadj
      by_cases hu : C u = 0
      · refine ⟨(u, v), ⟨hu, ?_⟩, rfl⟩
        show ¬ C v = 0
        rw [← hu]; exact fun h => hne h.symm
      · have hv : C v = 0 := by
          have := (C u).isLt; have := (C v).isLt
          apply Fin.ext
          have h1 : (C u).val ≠ 0 := fun h => hu (Fin.ext h)
          have h2 : (C u).val ≠ (C v).val := fun h => hne (Fin.ext h)
          simp only [Fin.val_zero]; omega
        refine ⟨(v, u), ⟨hv, hu⟩, Sym2.eq_swap⟩
  unfold edges
  calc G.edgeSet.ncard ≤ ((fun x : Fin p × Fin p => s(x.1, x.2)) '' (A ×ˢ Aᶜ)).ncard := Set.ncard_le_ncard hsub (Set.toFinite _)
    _ ≤ (A ×ˢ Aᶜ).ncard := Set.ncard_image_le (Set.toFinite _)
    _ = A.ncard * Aᶜ.ncard := Set.ncard_prod
    _ ≤ (A.ncard + Aᶜ.ncard) * (A.ncard + Aᶜ.ncard) / 4 := arith_ub _ _
    _ = p * p / 4 := by rw [Set.ncard_add_ncard_compl]; simp

theorem attained (p : ℕ) : p * p / 4 ∈ BipCounts p := by
  set k := p / 2 with hk
  have hkp : k ≤ p := Nat.div_le_self _ _
  let G : SimpleGraph (Fin p) := SimpleGraph.fromRel (fun i j : Fin p => i.val < k ∧ k ≤ j.val)
  refine ⟨G, ?_, ?_⟩
  · refine ⟨SimpleGraph.Coloring.mk (fun v => if v.val < k then (0 : Fin 2) else 1) ?_⟩
    intro u v h
    simp only [G, SimpleGraph.fromRel_adj] at h
    rcases h with ⟨_, ⟨h1, h2⟩ | ⟨h1, h2⟩⟩
    · simp [h1, show ¬ v.val < k by omega]
    · simp [h1, show ¬ u.val < k by omega]
  · set S : Set (Fin p × Fin p) := {i : Fin p | i.val < k} ×ˢ {j : Fin p | k ≤ j.val}
    have hE : G.edgeSet = (fun x : Fin p × Fin p => s(x.1, x.2)) '' S := by
      ext e
      induction e using Sym2.ind with
      | _ u v =>
        simp only [SimpleGraph.mem_edgeSet, G, SimpleGraph.fromRel_adj, Set.mem_image, S,
          Set.mem_prod, Set.mem_setOf_eq, Prod.exists, Sym2.eq_iff]
        constructor
        · rintro ⟨_, ⟨h1, h2⟩ | ⟨h1, h2⟩⟩
          · exact ⟨u, v, ⟨h1, h2⟩, Or.inl ⟨rfl, rfl⟩⟩
          · exact ⟨v, u, ⟨h1, h2⟩, Or.inr ⟨rfl, rfl⟩⟩
        · rintro ⟨a, b, ⟨h1, h2⟩, ⟨rfl, rfl⟩ | ⟨rfl, rfl⟩⟩
          · exact ⟨fun h => by subst h; omega, Or.inl ⟨h1, h2⟩⟩
          · exact ⟨fun h => by subst h; omega, Or.inr ⟨h1, h2⟩⟩
    have hinj : Set.InjOn (fun x : Fin p × Fin p => s(x.1, x.2)) S := by
      rintro ⟨a, b⟩ ⟨ha, hb⟩ ⟨c, d⟩ ⟨hc, hd⟩ h
      simp only [Set.mem_setOf_eq] at ha hb hc hd
      have h' : s(a, b) = s(c, d) := h
      rcases Sym2.eq_iff.mp h' with ⟨rfl, rfl⟩ | ⟨rfl, rfl⟩
      · rfl
      · omega
    unfold edges
    rw [hE, Set.InjOn.ncard_image hinj, Set.ncard_prod, ncard_lt p k hkp, ncard_ge p k hkp,
      hk, arith_eq]

theorem repair_statement : ∀ p : ℕ, IsGreatest (Census_SE_math_1868681__q.BipCounts p) (Census_SE_math_1868681__q.max_edges p) := by
  intro p
  refine ⟨attained p, ?_⟩
  rintro m ⟨G, hG, rfl⟩
  exact upper p G hG

theorem repair_nonvacuous : ∃ p : ℕ, (Census_SE_math_1868681__q.max_edges p : ℚ) ≠ (p : ℚ) ^ 2 / 4 := by
  refine ⟨1, ?_⟩
  simp [max_edges]

theorem final_theorem : ∀ p : ℕ, IsGreatest (Census_SE_math_1868681__q.BipCounts p) (Census_SE_math_1868681__q.max_edges p) :=
  repair_statement

end Census_SE_math_1868681__q
