import Mathlib.Probability.ProbabilityMassFunction.Binomial
import Mathlib.Tactic.NormNum
set_option autoImplicit false
open scoped ENNReal NNReal
namespace ProofCerts.Alg1
noncomputable def coinLaw : PMF (Fin 5) := PMF.binomial (1/4) (by rw [div_le_iff₀ (by norm_num)]; norm_num) 4
noncomputable def Pleft : ℝ := (coinLaw.toMeasure {k | (k.val : ℝ) ≤ 1 / 2}).toReal
noncomputable def Pright : ℝ := (coinLaw.toMeasure {k | (4 : ℝ) - k.val ≥ 9 / 2}).toReal
theorem left_event : {k : Fin 5 | (k.val : ℝ) ≤ 1 / 2} = {0} := by
  ext k
  fin_cases k <;> norm_num

theorem right_event : {k : Fin 5 | (4 : ℝ) - k.val ≥ 9 / 2} = ∅ := by
  ext k
  fin_cases k <;> norm_num

theorem Pleft_eq : Pleft = 81 / 256 := by
  rw [Pleft, left_event, PMF.toMeasure_apply_singleton _ _ (measurableSet_singleton _)]
  simp only [coinLaw, PMF.binomial_apply_zero]
  norm_num [ENNReal.toReal_sub_of_le]
theorem Pright_eq : Pright = 0 := by rw [Pright, right_event]; simp
theorem prob_identity_fails_kernel : Pleft ≠ Pright := by
  rw [Pleft_eq, Pright_eq]
  norm_num
end ProofCerts.Alg1
#print axioms ProofCerts.Alg1.prob_identity_fails_kernel
