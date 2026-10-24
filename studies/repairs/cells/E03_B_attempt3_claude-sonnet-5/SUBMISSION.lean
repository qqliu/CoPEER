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

theorem repair_statement : ∀ (c : ℝ) (n : ℕ), c ≠ 1 → 1 ≤ n → SE_cs_13118_a13122_explanation_real.Sigma (fun k => c ^ k) n = SE_cs_13118_a13122_explanation_real.closed_form c n := by
  intro c n hc hn
  unfold SE_cs_13118_a13122_explanation_real.Sigma SE_cs_13118_a13122_explanation_real.closed_form
  have hcm1 : c - 1 ≠ 0 := sub_ne_zero.mpr hc
  induction n with
  | zero => omega
  | succ m ih =>
    rcases Nat.eq_zero_or_pos m with hm0 | hmpos
    · subst hm0
      simp
    · have hm1 : 1 ≤ m := hmpos
      have hsucc_sub : (m + 1) - 1 = m := by omega
      have hm_sub : m - 1 + 1 = m := by omega
      rw [hsucc_sub]
      have step := Finset.sum_Icc_succ_top (show 1 ≤ (m - 1) + 1 by omega) (fun k => c ^ k)
      rw [hm_sub] at step
      rw [step, ih hm1]
      field_simp
      ring

theorem repair_nonvacuous : ∃ (c : ℝ) (n : ℕ), c ≠ 1 ∧ 1 ≤ n ∧ SE_cs_13118_a13122_explanation_real.Sigma (fun k => c ^ k) n = SE_cs_13118_a13122_explanation_real.closed_form c n ∧ SE_cs_13118_a13122_explanation_real.closed_form c n ≠ (c ^ n - 1) / (c - 1) := by
  refine ⟨2, 3, by norm_num, by norm_num, ?_, ?_⟩
  · exact repair_statement 2 3 (by norm_num) (by norm_num)
  · unfold SE_cs_13118_a13122_explanation_real.closed_form
    norm_num

theorem final_theorem : ∀ (c : ℝ) (n : ℕ), c ≠ 1 → 1 ≤ n → SE_cs_13118_a13122_explanation_real.Sigma (fun k => c ^ k) n = SE_cs_13118_a13122_explanation_real.closed_form c n := repair_statement

end SE_cs_13118_a13122_explanation_real
