import Mathlib.Probability.Distributions.Uniform
import Mathlib.Probability.ProbabilityMassFunction.Integrals
import Mathlib.Probability.Moments.Variance
import Mathlib.Probability.Independence.Basic
import Mathlib.Tactic.NormNum
import Mathlib.Tactic.Ring
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.NormNum.RealSqrt

/- The original witness is retained. The four outcomes now carry an actual
   product probability measure, and all moments are Mathlib integrals. -/
namespace Audit_reddit_mathematics_t3jogf
open MeasureTheory ProbabilityTheory
open scoped BigOperators
noncomputable def coin : Measure Bool := (PMF.uniformOfFintype Bool).toMeasure
instance : IsProbabilityMeasure coin := by unfold coin; infer_instance
noncomputable def μ : Measure (Bool × Bool) := coin.prod coin
instance : IsProbabilityMeasure μ := by unfold μ; infer_instance
noncomputable def X (w : Bool × Bool) : ℝ := if w.1 then 11/10 else 9/10
noncomputable def Y (w : Bool × Bool) : ℝ := if w.2 then 33/10 else 27/10
lemma atom (b : Bool) : coin {b} = 1/2 := by
  rw [coin, PMF.toMeasure_apply_singleton _ _ (MeasurableSet.singleton _)]
  norm_num [PMF.uniformOfFintype_apply]
lemma mass (w : Bool × Bool) : μ.real {w} = 1/4 := by
  rcases w with ⟨a,b⟩
  rw [measureReal_def, μ, ← Set.singleton_prod_singleton, Measure.prod_prod, atom, atom]
  norm_num
lemma integral_four (f : Bool × Bool → ℝ) : (∫ w, f w ∂μ) =
    (f (false,false)+f (false,true)+f (true,false)+f (true,true))/4 := by
  rw [integral_fintype .of_finite]
  simp only [mass, smul_eq_mul, Fintype.sum_prod_type, Fintype.sum_bool]
  ring
lemma variance_four (f : Bool × Bool → ℝ) : variance f μ =
    (((f (false,false)-(∫ w, f w ∂μ))^2 + (f (false,true)-(∫ w, f w ∂μ))^2 +
      (f (true,false)-(∫ w, f w ∂μ))^2 + (f (true,true)-(∫ w, f w ∂μ))^2)/4) := by
  rw [variance_eq_integral (measurable_of_countable f).aemeasurable, integral_four]
lemma moments : (∫ w, X w ∂μ) = 1 ∧ (∫ w, Y w ∂μ) = 3 ∧
    variance X μ = 1/100 ∧ variance Y μ = 9/100 ∧
    (∫ w, (X+Y) w ∂μ) = 4 ∧ variance (X+Y) μ = 1/10 := by
  norm_num [variance_four, integral_four, X,Y]
noncomputable def uncertainty (f : Bool × Bool → ℝ) := Real.sqrt (variance f μ)/(∫w,f w ∂μ)
theorem certificate : IndepFun X Y μ ∧
    (∫ w, X w ∂μ) = 1 ∧ (∫ w, Y w ∂μ) = 3 ∧
    uncertainty X = 1/10 ∧ uncertainty Y = 1/10 ∧
    uncertainty (X+Y) ≠ Real.sqrt ((uncertainty X)^2+(uncertainty Y)^2) := by
  have hI : IndepFun X Y μ := by
    exact indepFun_prod (μ := coin) (ν := coin)
      (measurable_of_countable (fun b : Bool => if b then (11/10 : ℝ) else 9/10))
      (measurable_of_countable (fun b : Bool => if b then (33/10 : ℝ) else 27/10))
  rcases moments with ⟨mx,my,vx,vy,mt,vt⟩
  have ux : uncertainty X = 1/10 := by norm_num [uncertainty,mx,vx]
  have uy : uncertainty Y = 1/10 := by norm_num [uncertainty,my,vy]
  refine ⟨hI,mx,my,ux,uy,?_⟩
  rw [ux,uy,uncertainty,vt,mt]
  intro h
  have hs := congrArg (fun t : ℝ => t^2) h
  have h1 := Real.sq_sqrt (show (0 : ℝ) ≤ 1/10 by norm_num)
  have h2 := Real.sq_sqrt (show (0 : ℝ) ≤ (1/10)^2+(1/10)^2 by norm_num)
  nlinarith
end Audit_reddit_mathematics_t3jogf
