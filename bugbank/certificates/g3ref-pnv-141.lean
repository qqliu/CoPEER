import Mathlib
open Set MeasureTheory
/-! Original witness preserved; standard Mathlib mathematical objects. Local proof-step counterexample. -/
namespace G3refPnv141
noncomputable def integrand (x : ℝ) : ℝ := 1 / (x * Real.log x)
lemma continuous_integrand : ContinuousOn integrand (Icc 2 4) := by
  apply continuousOn_const.div (continuousOn_id.mul ?_) ?_
  · apply Real.continuousOn_log.mono
    intro x hx
    simp only [mem_compl_iff, mem_singleton_iff]
    linarith [hx.1]
  · intro x hx
    exact mul_ne_zero (by change x ≠ 0; linarith [hx.1]) (ne_of_gt (Real.log_pos (by linarith [hx.1])))
theorem refutes_displayed_antiderivative_at_c_eq_one :
    ContinuousOn integrand (Icc 2 4) ∧
    0 < (∫ x in (2 : ℝ)..4, integrand x) ∧
    (∫ x in (2 : ℝ)..4, integrand x) ≠
      (Real.log 4 ^ (1 - (1 : ℝ))) / (1-1) -
      (Real.log 2 ^ (1 - (1 : ℝ))) / (1-1) := by
  have hp : 0 < (∫ x in (2 : ℝ)..4, integrand x) := by
    apply intervalIntegral.intervalIntegral_pos_of_pos_on
      (continuous_integrand.intervalIntegrable_of_Icc (by norm_num)) _ (by norm_num)
    intro x hx
    apply one_div_pos.mpr
    exact mul_pos (by linarith [hx.1]) (Real.log_pos (by linarith [hx.1]))
  refine ⟨continuous_integrand, hp, ?_⟩
  simpa using ne_of_gt hp
end G3refPnv141
