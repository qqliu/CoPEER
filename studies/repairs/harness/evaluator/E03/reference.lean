import defs_only
/- EVALUATOR-ONLY reference correction for E03 (original package: repair, line 62; repair_divfree, line 51). -/
namespace SE_cs_13118_a13122_explanation_real.Ref

/-- Reference corrected closed form: `(c ^ n - c) / (c - 1)`. -/
noncomputable def closed_form (c : ℝ) (n : ℕ) : ℝ := (c ^ n - c) / (c - 1)

theorem Sigma_succ (T : ℕ → ℝ) (m : ℕ) : Sigma T (m + 2) = Sigma T (m + 1) + T (m + 1) := by
  unfold Sigma
  simp [Finset.sum_Icc_succ_top]

theorem divfree (c : ℝ) (n : ℕ) (hn : 1 ≤ n) : (c - 1) * Sigma (fun k => c ^ k) n = c ^ n - c := by
  obtain ⟨m, rfl⟩ : ∃ m, n = m + 1 := ⟨n - 1, by omega⟩
  clear hn
  induction m with
  | zero => simp [Sigma]
  | succ m ih =>
    rw [Sigma_succ, mul_add, ih]
    ring

theorem universal : ∀ (c : ℝ) (n : ℕ), c ≠ 1 → 1 ≤ n → Sigma (fun k => c ^ k) n = closed_form c n := by
  intro c n hc hn
  have h := divfree c n hn
  have hc' : c - 1 ≠ 0 := sub_ne_zero.mpr hc
  unfold closed_form
  rw [eq_div_iff hc', mul_comm]
  exact h

end SE_cs_13118_a13122_explanation_real.Ref
