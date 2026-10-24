import Mathlib
/-! Original spiral r(t)=1+t,theta(t)=t at0. All derivatives,
trigonometry, square roots, and arc length integrals are actual Mathlib
objects. Curvature is turning-angle derivative divided by arc-length
derivative, as in the source's Whewell definition. -/
noncomputable section
namespace ProofWiki99460CodexExpansion
open Real

def x (t : ℝ) := (1+t)*cos t
def y (t : ℝ) := (1+t)*sin t
def dx (t : ℝ) := cos t - (1+t)*sin t
def dy (t : ℝ) := sin t + (1+t)*cos t
def angle (t : ℝ) := arctan (dy t / dx t)
def speed (t : ℝ) := sqrt ((dx t)^2 + (dy t)^2)
def arc (t : ℝ) := ∫ u in (0:ℝ)..t, speed u

theorem x_derivative (t : ℝ) : HasDerivAt x (dx t) t := by
  convert (((hasDerivAt_id t).const_add 1).mul (hasDerivAt_cos t)) using 1 <;>
    simp [x,dx] <;> ring

theorem y_derivative (t : ℝ) : HasDerivAt y (dy t) t := by
  convert (((hasDerivAt_id t).const_add 1).mul (hasDerivAt_sin t)) using 1 <;>
    simp [y,dy] <;> ring

theorem dx_zero : HasDerivAt dx (-1) 0 := by
  convert (hasDerivAt_cos (0:ℝ)).sub
    (((hasDerivAt_id (0:ℝ)).const_add 1).mul (hasDerivAt_sin 0)) using 1 <;>
    norm_num [dx]

theorem dy_zero : HasDerivAt dy 2 0 := by
  convert (hasDerivAt_sin (0:ℝ)).add
    (((hasDerivAt_id (0:ℝ)).const_add 1).mul (hasDerivAt_cos 0)) using 1 <;>
    norm_num [dy]

theorem angle_derivative : HasDerivAt angle (3/2) 0 := by
  convert (dy_zero.div dx_zero (by norm_num [dx])).arctan using 1 <;>
    norm_num [angle,dx,dy]

theorem arc_derivative : HasDerivAt arc (sqrt 2) 0 := by
  have hc : Continuous speed := by unfold speed dx dy; fun_prop
  convert intervalIntegral.integral_hasDerivAt_right (hc.intervalIntegrable 0 0)
    hc.stronglyMeasurable.stronglyMeasurableAtFilter hc.continuousAt using 1 <;>
    norm_num [arc,speed,dx,dy]

theorem refutes_published_curvature_formula :
    deriv x 0 = 1 ∧ deriv y 0 = 1 ∧
    deriv angle 0 = 3/2 ∧ deriv arc 0 = sqrt 2 ∧
    deriv angle 0 / deriv arc 0 ≠ 3 / sqrt 2 := by
  have hs : sqrt 2 ≠ 0 := ne_of_gt (sqrt_pos.2 (by norm_num))
  refine ⟨?_, ?_, angle_derivative.deriv, arc_derivative.deriv, ?_⟩
  · simpa [dx] using (x_derivative 0).deriv
  · simpa [dy] using (y_derivative 0).deriv
  · rw [angle_derivative.deriv, arc_derivative.deriv]
    intro h
    have := (div_left_inj' hs).mp h
    norm_num at this
/-- The original polar parameters, including both derivatives in the displayed formula. -/
def r (t : ℝ) := 1 + t
def theta (t : ℝ) := t
def publishedPolar (t : ℝ) :=
  (2 * (deriv r t)^2 * deriv theta t + r t * deriv (deriv r) t * deriv theta t +
    r t * deriv r t * deriv (deriv theta) t + (r t)^2 * (deriv theta t)^3) /
      sqrt ((deriv r t)^2 + (r t * deriv theta t)^2)

theorem polar_parameters :
    deriv r = (fun _ => 1) ∧ deriv theta = (fun _ => 1) ∧
    x = (fun t => r t * cos (theta t)) ∧ y = (fun t => r t * sin (theta t)) := by
  refine ⟨?_, ?_, rfl, rfl⟩
  · funext t
    exact (((hasDerivAt_id t).const_add 1).deriv)
  · funext t
    exact (hasDerivAt_id t).deriv

theorem refutes_complete_polar_expression :
    publishedPolar 0 = 3 / sqrt 2 ∧
    deriv angle 0 / deriv arc 0 ≠ publishedPolar 0 := by
  have hp : publishedPolar 0 = 3 / sqrt 2 := by
    simp [publishedPolar, polar_parameters.1, polar_parameters.2.1, r]
    ring
  exact ⟨hp, hp ▸ refutes_published_curvature_formula.2.2.2.2⟩
end ProofWiki99460CodexExpansion
