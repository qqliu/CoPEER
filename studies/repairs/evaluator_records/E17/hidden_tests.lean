import SUBMISSION
import reference
/- EVALUATOR-ONLY hidden-instance agreement for E17: the submitted right-hand side must agree with the reference
(2 * a ^ 2 - 1) ^ 2 + 3 at the listed integers (a = 2 is the certified witness: 52, where the source's rhs gives 12). -/
theorem agree_0 : G3refPnv102.rhsC 2 = G3refPnv102.Ref.rhsC 2 := by
  first
  | decide
  | rfl
  | (norm_num [G3refPnv102.rhsC, G3refPnv102.Ref.rhsC])
  | (simp only [G3refPnv102.rhsC, G3refPnv102.Ref.rhsC]; norm_num)
theorem agree_1 : G3refPnv102.rhsC 0 = G3refPnv102.Ref.rhsC 0 := by
  first
  | decide
  | rfl
  | (norm_num [G3refPnv102.rhsC, G3refPnv102.Ref.rhsC])
  | (simp only [G3refPnv102.rhsC, G3refPnv102.Ref.rhsC]; norm_num)
theorem agree_2 : G3refPnv102.rhsC 1 = G3refPnv102.Ref.rhsC 1 := by
  first
  | decide
  | rfl
  | (norm_num [G3refPnv102.rhsC, G3refPnv102.Ref.rhsC])
  | (simp only [G3refPnv102.rhsC, G3refPnv102.Ref.rhsC]; norm_num)
theorem agree_3 : G3refPnv102.rhsC (-1) = G3refPnv102.Ref.rhsC (-1) := by
  first
  | decide
  | rfl
  | (norm_num [G3refPnv102.rhsC, G3refPnv102.Ref.rhsC])
  | (simp only [G3refPnv102.rhsC, G3refPnv102.Ref.rhsC]; norm_num)
theorem agree_4 : G3refPnv102.rhsC 3 = G3refPnv102.Ref.rhsC 3 := by
  first
  | decide
  | rfl
  | (norm_num [G3refPnv102.rhsC, G3refPnv102.Ref.rhsC])
  | (simp only [G3refPnv102.rhsC, G3refPnv102.Ref.rhsC]; norm_num)
theorem agree_5 : G3refPnv102.rhsC (-2) = G3refPnv102.Ref.rhsC (-2) := by
  first
  | decide
  | rfl
  | (norm_num [G3refPnv102.rhsC, G3refPnv102.Ref.rhsC])
  | (simp only [G3refPnv102.rhsC, G3refPnv102.Ref.rhsC]; norm_num)
theorem agree_6 : G3refPnv102.rhsC 5 = G3refPnv102.Ref.rhsC 5 := by
  first
  | decide
  | rfl
  | (norm_num [G3refPnv102.rhsC, G3refPnv102.Ref.rhsC])
  | (simp only [G3refPnv102.rhsC, G3refPnv102.Ref.rhsC]; norm_num)
theorem agree_7 : G3refPnv102.rhsC (-7) = G3refPnv102.Ref.rhsC (-7) := by
  first
  | decide
  | rfl
  | (norm_num [G3refPnv102.rhsC, G3refPnv102.Ref.rhsC])
  | (simp only [G3refPnv102.rhsC, G3refPnv102.Ref.rhsC]; norm_num)
theorem agree_8 : G3refPnv102.rhsC 10 = G3refPnv102.Ref.rhsC 10 := by
  first
  | decide
  | rfl
  | (norm_num [G3refPnv102.rhsC, G3refPnv102.Ref.rhsC])
  | (simp only [G3refPnv102.rhsC, G3refPnv102.Ref.rhsC]; norm_num)
theorem agree_9 : G3refPnv102.rhsC (-3) = G3refPnv102.Ref.rhsC (-3) := by
  first
  | decide
  | rfl
  | (norm_num [G3refPnv102.rhsC, G3refPnv102.Ref.rhsC])
  | (simp only [G3refPnv102.rhsC, G3refPnv102.Ref.rhsC]; norm_num)
#print axioms agree_0
#print axioms agree_1
#print axioms agree_2
#print axioms agree_3
#print axioms agree_4
#print axioms agree_5
#print axioms agree_6
#print axioms agree_7
#print axioms agree_8
#print axioms agree_9
