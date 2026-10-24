import Mathlib.MeasureTheory.Integral.IntervalIntegral.Periodic
import Mathlib.MeasureTheory.Function.L2Space
import Mathlib.MeasureTheory.Function.LpSeminorm.Indicator
import Mathlib.MeasureTheory.Integral.Bochner.Set
import Mathlib.Tactic
open MeasureTheory Set
namespace Arxiv151003522v1SourceEnrichedCodex
/-! Human-review repair. The domain is Mathlib's actual quotient torus ℝ/ℤ,
with its standard Lebesgue/Haar measure of total mass one. The half-open arc [0,1/3) has measure 1/3. The function is 1 on that arc and -1/2 outside.
Mathlib Bochner integrals give mean zero for u and -1/4 for u-u³; MemLp
constructs both as actual L² elements, so the final theorem checks membership
and failure of membership in the mean-zero subspace. No numerical quantity is
substituted for an integral. The original [0,1/3) witness is preserved exactly: the closed arc centered at 1/6
with radius 1/6 is [0,1/3], and its right endpoint is removed. -/
abbrev Torus := AddCircle (1:ℝ)
noncomputable def μ : Measure Torus := volume
noncomputable def region : Set Torus :=
  Metric.closedBall ((1/6:ℝ):Torus) (1/6:ℝ) \ {((1/3:ℝ):Torus)}

theorem region_measurable : MeasurableSet region :=
  measurableSet_closedBall.diff (measurableSet_singleton _)
instance : IsFiniteMeasure μ := by unfold μ; infer_instance
noncomputable def u (x : Torus) : ℝ :=
  region.indicator (fun _ => (3/2:ℝ)) x - 1/2
noncomputable def drift (x : Torus) : ℝ := u x - u x ^ 3

theorem u_memLp : MemLp u 2 μ :=
  ((memLp_const (3/2:ℝ)).indicator region_measurable).sub (memLp_const (1/2:ℝ))

theorem drift_formula : drift = fun x =>
    region.indicator (fun _ => (3/8:ℝ)) x - 3/8 := by
  funext x
  by_cases hx : x ∈ region
  · simp only [drift, u, Set.indicator_of_mem hx]
    norm_num
  · simp only [drift, u, Set.indicator_of_notMem hx]
    norm_num

theorem drift_memLp : MemLp drift 2 μ := by
  rw [drift_formula]
  exact ((memLp_const (3/8:ℝ)).indicator region_measurable).sub (memLp_const (3/8:ℝ))


theorem integral_indicator (c : ℝ) :
    ∫ x, region.indicator (fun _ => c) x ∂μ = (1/3)*c := by
  rw [MeasureTheory.integral_indicator region_measurable]
  rw [MeasureTheory.setIntegral_const]
  have hvol : volume region = ENNReal.ofReal (1/3:ℝ) := by
    have hz : volume ({((1/3:ℝ):Torus)} : Set Torus) = 0 := by
      rw [← Metric.closedBall_zero (x := ((1/3:ℝ):Torus)), AddCircle.volume_closedBall]
      norm_num
    rw [region, measure_diff_null hz]
    norm_num [AddCircle.volume_closedBall]
  norm_num [μ,Measure.real,hvol]

theorem integral_u : ∫ x, u x ∂μ = 0 := by
  rw [show u = (fun x => region.indicator (fun _ => (3/2:ℝ)) x - 1/2) from rfl]
  rw [integral_sub]
  · rw [integral_indicator,integral_const]
    norm_num [μ,Measure.real,AddCircle.measure_univ]
  · exact (integrable_const (3/2:ℝ)).indicator region_measurable
  · exact integrable_const (1/2:ℝ)

theorem integral_drift : ∫ x, drift x ∂μ = -1/4 := by
  rw [drift_formula,integral_sub]
  · rw [integral_indicator,integral_const]
    norm_num [μ,Measure.real,AddCircle.measure_univ]
  · exact (integrable_const (3/8:ℝ)).indicator region_measurable
  · exact integrable_const (3/8:ℝ)

noncomputable def uL2 : Lp ℝ 2 μ := u_memLp.toLp u
noncomputable def driftL2 : Lp ℝ 2 μ := drift_memLp.toLp drift
def H : Set (Lp ℝ 2 μ) := {f | ∫ x, f x ∂μ = 0}

theorem uL2_mem_H : uL2 ∈ H := by
  change (∫ x, uL2 x ∂μ) = 0
  exact (integral_congr_ae u_memLp.coeFn_toLp).trans integral_u

theorem driftL2_not_mem_H : driftL2 ∉ H := by
  change ¬ (∫ x, driftL2 x ∂μ) = 0
  unfold driftL2
  rw [integral_congr_ae drift_memLp.coeFn_toLp, integral_drift]
  norm_num

theorem cube_memLp : MemLp (fun x => u x ^ 3) 2 μ := by
  have h := u_memLp.sub drift_memLp
  change MemLp (fun x => u x - drift x) 2 μ at h
  have heq : (fun x => u x - drift x) = (fun x => u x ^ 3) := by
    funext x
    simp [drift]
  rwa [heq] at h

/-- The actual mean-zero subspace of the Hilbert space L²(T) is not closed
under the pointwise unprojected cubic drift, even for bounded inputs. -/
theorem refutes_unprojected_cubic_drift_closure :
    MemLp u 2 μ ∧ MemLp (fun x => u x ^ 3) 2 μ ∧
    MemLp drift 2 μ ∧ uL2 ∈ H ∧ driftL2 ∉ H ∧
    (∫ x, u x ∂μ) = 0 ∧ (∫ x, drift x ∂μ) = -1/4 ∧
    ¬ (∀ f : Torus → ℝ, MemLp f 2 μ →
      MemLp (fun x => f x ^ 3) 2 μ →
      (∫ x, f x ∂μ) = 0 → (∫ x, (f x - f x ^ 3) ∂μ) = 0) := by
  refine ⟨u_memLp, cube_memLp, drift_memLp, uL2_mem_H,
    driftL2_not_mem_H, integral_u, integral_drift, ?_⟩
  intro h
  have hz := h u u_memLp cube_memLp integral_u
  change (∫ x, drift x ∂μ) = 0 at hz
  rw [integral_drift] at hz
  norm_num at hz
end Arxiv151003522v1SourceEnrichedCodex
