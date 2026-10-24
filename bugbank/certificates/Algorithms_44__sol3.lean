import Mathlib
namespace QEDBench.Algorithms_44_sol3
abbrev Vec := ℝ × ℝ
def P : Set Vec := {x | 0 ≤ x.1 ∧ 0 ≤ x.2 ∧ 1 ≤ x.1 + x.2}
def y : Vec := (0,0)
def c : Vec := (-1,-1)
def dot (u v : Vec) : ℝ := dotProduct ![u.1,u.2] ![v.1,v.2]
lemma dot_c (x : Vec) : dot c x = -(x.1+x.2) := by
  simp [dot, c, dotProduct, Fin.sum_univ_two]
  ring
/-- Original rational separator c=(-1,-1): maximum -1 attained at(1,0), below c·y=0. -/
theorem certificate :
    y ∉ P ∧ IsGreatest ((dot c) '' P) (-1) ∧ dot c y = 0 ∧
    (-1 : ℝ) < dot c y ∧
    (∃ q : ℚ × ℚ, c = ((q.1 : ℝ),(q.2 : ℝ))) := by
  have hg : IsGreatest ((dot c) '' P) (-1) := by
    constructor
    · refine ⟨(1,0), by norm_num [P], ?_⟩
      rw [dot_c]
      norm_num
    · rintro z ⟨x,hx,rfl⟩
      rw [dot_c]
      exact neg_le_neg hx.2.2
  refine ⟨by norm_num [y,P], hg, ?_, ?_, ?_⟩
  · rw [dot_c]; norm_num [y]
  · rw [dot_c]; norm_num [y]
  · exact ⟨(-1,-1), by norm_num [c]⟩
end QEDBench.Algorithms_44_sol3
