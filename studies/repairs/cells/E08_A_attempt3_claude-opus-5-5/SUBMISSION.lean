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
def max_edges (p : ℕ) : ℕ := (p / 2) * (p - p / 2)

/-- The corrected sentence for every `p`: `max_edges p` is the greatest element of `BipCounts p`, an
attained maximum (shape fixed). -/
def CorrectedClaim : Prop := ∀ p : ℕ, IsGreatest (BipCounts p) (max_edges p)
-- ===== END FIXED PART =====

def cb (p : ℕ) (f : Fin p → Bool) : SimpleGraph (Fin p) where
  Adj i j := f i ≠ f j
  symm := fun _ _ h => Ne.symm h
  loopless := ⟨fun _ h => h rfl⟩

lemma cb_edges (p : ℕ) (f : Fin p → Bool) :
    edges (cb p f) = (Finset.univ.filter (fun i => f i = true)).card *
      (Finset.univ.filter (fun i => ¬ f i = true)).card := by
  classical
  have h1 : edges (cb p f) = (cb p f).edgeFinset.card := by
    rw [edges, ← SimpleGraph.coe_edgeFinset, Set.ncard_coe_finset]
  have h2 := SimpleGraph.sum_degrees_eq_twice_card_edges (cb p f)
  have hdeg : ∀ i, (cb p f).degree i =
      if f i = true then (Finset.univ.filter (fun i => ¬ f i = true)).card
      else (Finset.univ.filter (fun i => f i = true)).card := by
    intro i
    rw [← SimpleGraph.card_neighborFinset_eq_degree]
    split_ifs with hf <;>
    · congr 1
      ext j
      simp only [SimpleGraph.mem_neighborFinset, cb, Finset.mem_filter, Finset.mem_univ, true_and]
      cases hj : f j <;> simp_all
  simp_rw [hdeg] at h2
  rw [← Finset.sum_filter_add_sum_filter_not Finset.univ (fun i => f i = true)] at h2
  rw [Finset.sum_congr rfl (fun x hx => if_pos (Finset.mem_filter.mp hx).2),
    Finset.sum_congr rfl (fun x hx => if_neg (Finset.mem_filter.mp hx).2)] at h2
  simp only [Finset.sum_const, smul_eq_mul] at h2
  rw [h1]
  rw [Nat.mul_comm (Finset.univ.filter (fun i => ¬ f i = true)).card] at h2
  linarith

lemma key (a b : ℕ) : a * b ≤ ((a + b) / 2) * ((a + b) - (a + b) / 2) := by
  generalize hk : (a + b) / 2 = k
  rcases (show a + b = 2 * k ∨ a + b = 2 * k + 1 by omega) with h | h
  · rw [show a + b - k = k by omega]
    rcases le_or_gt a k with h' | h'
    · obtain ⟨s, rfl⟩ : ∃ s, k = a + s := ⟨k - a, by omega⟩
      have : b = a + 2 * s := by omega
      subst this; nlinarith
    · obtain ⟨s, rfl⟩ : ∃ s, a = k + s := ⟨a - k, by omega⟩
      have : k = b + s := by omega
      subst this; nlinarith
  · rw [show a + b - k = k + 1 by omega]
    rcases le_or_gt a k with h' | h'
    · obtain ⟨s, rfl⟩ : ∃ s, k = a + s := ⟨k - a, by omega⟩
      have : b = a + 2 * s + 1 := by omega
      subst this; nlinarith
    · obtain ⟨s, rfl⟩ : ∃ s, a = k + 1 + s := ⟨a - k - 1, by omega⟩
      have : k = b + s := by omega
      subst this; nlinarith

theorem repair_statement : ∀ p : ℕ, IsGreatest (Census_SE_math_1868681__q.BipCounts p) (Census_SE_math_1868681__q.max_edges p) := by
  intro p
  constructor
  · refine ⟨cb p (fun i => decide (i.val < p / 2)), ?_, ?_⟩
    · refine ⟨⟨fun i => if i.val < p / 2 then 0 else 1, ?_⟩⟩
      intro i j h
      simp only [cb, SimpleGraph.top_adj] at h ⊢
      by_cases hi : i.val < p / 2 <;> by_cases hj : j.val < p / 2 <;> simp_all
    · rw [cb_edges, max_edges]
      have ha : (Finset.univ.filter (fun i : Fin p => decide (i.val < p / 2) = true)).card = p / 2 := by
        simp only [decide_eq_true_eq]
        rw [Fin.card_filter_val_lt]; omega
      have hab := Finset.filter_card_add_filter_neg_card_eq_card
        (s := (Finset.univ : Finset (Fin p))) (fun i : Fin p => decide (i.val < p / 2) = true)
      rw [Finset.card_univ, Fintype.card_fin] at hab
      rw [ha] at hab ⊢
      congr 1; omega
  · rintro m ⟨G, ⟨c⟩, rfl⟩
    let f : Fin p → Bool := fun i => decide (c i = 0)
    have hle : G ≤ cb p f := by
      intro i j h
      have := c.valid h
      simp only [cb, f]
      intro h2
      apply this
      revert h2
      generalize c i = x; generalize c j = y
      fin_cases x <;> fin_cases y <;> simp
    have h1 : edges G ≤ edges (cb p f) :=
      Set.ncard_le_ncard ((SimpleGraph.edgeSet_subset_edgeSet).mpr hle) (Set.toFinite _)
    refine h1.trans ?_
    rw [cb_edges, max_edges]
    have hab := Finset.filter_card_add_filter_neg_card_eq_card
      (s := (Finset.univ : Finset (Fin p))) (fun i : Fin p => f i = true)
    rw [Finset.card_univ, Fintype.card_fin] at hab
    have := key (Finset.univ.filter (fun i => f i = true)).card
      (Finset.univ.filter (fun i => ¬ f i = true)).card
    rw [hab] at this
    exact this

theorem repair_nonvacuous : ∃ p : ℕ, (Census_SE_math_1868681__q.max_edges p : ℚ) ≠ (p : ℚ) ^ 2 / 4 := by
  refine ⟨1, ?_⟩
  simp [max_edges]

theorem final_theorem : ∀ p : ℕ, IsGreatest (Census_SE_math_1868681__q.BipCounts p) (Census_SE_math_1868681__q.max_edges p) :=
  repair_statement

end Census_SE_math_1868681__q
