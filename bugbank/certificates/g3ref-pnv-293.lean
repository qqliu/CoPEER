import Mathlib
open Set MeasureTheory
/-! Original witness preserved; standard Mathlib mathematical objects. Local proof-step counterexample. -/
namespace G3refPnv293
 theorem refutes_constructed_interval_basis_membership :
    Real.sqrt 2 ∈ Ioo (Real.sqrt 2 - (1/10 : ℝ)) (Real.sqrt 2 + 1/10) ∧
    Ioo (Real.sqrt 2 - (1/10 : ℝ)) (Real.sqrt 2 + 1/10) ⊆ Ioo 1 2 ∧
    Irrational (Real.sqrt 2 - (1/10 : ℚ)) ∧
    Irrational (Real.sqrt 2 + (1/10 : ℚ)) := by
  have h0 := Real.sqrt_nonneg (2 : ℝ)
  have hsq := Real.sq_sqrt (show (0:ℝ) ≤ 2 by norm_num)
  have hlo : (7/5 : ℝ) < Real.sqrt 2 := by nlinarith
  have hhi : Real.sqrt 2 < (3/2 : ℝ) := by nlinarith
  refine ⟨⟨by linarith, by linarith⟩, ?_, irrational_sqrt_two.sub_ratCast _, irrational_sqrt_two.add_ratCast _⟩
  intro x hx
  constructor <;> linarith [hx.1,hx.2]
theorem not_rational_endpoint_basis_member :
    ¬ ∃ a b : ℚ, Ioo (Real.sqrt 2 - (1/10 : ℝ)) (Real.sqrt 2 + 1/10) =
      Ioo (a:ℝ) (b:ℝ) := by
  intro ⟨a,b,heq⟩
  have hlo : Real.sqrt 2 - (1/10 : ℝ) < Real.sqrt 2 + 1/10 := by linarith
  have hmem : Real.sqrt 2 ∈ Ioo (a:ℝ) (b:ℝ) := by
    rw [← heq]; constructor <;> linarith
  have hleft := ((Ioo_subset_Ioo_iff hlo).mp heq.subset).1
  have hright := ((Ioo_subset_Ioo_iff (lt_trans hmem.1 hmem.2)).mp heq.superset).1
  have ha : Real.sqrt 2 - (1/10 : ℝ) = (a:ℝ) := le_antisymm hright hleft
  have hir : Irrational (Real.sqrt 2 - (1/10 : ℚ)) := irrational_sqrt_two.sub_ratCast _
  have hc : ((1/10 : ℚ):ℝ) = (1/10 : ℝ) := by norm_num
  rw [hc,ha] at hir
  exact hir ⟨a,rfl⟩
end G3refPnv293
