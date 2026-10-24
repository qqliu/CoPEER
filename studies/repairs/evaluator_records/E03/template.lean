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
noncomputable def closed_form (c : ℝ) (n : ℕ) : ℝ := «HOLE»

/-- The corrected located line on the source's domain (shape fixed). -/
def CorrectedClaim : Prop :=
  ∀ (c : ℝ) (n : ℕ), c ≠ 1 → 1 ≤ n → Sigma (fun k => c ^ k) n = closed_form c n
-- ===== END FIXED PART =====

-- ===== OBLIGATIONS: keep the names and statements; replace each `sorry` by a proof =====
/-- Universal: the corrected identity on the source's whole domain. -/
theorem repair_statement : ∀ (c : ℝ) (n : ℕ), c ≠ 1 → 1 ≤ n → SE_cs_13118_a13122_explanation_real.Sigma (fun k => c ^ k) n = SE_cs_13118_a13122_explanation_real.closed_form c n := sorry

/-- Non-vacuity: the domain has a point, the corrected identity holds there, and the corrected closed form
differs from the source's `(c ^ n - 1) / (c - 1)` there. -/
theorem repair_nonvacuous : ∃ (c : ℝ) (n : ℕ), c ≠ 1 ∧ 1 ≤ n ∧ SE_cs_13118_a13122_explanation_real.Sigma (fun k => c ^ k) n = SE_cs_13118_a13122_explanation_real.closed_form c n ∧ SE_cs_13118_a13122_explanation_real.closed_form c n ≠ (c ^ n - 1) / (c - 1) := sorry

/-- The endpoint of this record is the corrected universal statement itself; restate it here, e.g.
`:= repair_statement`. If you cannot, replace this declaration (this doc comment included) by the single
line `-- CANNOT: <reason>`. -/
theorem final_theorem : ∀ (c : ℝ) (n : ℕ), c ≠ 1 → 1 ≤ n → SE_cs_13118_a13122_explanation_real.Sigma (fun k => c ^ k) n = SE_cs_13118_a13122_explanation_real.closed_form c n := sorry
-- ===== END OBLIGATIONS =====
end SE_cs_13118_a13122_explanation_real
