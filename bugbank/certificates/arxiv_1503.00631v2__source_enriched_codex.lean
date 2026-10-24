import Mathlib.Tactic
namespace Arxiv150300631v2SourceEnrichedCodex
noncomputable def F : ℝ := 9/4
noncomputable def B : ℝ := 43043/100000
noncomputable def surrogate : ℝ :=
  0.246345*B^2 + (18.810319*F-42.033351)*B +
  202.972148*F^2-924.926294*F+1052.803636
noncomputable def assertedBound : ℝ := 102.618907*F^2-473.377198*F-509.223573
theorem refutes_displayed_quadratic_bound :
    2.226 < F ∧ F ≤ 2.26 ∧ B = -24.116548*F+54.692663 ∧
    surrogate > assertedBound := by
  norm_num [F,B,surrogate,assertedBound]
end Arxiv150300631v2SourceEnrichedCodex
