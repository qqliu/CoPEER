import Mathlib.Analysis.InnerProductSpace.PiL2
import Mathlib.Geometry.Euclidean.Angle.Unoriented.Basic
import Mathlib.Tactic.Abel
import Mathlib.Tactic.NormNum
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.Ring
import Mathlib.Tactic.FinCases

/- Human-guided audit: Original rhombus of side5 dropped the source triangle dimensions. Replaced by source coordinates A=(0,0),B=(6√3,0),C=(−3√3,9),C′=−B,E=C−B. Source sides6√3,BC18 and cosine of120° are checked; ACEC′ is equal-sided but has nonright angle. Uses EuclideanSpace, norm, inner product and angle.
   Original witness action: REPLACED_INVALID. -/
namespace Audit_reddit_learnmath_egpgy9
open scoped RealInnerProductSpace
open InnerProductGeometry
noncomputable def b : EuclideanSpace ℝ (Fin 2) := WithLp.toLp 2 ![6*Real.sqrt 3,0]
noncomputable def c : EuclideanSpace ℝ (Fin 2) := WithLp.toLp 2 ![-3*Real.sqrt 3,9]
noncomputable def d : EuclideanSpace ℝ (Fin 2) := -b
noncomputable def e : EuclideanSpace ℝ (Fin 2) := c-b
lemma facts : ‖b‖ = 6*Real.sqrt 3 ∧ ‖c‖ = 6*Real.sqrt 3 ∧ ‖c-b‖ = 18 ∧
    ⟪b,c⟫ = -54 ∧ ⟪c,d⟫ = 54 := by
  have hs := Real.sq_sqrt (show (0 : ℝ) ≤ 3 by norm_num)
  have hp := Real.sqrt_nonneg (3 : ℝ)
  have ib : ⟪b,b⟫ = (6*Real.sqrt 3)^2 := by rw [EuclideanSpace.inner_eq_star_dotProduct]; simp [b, dotProduct, Fin.sum_univ_two]; ring
  have ic : ⟪c,c⟫ = (6*Real.sqrt 3)^2 := by
    rw [EuclideanSpace.inner_eq_star_dotProduct]; simp [c, dotProduct, Fin.sum_univ_two]; nlinarith
  have ie : ⟪c-b,c-b⟫ = (18 : ℝ)^2 := by
    rw [EuclideanSpace.inner_eq_star_dotProduct]; simp [b,c, dotProduct, Fin.sum_univ_two]; nlinarith
  refine ⟨?_,?_,?_,?_,?_⟩
  · have := real_inner_self_eq_norm_sq b; nlinarith [norm_nonneg b]
  · have := real_inner_self_eq_norm_sq c; nlinarith [norm_nonneg c]
  · have := real_inner_self_eq_norm_sq (c-b); nlinarith [norm_nonneg (c-b)]
  · rw [EuclideanSpace.inner_eq_star_dotProduct]; simp [b,c, dotProduct, Fin.sum_univ_two]; nlinarith
  · rw [EuclideanSpace.inner_eq_star_dotProduct]; simp [b,c,d, dotProduct, Fin.sum_univ_two]; nlinarith
theorem certificate_core : ‖b‖ = 6*Real.sqrt 3 ∧ ‖c‖ = 6*Real.sqrt 3 ∧ ‖c-b‖ = 18 ∧
    Real.cos (angle b c) = -(1/2 : ℝ) ∧
    ‖c‖ = ‖e-c‖ ∧ ‖e-c‖ = ‖d-e‖ ∧ ‖d-e‖ = ‖d‖ ∧
    angle c d ≠ Real.pi/2 := by
  rcases facts with ⟨hb,hc,hbc,hinner,hcd⟩
  refine ⟨hb,hc,hbc,?_,?_,?_,?_,?_⟩
  · rw [cos_angle, hb,hc,hinner]
    have hs := Real.sq_sqrt (show (0 : ℝ) ≤ 3 by norm_num)
    have hden : (6*Real.sqrt 3)*(6*Real.sqrt 3) = (108 : ℝ) := by nlinarith
    rw [hden]; norm_num
  · simpa [e, sub_sub_cancel_left, hc, hb]
  · have h1 : e-c = -b := by dsimp [e]; abel
    have h2 : d-e = -c := by dsimp [d,e]; abel
    rw [h1,h2,norm_neg,norm_neg,hb,hc]
  · have h2 : d-e = -c := by dsimp [d,e]; abel
    rw [h2, norm_neg, hc]
    simp only [d,norm_neg,hb]
  · intro h
    have hz := (inner_eq_zero_iff_angle_eq_pi_div_two c d).2 h
    rw [hcd] at hz; norm_num at hz
theorem certificate :
    angle b c = 2*Real.pi/3 ∧ ‖b‖ = 6*Real.sqrt 3 ∧ ‖c‖ = 6*Real.sqrt 3 ∧ ‖c-b‖ = 18 ∧
    ‖c‖ = ‖e-c‖ ∧ ‖e-c‖ = ‖d-e‖ ∧ ‖d-e‖ = ‖d‖ ∧ angle c d ≠ Real.pi/2 := by
  rcases certificate_core with ⟨hb,hc,hbc,hcos,hs1,hs2,hs3,hn⟩
  refine ⟨?_,hb,hc,hbc,hs1,hs2,hs3,hn⟩
  apply Real.injOn_cos ⟨angle_nonneg _ _, angle_le_pi _ _⟩
    ⟨by linarith [Real.pi_pos], by linarith [Real.pi_pos]⟩
  rw [hcos, show 2*Real.pi/3 = Real.pi-Real.pi/3 by ring, Real.cos_pi_sub, Real.cos_pi_div_three]
end Audit_reddit_learnmath_egpgy9
