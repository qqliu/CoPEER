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

theorem Sigma_succ (c : ℝ) (n : ℕ) (hn : 1 ≤ n) :
    Sigma (fun k => c ^ k) (n + 1) = Sigma (fun k => c ^ k) n + c ^ n := by
  have h1 : (n + 1) - 1 = n := by omega
  have h2 : n - 1 + 1 = n := by omega
  unfold Sigma
  rw [h1]
  conv_lhs => rw [← h2]
  rw [Finset.sum_Icc_succ_top (by omega)]
  rw [h2]

theorem repair_statement : ∀ (c : ℝ) (n : ℕ), c ≠ 1 → 1 ≤ n → SE_cs_13118_a13122_explanation_real.Sigma (fun k => c ^ k) n = SE_cs_13118_a13122_explanation_real.closed_form c n := by
  intro c n hc hn
  induction n, hn using Nat.le_induction with
  | base =>
    unfold Sigma closed_form
    norm_num
  | succ n hn ih =>
    rw [Sigma_succ c n hn, ih]
    have hc1 : c - 1 ≠ 0 := sub_ne_zero.mpr hc
    unfold closed_form
    field_simp
    ring

theorem repair_nonvacuous : ∃ (c : ℝ) (n : ℕ), c ≠ 1 ∧ 1 ≤ n ∧ SE_cs_13118_a13122_explanation_real.Sigma (fun k => c ^ k) n = SE_cs_13118_a13122_explanation_real.closed_form c n ∧ SE_cs_13118_a13122_explanation_real.closed_form c n ≠ (c ^ n - 1) / (c - 1) := by
  refine ⟨2, 1, ?_, ?_, ?_, ?_⟩
  · norm_num
  · norm_num
  · exact repair_statement 2 1 (by norm_num) (by norm_num)
  · unfold closed_form
    norm_num

theorem final_theorem : ∀ (c : ℝ) (n : ℕ), c ≠ 1 → 1 ≤ n → SE_cs_13118_a13122_explanation_real.Sigma (fun k => c ^ k) n = SE_cs_13118_a13122_explanation_real.closed_form c n := repair_statement

end SE_cs_13118_a13122_explanation_real
