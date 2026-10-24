import Mathlib
/-! Original four equiprobable outcomes and events, with an actual Mathlib
probability measure and conditional probability. Labels shifted from
{1,2,3,4} to Fin4={0,1,2,3}; A={0},B={0,1}. -/
namespace ProofWiki137657CodexExpansion
open MeasureTheory ProbabilityTheory
open scoped NNReal ENNReal
abbrev Ω := Fin 4
noncomputable def μ : Measure Ω := (1 / 4 : ℝ≥0∞) •
  (Measure.dirac 0 + Measure.dirac 1 + Measure.dirac 2 + Measure.dirac 3)
def A : Set Ω := {0}
def B : Set Ω := {0,1}

lemma inv4 : (4 : ℝ≥0∞)⁻¹ = ↑((4 : ℝ≥0)⁻¹) :=
  (ENNReal.coe_inv (by norm_num : (4 : ℝ≥0) ≠ 0)).symm
lemma inv2 : (2 : ℝ≥0∞)⁻¹ = ↑((2 : ℝ≥0)⁻¹) :=
  (ENNReal.coe_inv (by norm_num : (2 : ℝ≥0) ≠ 0)).symm

instance : IsProbabilityMeasure μ := ⟨by
  norm_num [μ, Measure.smul_apply]
  rw [inv4, ← ENNReal.coe_add, ← ENNReal.coe_add, ← ENNReal.coe_add]
  norm_num⟩

theorem measure_B : μ B = 1/2 := by
  norm_num [μ, B, Measure.smul_apply, Measure.dirac_apply', Set.indicator_apply,
    show (2 : Ω) ≠ 0 by decide, show (2 : Ω) ≠ 1 by decide,
    show (3 : Ω) ≠ 0 by decide, show (3 : Ω) ≠ 1 by decide]
  rw [inv4,inv2,← ENNReal.coe_add]
  norm_num

theorem measure_inter : μ (B ∩ A) = 1/4 := by
  norm_num [μ, A, B, Measure.smul_apply, Measure.dirac_apply', Set.indicator_apply,
    Pi.single_apply, show (2 : Ω) ≠ 0 by decide, show (3 : Ω) ≠ 0 by decide]

theorem refutes_joint_as_conditional_probability :
    μ B > 0 ∧ μ (A ∩ B) = 1/4 ∧ μ[A | B] = 1/2 ∧ μ[A | B] ≠ μ (A ∩ B) := by
  have hcond : μ[A | B] = 1/2 := by
    rw [cond_apply (by measurability), measure_B, measure_inter]
    norm_num
    rw [inv4,inv2]
    norm_cast
    norm_num
  rw [Set.inter_comm A B, measure_B, measure_inter, hcond]
  norm_num
end ProofWiki137657CodexExpansion
