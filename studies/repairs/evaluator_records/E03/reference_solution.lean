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

-- ===== OBLIGATIONS: keep the names and statements; replace each `sorry` by a proof =====
/-- Universal: the corrected identity on the source's whole domain. -/
theorem repair_statement : ∀ (c : ℝ) (n : ℕ), c ≠ 1 → 1 ≤ n → SE_cs_13118_a13122_explanation_real.Sigma (fun k => c ^ k) n = SE_cs_13118_a13122_explanation_real.closed_form c n := by
  intro c n hc hn
  have h := divfree c n hn
  have hc' : c - 1 ≠ 0 := sub_ne_zero.mpr hc
  unfold closed_form
  rw [eq_div_iff hc', mul_comm]
  exact h

/-- Non-vacuity: the domain has a point, the corrected identity holds there, and the corrected closed form
differs from the source's `(c ^ n - 1) / (c - 1)` there. -/
theorem repair_nonvacuous : ∃ (c : ℝ) (n : ℕ), c ≠ 1 ∧ 1 ≤ n ∧ SE_cs_13118_a13122_explanation_real.Sigma (fun k => c ^ k) n = SE_cs_13118_a13122_explanation_real.closed_form c n ∧ SE_cs_13118_a13122_explanation_real.closed_form c n ≠ (c ^ n - 1) / (c - 1) := ⟨2, 3, by norm_num, by norm_num, repair_statement 2 3 (by norm_num) (by norm_num), by norm_num [closed_form]⟩

/-- The endpoint of this record is the corrected universal statement itself; restate it here, e.g.
`:= repair_statement`. If you cannot, replace this declaration (this doc comment included) by the single
line `-- CANNOT: <reason>`. -/
theorem final_theorem : ∀ (c : ℝ) (n : ℕ), c ≠ 1 → 1 ≤ n → SE_cs_13118_a13122_explanation_real.Sigma (fun k => c ^ k) n = SE_cs_13118_a13122_explanation_real.closed_form c n := repair_statement
-- ===== END OBLIGATIONS =====
end SE_cs_13118_a13122_explanation_real
