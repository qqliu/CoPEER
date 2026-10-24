import Mathlib.Analysis.SpecialFunctions.Integrals.PosLogEqCircleAverage
import Mathlib.Analysis.Analytic.Order
import Mathlib.Tactic.NormNum
import Mathlib.Tactic.Linarith

/-!
# g3ref-pnv-367: Jensen's radius must match the zero-count integral

Source: `qedbench_certificate_availability_triage/runs/g3refs_claim_contexts/g3ref-pnv-367.txt`.
The source equates the integral through 1 with boundary data at an arbitrary
radius R < 1. Its printed exponential also contains the constant π where a
circle parameter φ would be expected. These are distinguished below.

The original witness is retained: f(z) = z - 1/2 and R = 3/4. Mathlib proves
analyticity, boundedness, the unique simple zero, the actual real integrals,
and the actual circle average. No rational logarithm or integral surrogate
is used. The stored witness counts zeros in a closed disk; the source says
open disk. Both counts are tied to their exact zero sets, and their weighted
integrals agree because the counts differ only at the radius 1/2.

The full integral is log 2. The intended circle-boundary expression is
log(3/2); the literal printed constant-angle expression is log(5/2). Both
differ from log 2. Replacing the upper integration limit by R gives the
intended circle-boundary expression. This challenges the displayed proof
step, not the Blaschke convergence theorem, which the witness satisfies.
-/

namespace G3refPnv367

open MeasureTheory Metric Set Real

noncomputable def witnessF (z : ℂ) : ℂ := z - 1 / 2

noncomputable def witnessR : ℝ := 3 / 4

/-- The original witness's closed-disk counting convention. -/
noncomputable def witnessZeroCount (r : ℝ) : ℝ := if 1 / 2 ≤ r then 1 else 0

/-- The source's open-disk counting convention. -/
noncomputable def sourceZeroCount (r : ℝ) : ℝ := if 1 / 2 < r then 1 else 0

noncomputable def zerosInClosedDisk (r : ℝ) : Finset ℂ := by
  classical
  exact ({(1 / 2 : ℂ)} : Finset ℂ).filter (fun z => ‖z‖ ≤ r)

noncomputable def zerosInOpenDisk (r : ℝ) : Finset ℂ := by
  classical
  exact ({(1 / 2 : ℂ)} : Finset ℂ).filter (fun z => ‖z‖ < r)

theorem witness_analytic : AnalyticOnNhd ℂ witnessF Set.univ := by
  intro z _
  unfold witnessF
  fun_prop

theorem witness_derivative (z : ℂ) : HasDerivAt witnessF 1 z := by
  exact (hasDerivAt_id z).sub_const (1 / 2 : ℂ)

theorem witness_unique_zero (z : ℂ) : witnessF z = 0 ↔ z = 1 / 2 := by
  simp [witnessF, sub_eq_zero]

theorem witness_simple_zero : analyticOrderAt witnessF (1 / 2) = 1 := by
  apply AnalyticAt.analyticOrderAt_eq_one_of_zero_deriv_ne_zero
  · exact witness_analytic _ (Set.mem_univ _)
  · simp [witnessF]
  · rw [(witness_derivative _).deriv]
    exact one_ne_zero

theorem witness_nonzero_at_origin : witnessF 0 ≠ 0 := by
  norm_num [witnessF]

theorem witness_origin_norm : ‖witnessF 0‖ = (1 / 2 : ℝ) := by
  norm_num [witnessF]

theorem witness_bounded_on_unit_disk (z : ℂ) (hz : ‖z‖ < 1) :
    ‖witnessF z‖ ≤ (3 / 2 : ℝ) := by
  calc ‖witnessF z‖ ≤ ‖z‖ + ‖(1 / 2 : ℂ)‖ := norm_sub_le _ _
  _ ≤ 3 / 2 := by norm_num at *; linarith

theorem mem_zerosInClosedDisk (r : ℝ) (z : ℂ) :
    z ∈ zerosInClosedDisk r ↔ witnessF z = 0 ∧ ‖z‖ ≤ r := by
  classical
  simp [zerosInClosedDisk, witnessF, sub_eq_zero]

theorem mem_zerosInOpenDisk (r : ℝ) (z : ℂ) :
    z ∈ zerosInOpenDisk r ↔ witnessF z = 0 ∧ ‖z‖ < r := by
  classical
  simp [zerosInOpenDisk, witnessF, sub_eq_zero]

/-- Together with the unique-zero and simple-zero theorems, this is the
original count with multiplicity, expressed using Mathlib finite sets. -/
theorem witnessZeroCount_card (r : ℝ) :
    witnessZeroCount r = ((zerosInClosedDisk r).card : ℝ) := by
  classical
  simp only [zerosInClosedDisk, Finset.filter_singleton, norm_div, norm_one,
    Complex.norm_ofNat, witnessZeroCount]
  split_ifs <;> simp

theorem sourceZeroCount_card (r : ℝ) :
    sourceZeroCount r = ((zerosInOpenDisk r).card : ℝ) := by
  classical
  simp only [zerosInOpenDisk, Finset.filter_singleton, norm_div, norm_one,
    Complex.norm_ofNat, sourceZeroCount]
  split_ifs <;> simp

/-- A singleton endpoint difference cannot change the real integral. -/
theorem closed_open_integrals_equal (u : ℝ) :
    (∫ r in (0 : ℝ)..u, witnessZeroCount r / r) =
      ∫ r in (0 : ℝ)..u, sourceZeroCount r / r := by
  apply intervalIntegral.integral_congr_ae
  filter_upwards [volume.ae_ne (1 / 2 : ℝ)] with r hr
  intro _
  have h : (1 / 2 : ℝ) ≤ r ↔ 1 / 2 < r := by
    constructor
    · intro h
      exact lt_of_le_of_ne h (Ne.symm hr)
    · exact le_of_lt
  simp only [witnessZeroCount, sourceZeroCount, h]

/-- This is a Bochner interval integral of the actual zero-count function. -/
theorem sourceZeroCount_integral (u : ℝ) (hu : (1 / 2 : ℝ) ≤ u) :
    (∫ r in (0 : ℝ)..u, sourceZeroCount r / r) = Real.log (u / (1 / 2)) := by
  have hz : (0 : ℝ) ≤ u := le_trans (by norm_num) hu
  have fun_eq : (fun r : ℝ => sourceZeroCount r / r) =
      Set.indicator (Set.Ioi (1 / 2)) (fun r => r⁻¹) := by
    funext r
    simp only [sourceZeroCount, Set.indicator, Set.mem_Ioi]
    split_ifs <;> simp
  rw [fun_eq, intervalIntegral.integral_of_le hz, integral_indicator measurableSet_Ioi,
    Measure.restrict_restrict measurableSet_Ioi, Set.inter_comm, Set.Ioc_inter_Ioi,
    max_eq_right (by norm_num : (0 : ℝ) ≤ 1 / 2), ← intervalIntegral.integral_of_le hu]
  exact integral_inv_of_pos (by norm_num) (lt_of_lt_of_le (by norm_num) hu)

theorem witnessZeroCount_integral (u : ℝ) (hu : (1 / 2 : ℝ) ≤ u) :
    (∫ r in (0 : ℝ)..u, witnessZeroCount r / r) = Real.log (u / (1 / 2)) := by
  rw [closed_open_integrals_equal, sourceZeroCount_integral u hu]

theorem full_unit_integral :
    (∫ r in (0 : ℝ)..1, witnessZeroCount r / r) = Real.log 2 := by
  rw [witnessZeroCount_integral 1 (by norm_num)]
  norm_num

theorem actual_circle_average :
    circleAverage (fun z : ℂ => Real.log ‖witnessF z‖) 0 witnessR = Real.log (3 / 4) := by
  apply circleAverage_log_norm_sub_const_of_mem_closedBall
  norm_num [witnessR, Metric.mem_closedBall, dist_eq_norm, norm_div, Complex.norm_ofNat]

/-- The intended rotating-boundary reading, using Mathlib's circle average. -/
noncomputable def intendedBoundaryExpression : ℝ :=
  circleAverage (fun z : ℂ => Real.log ‖witnessF z‖) 0 witnessR - Real.log ‖witnessF 0‖

/-- The library average is exactly the rotating-angle integral that the
surrounding Jensen argument intends, with φ in the exponential. -/
theorem intended_boundary_as_angle_integral :
    intendedBoundaryExpression =
      (1 / (2 * Real.pi)) *
        (∫ φ in (0 : ℝ)..(2 * Real.pi),
          Real.log ‖witnessF ((witnessR : ℂ) * Complex.exp (Complex.I * φ))‖)
        - Real.log ‖witnessF 0‖ := by
  simp only [intendedBoundaryExpression, circleAverage_def, circleMap,
    zero_add, smul_eq_mul, one_div, mul_comm Complex.I]

theorem intended_boundary_value : intendedBoundaryExpression = Real.log (3 / 2) := by
  rw [intendedBoundaryExpression, actual_circle_average, witness_origin_norm,
    ← Real.log_div (by norm_num) (by norm_num)]
  norm_num

/-- The source as literally printed has a constant exponential `exp(iπ)`. -/
noncomputable def literalBoundaryExpression : ℝ :=
  (1 / (2 * Real.pi)) *
    (∫ _φ in (0 : ℝ)..(2 * Real.pi),
      Real.log ‖witnessF ((witnessR : ℂ) * Complex.exp (Complex.I * Real.pi))‖)
    - Real.log ‖witnessF 0‖

theorem literal_boundary_value : literalBoundaryExpression = Real.log (5 / 2) := by
  have hn : ‖witnessF ((witnessR : ℂ) * Complex.exp (Complex.I * Real.pi))‖ =
      (5 / 4 : ℝ) := by
    rw [mul_comm Complex.I, Complex.exp_pi_mul_I]
    norm_num [witnessF, witnessR]
  rw [literalBoundaryExpression, hn, intervalIntegral.integral_const, witness_origin_norm]
  simp only [sub_zero, smul_eq_mul]
  have hpi : (2 * Real.pi : ℝ) ≠ 0 := mul_ne_zero (by norm_num) (ne_of_gt Real.pi_pos)
  rw [← mul_assoc, one_div_mul_cancel hpi, one_mul,
    ← Real.log_div (by norm_num) (by norm_num)]
  norm_num

theorem intended_equality_false :
    (∫ r in (0 : ℝ)..1, witnessZeroCount r / r) ≠ intendedBoundaryExpression := by
  rw [full_unit_integral, intended_boundary_value]
  exact ne_of_gt (Real.strictMonoOn_log (by norm_num) (by norm_num) (by norm_num))

theorem literal_equality_false :
    (∫ r in (0 : ℝ)..1, sourceZeroCount r / r) ≠ literalBoundaryExpression := by
  rw [sourceZeroCount_integral 1 (by norm_num), literal_boundary_value]
  norm_num only [div_one, one_div, inv_inv]
  exact ne_of_lt (Real.strictMonoOn_log (by norm_num) (by norm_num) (by norm_num))

/-- All hypotheses and the zero-count interpretation accompany the actual
analytic mismatch. The simple-zero order proves that counting this sole zero
once agrees with counting multiplicity. No original witness is replaced. -/
theorem refutes_radius_R_boundary_for_full_unit_integral :
    AnalyticOnNhd ℂ witnessF Set.univ ∧
    (∀ z : ℂ, ‖z‖ < 1 → ‖witnessF z‖ ≤ (3 / 2 : ℝ)) ∧
    witnessF 0 ≠ 0 ∧
    (∀ z : ℂ, witnessF z = 0 ↔ z = 1 / 2) ∧
    analyticOrderAt witnessF (1 / 2) = 1 ∧
    (∀ r z, z ∈ zerosInClosedDisk r ↔ witnessF z = 0 ∧ ‖z‖ ≤ r) ∧
    (∀ r z, z ∈ zerosInOpenDisk r ↔ witnessF z = 0 ∧ ‖z‖ < r) ∧
    (∀ r, witnessZeroCount r = ((zerosInClosedDisk r).card : ℝ)) ∧
    (∀ r, sourceZeroCount r = ((zerosInOpenDisk r).card : ℝ)) ∧
    (1 / 2 : ℝ) < witnessR ∧ witnessR < 1 ∧
    (∫ r in (0 : ℝ)..1, witnessZeroCount r / r) = Real.log 2 ∧
    intendedBoundaryExpression = Real.log (3 / 2) ∧
    literalBoundaryExpression = Real.log (5 / 2) ∧
    (∫ r in (0 : ℝ)..1, witnessZeroCount r / r) ≠ intendedBoundaryExpression ∧
    (∫ r in (0 : ℝ)..1, sourceZeroCount r / r) ≠ literalBoundaryExpression := by
  exact ⟨witness_analytic, witness_bounded_on_unit_disk, witness_nonzero_at_origin,
    witness_unique_zero, witness_simple_zero, mem_zerosInClosedDisk, mem_zerosInOpenDisk,
    witnessZeroCount_card, sourceZeroCount_card, by norm_num [witnessR],
    by norm_num [witnessR], full_unit_integral, intended_boundary_value,
    literal_boundary_value, intended_equality_false, literal_equality_false⟩

/-- Fixing the disputed upper limit gives the actual Jensen circle average. -/
theorem negative_control_corrected_upper_limit_R :
    witnessR ≠ 1 ∧
    (∫ r in (0 : ℝ)..witnessR, witnessZeroCount r / r) = Real.log (3 / 2) ∧
    (∫ r in (0 : ℝ)..witnessR, witnessZeroCount r / r) = intendedBoundaryExpression := by
  have hi : (∫ r in (0 : ℝ)..witnessR, witnessZeroCount r / r) = Real.log (3 / 2) := by
    rw [witnessZeroCount_integral witnessR (by norm_num [witnessR])]
    norm_num [witnessR]
  exact ⟨by norm_num [witnessR], hi, hi.trans intended_boundary_value.symm⟩

end G3refPnv367
