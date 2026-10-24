import Mathlib.Probability.Distributions.Gaussian.Real
import Mathlib.Data.Matrix.Mul
import Mathlib.LinearAlgebra.Matrix.Trace
import Mathlib.Combinatorics.Enumerative.Catalan.Basic
import Mathlib.Tactic
open MeasureTheory ProbabilityTheory
open scoped NNReal
/-! Same source claim: Gaussian matrix trace moments equal Catalan numbers.
The old N=2,k=1 witness did not specify a consistent real-symmetric Gaussian
ensemble; its Wick counter merely assumed the desired moment. Use N=1,k=2,
where both the real-symmetric and Hermitian descriptions reduce to one centered
real Gaussian of variance one, as prescribed by the source's covariance. The
probability measure is the actual Mathlib gaussianReal 0 1. Its fourth moment
is proved from Mathlib's moment-generating-function derivative theorem, and
Matrix.trace and matrix powers are the actual library operations. The measure
is normalized, following the source's use of Gaussian expectation. -/
namespace MSE811862
noncomputable def mg (t : ℝ) := Real.exp (t^2/2)
noncomputable def d1 (t : ℝ) := t * mg t
noncomputable def d2 (t : ℝ) := (1+t^2) * mg t
noncomputable def d3 (t : ℝ) := (3*t+t^3) * mg t
noncomputable def d4 (t : ℝ) := (3+6*t^2+t^4) * mg t
lemma hd0 (t : ℝ) : HasDerivAt mg (d1 t) t := by
  unfold mg d1
  convert (Real.hasDerivAt_exp (t^2/2)).comp t (((hasDerivAt_id t).pow 2).div_const 2) using 1 <;> simp [mg] <;> ring
lemma hd1 (t : ℝ) : HasDerivAt d1 (d2 t) t := by
  convert (hasDerivAt_id t).mul (hd0 t) using 1 <;> simp [d1,d2] <;> ring
lemma hd2 (t : ℝ) : HasDerivAt d2 (d3 t) t := by
  convert ((hasDerivAt_const t (1:ℝ)).add ((hasDerivAt_id t).pow 2)).mul (hd0 t) using 1 <;> simp [d1,d2,d3] <;> ring
lemma hd3 (t : ℝ) : HasDerivAt d3 (d4 t) t := by
  convert (((hasDerivAt_id t).const_mul 3).add ((hasDerivAt_id t).pow 3)).mul (hd0 t) using 1 <;> simp [d1,d3,d4] <;> ring
lemma fourth_moment : (∫ x : ℝ, x^4 ∂gaussianReal 0 1) = 3 := by
  change (∫ x : ℝ, ((fun z : ℝ => z)^4) x ∂gaussianReal 0 1) = 3
  rw [← iteratedDeriv_mgf_zero (by simp)]
  rw [mgf_fun_id_gaussianReal]
  simp only [zero_mul, NNReal.coe_one, one_mul, zero_add]
  change iteratedDeriv 4 mg 0 = 3
  have h0 : deriv mg = d1 := funext (fun t => (hd0 t).deriv)
  have h1 : deriv d1 = d2 := funext (fun t => (hd1 t).deriv)
  have h2 : deriv d2 = d3 := funext (fun t => (hd2 t).deriv)
  have h3 : deriv d3 = d4 := funext (fun t => (hd3 t).deriv)
  norm_num [iteratedDeriv_succ,iteratedDeriv_zero,h0,h1,h2,h3,d4,mg]
lemma second_moment : (∫ x : ℝ, x^2 ∂gaussianReal 0 1) = 1 := by
  have h := variance_fun_id_gaussianReal (μ := (0 : ℝ)) (v := (1 : ℝ≥0))
  rw [variance_eq_integral measurable_id'.aemeasurable] at h
  simpa using h

def scalarMatrix (x : ℝ) : Matrix (Fin 1) (Fin 1) ℝ := fun _ _ => x
lemma trace_fourth (x : ℝ) : Matrix.trace ((scalarMatrix x)^4) = x^4 := by
  simp [scalarMatrix, Matrix.trace, pow_succ, Matrix.mul_apply, Fin.sum_univ_one]
lemma trace_second (x : ℝ) : Matrix.trace ((scalarMatrix x)^2) = x^2 := by
  simp [scalarMatrix, Matrix.trace, pow_succ, Matrix.mul_apply, Fin.sum_univ_one]

theorem certificate :
    (∀ x : ℝ, (scalarMatrix x).IsSymm) ∧
    (∫ x : ℝ, x ∂gaussianReal 0 1) = 0 ∧
    (∫ x : ℝ, Matrix.trace ((scalarMatrix x)^2) ∂gaussianReal 0 1) = 1 ∧
    (∫ x : ℝ, Matrix.trace ((scalarMatrix x)^4) ∂gaussianReal 0 1) = 3 ∧
    catalan 2 = 2 ∧
    (∫ x : ℝ, Matrix.trace ((scalarMatrix x)^4) ∂gaussianReal 0 1) ≠ (catalan 2 : ℝ) := by
  have hs : ∀ x : ℝ, (scalarMatrix x).IsSymm := by intro x; rfl
  simpa [trace_fourth,trace_second,fourth_moment,second_moment,catalan_two] using hs
end MSE811862
