import Mathlib
/-! The source constrains the angle to [0,π]. This witness has actual angle π/4
and inferred angle 3π/4, both strictly inside that interval. Angles, distances,
inner products and inverse trigonometric functions are the actual Mathlib
objects on the complex plane, eliminating the historical surd comparison proxy. -/
open Complex Real
open scoped RealInnerProductSpace
namespace MSE4217205
noncomputable def A : ℂ := -Complex.I
noncomputable def B : ℂ := 1
noncomputable def C : ℂ := 0
noncomputable def trueAngle : ℝ := InnerProductGeometry.angle (A-B) (C-B)
noncomputable def slope (X Y : ℂ) : ℝ := (Y.im-X.im)/(Y.re-X.re)
noncomputable def t : ℝ := (slope B C - slope A B)/(1 + slope B C*slope A B)
noncomputable def ruleAngle : ℝ := Real.pi + Real.arctan t

theorem coordinates : slope A B = 1 ∧ slope B C = 0 ∧ t = -1 := by
  norm_num [slope,A,B,C,t]

theorem actual_cos : Real.cos trueAngle = 1 / Real.sqrt 2 := by
  rw [trueAngle, InnerProductGeometry.cos_angle]
  norm_num [A,B,C, Complex.inner, Complex.norm_def, Complex.normSq]

theorem actual_angle : trueAngle = Real.pi/4 := by
  apply Real.injOn_cos (Set.mem_Icc.mpr ⟨InnerProductGeometry.angle_nonneg _ _,
      InnerProductGeometry.angle_le_pi _ _⟩)
    (Set.mem_Icc.mpr ⟨by positivity, by linarith [Real.pi_pos]⟩)
  change Real.cos trueAngle = Real.cos (Real.pi/4)
  rw [actual_cos, Real.cos_pi_div_four]
  have hs := Real.sq_sqrt (by norm_num : (0:ℝ) ≤ 2)
  have hp : 0 < Real.sqrt 2 := Real.sqrt_pos.2 (by norm_num)
  field_simp
  nlinarith

theorem claimed_angle : ruleAngle = 3 * Real.pi/4 := by
  rw [ruleAngle,coordinates.2.2,Real.arctan_neg,Real.arctan_one]
  ring

theorem true_distance : dist A C = 1 := by
  simp [A,C,dist_eq_norm]

theorem certificate :
    slope A B = 1 ∧ slope B C = 0 ∧ t = -1 ∧
    0 < trueAngle ∧ trueAngle < Real.pi ∧
    trueAngle = Real.pi/4 ∧ ruleAngle = 3*Real.pi/4 ∧
    ruleAngle ≠ trueAngle ∧ dist A C = 1 := by
  rw [coordinates.1,coordinates.2.1,coordinates.2.2,actual_angle,claimed_angle,true_distance]
  constructor; rfl
  constructor; rfl
  constructor; rfl
  have hp := Real.pi_pos
  refine ⟨by positivity,by linarith,rfl,rfl,?_,rfl⟩
  intro h
  linarith
end MSE4217205
