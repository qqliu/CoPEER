import Mathlib.Geometry.Euclidean.Angle.Unoriented.Affine
import Mathlib.Analysis.InnerProductSpace.PiL2
import Mathlib.Tactic
namespace Arxiv150800060v3SourceEnrichedCodex
abbrev V := EuclideanSpace ℝ (Fin 2)
noncomputable def a : V := !₂[-1,0]
noncomputable def b : V := !₂[1,0]
noncomputable def p : V := !₂[0,1/2]
lemma dot_rays : inner ℝ (a-p) (b-p) = -3/4 := by
  norm_num [a,b,p,EuclideanSpace.inner_eq_star_dotProduct,dotProduct,Fin.sum_univ_succ]
lemma inside : ‖p‖ < 1 := by
  have h : ‖p‖^2 = (1/4:ℝ) := by
    norm_num [EuclideanSpace.real_norm_sq_eq,p,Fin.sum_univ_succ]
  nlinarith [norm_nonneg p]
theorem refutes_inside_diametral_circle_implies_acute_angle :
    a + b = 0 ∧ ‖a‖ = 1 ∧ ‖b‖ = 1 ∧ ‖p‖ < 1 ∧
    ¬ EuclideanGeometry.angle a p b < Real.pi/2 := by
  have ha : ‖a‖^2 = (1:ℝ) := by
    norm_num [EuclideanSpace.real_norm_sq_eq,a,Fin.sum_univ_succ]
  have hb : ‖b‖^2 = (1:ℝ) := by
    norm_num [EuclideanSpace.real_norm_sq_eq,b,Fin.sum_univ_succ]
  refine ⟨?_,by nlinarith [norm_nonneg a],by nlinarith [norm_nonneg b],inside,?_⟩
  · ext i
    fin_cases i <;> norm_num [a,b]
  · intro h
    change InnerProductGeometry.angle (a-p) (b-p) < Real.pi/2 at h
    rw [InnerProductGeometry.angle,Real.arccos_lt_pi_div_two,dot_rays] at h
    have hd : 0 ≤ ‖a-p‖ * ‖b-p‖ := mul_nonneg (norm_nonneg _) (norm_nonneg _)
    have hn : (-3/4:ℝ)/(‖a-p‖*‖b-p‖) ≤ 0 :=
      div_nonpos_of_nonpos_of_nonneg (by norm_num) hd
    linarith
end Arxiv150800060v3SourceEnrichedCodex
