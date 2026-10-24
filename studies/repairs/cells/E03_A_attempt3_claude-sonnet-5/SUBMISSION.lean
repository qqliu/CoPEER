import defs_only
/-!
Record E03: correction template.
Fill the ONE hole `«HOLE»` in the FIXED PART (nothing else in the fixed part may change), then prove
the OBLIGATIONS below with exactly these names and statements. Helper lemmas may be added between the
fixed part and the obligations, inside the namespace. Import nothing else.
-/
namespace SE_cs_13118_a13122_explanation_real

-- ===== FIXED PART: only the hole «HOLE» may be edited =====
/-- The corrected closed form for `Sigma (fun k => c ^ k) n` on the source's domain `c ≠ 1`, `1 ≤ n`.
The hole must be a closed expression in `c` and `n` built from field operations and powers: no sums,
no `Sigma`, no `Finset`, no `if`/`match`. -/
noncomputable def closed_form (c : ℝ) (n : ℕ) : ℝ := (c ^ n - c) / (c - 1)

/-- The corrected located line on the source's domain (shape fixed). -/
def CorrectedClaim : Prop :=
  ∀ (c : ℝ) (n : ℕ), c ≠ 1 → 1 ≤ n → Sigma (fun k => c ^ k) n = closed_form c n
-- ===== END FIXED PART =====

theorem sum_Icc_geom (c : ℝ) (hc : c ≠ 1) : ∀ m : ℕ,
    Sigma (fun k => c ^ k) (m + 1) = closed_form c (m + 1) := by
  intro m
  induction m with
  | zero =>
      simp [Sigma, closed_form]
  | succ m ih =>
      have hIcc : Finset.Icc 1 ((m + 1 + 1) - 1) = insert (m + 1) (Finset.Icc 1 ((m + 1) - 1)) := by
        have h1 : (m + 1 + 1) - 1 = m + 1 := by omega
        have h2 : (m + 1) - 1 = m := by omega
        rw [h1, h2]
        ext x
        simp only [Finset.mem_Icc, Finset.mem_insert]
        omega
      have hSigma : Sigma (fun k => c ^ k) (m + 1 + 1)
          = c ^ (m + 1) + Sigma (fun k => c ^ k) (m + 1) := by
        unfold Sigma
        rw [hIcc]
        rw [Finset.sum_insert]
        simp only [Finset.mem_Icc]
        omega
      rw [hSigma, ih]
      have hne : c - 1 ≠ 0 := sub_ne_zero.mpr hc
      unfold closed_form
      field_simp
      ring

theorem repair_statement : ∀ (c : ℝ) (n : ℕ), c ≠ 1 → 1 ≤ n → SE_cs_13118_a13122_explanation_real.Sigma (fun k => c ^ k) n = SE_cs_13118_a13122_explanation_real.closed_form c n := by
  intro c n hc hn
  obtain ⟨m, rfl⟩ := Nat.exists_eq_add_of_le' hn
  exact sum_Icc_geom c hc m

theorem repair_nonvacuous : ∃ (c : ℝ) (n : ℕ), c ≠ 1 ∧ 1 ≤ n ∧ SE_cs_13118_a13122_explanation_real.Sigma (fun k => c ^ k) n = SE_cs_13118_a13122_explanation_real.closed_form c n ∧ SE_cs_13118_a13122_explanation_real.closed_form c n ≠ (c ^ n - 1) / (c - 1) := by
  refine ⟨2, 3, by norm_num, by norm_num, ?_, ?_⟩
  · exact sum_Icc_geom 2 (by norm_num) 2
  · unfold closed_form
    norm_num

theorem final_theorem : ∀ (c : ℝ) (n : ℕ), c ≠ 1 → 1 ≤ n → SE_cs_13118_a13122_explanation_real.Sigma (fun k => c ^ k) n = SE_cs_13118_a13122_explanation_real.closed_form c n := repair_statement

end SE_cs_13118_a13122_explanation_real
