import SUBMISSION
import reference
/- EVALUATOR-ONLY hidden-instance agreement for E06: the submitted total must agree with the reference
T + a - 2(n-2)d on the listed (T, a, n, d). Core record: decide / rfl / simp / omega. -/
theorem agree_0 : SE_cstheory_2312_a2318_Census.total 2 19 3 20 = SE_cstheory_2312_a2318_Census.Ref.total 2 19 3 20 := by
  first
  | decide
  | rfl
  | (simp [SE_cstheory_2312_a2318_Census.total, SE_cstheory_2312_a2318_Census.Ref.total])
  | (unfold SE_cstheory_2312_a2318_Census.total SE_cstheory_2312_a2318_Census.Ref.total; omega)
theorem agree_1 : SE_cstheory_2312_a2318_Census.total 2 19 3 0 = SE_cstheory_2312_a2318_Census.Ref.total 2 19 3 0 := by
  first
  | decide
  | rfl
  | (simp [SE_cstheory_2312_a2318_Census.total, SE_cstheory_2312_a2318_Census.Ref.total])
  | (unfold SE_cstheory_2312_a2318_Census.total SE_cstheory_2312_a2318_Census.Ref.total; omega)
theorem agree_2 : SE_cstheory_2312_a2318_Census.total 2 0 2 5 = SE_cstheory_2312_a2318_Census.Ref.total 2 0 2 5 := by
  first
  | decide
  | rfl
  | (simp [SE_cstheory_2312_a2318_Census.total, SE_cstheory_2312_a2318_Census.Ref.total])
  | (unfold SE_cstheory_2312_a2318_Census.total SE_cstheory_2312_a2318_Census.Ref.total; omega)
theorem agree_3 : SE_cstheory_2312_a2318_Census.total 100 1 3 50 = SE_cstheory_2312_a2318_Census.Ref.total 100 1 3 50 := by
  first
  | decide
  | rfl
  | (simp [SE_cstheory_2312_a2318_Census.total, SE_cstheory_2312_a2318_Census.Ref.total])
  | (unfold SE_cstheory_2312_a2318_Census.total SE_cstheory_2312_a2318_Census.Ref.total; omega)
theorem agree_4 : SE_cstheory_2312_a2318_Census.total 1000 (-979) 3 1 = SE_cstheory_2312_a2318_Census.Ref.total 1000 (-979) 3 1 := by
  first
  | decide
  | rfl
  | (simp [SE_cstheory_2312_a2318_Census.total, SE_cstheory_2312_a2318_Census.Ref.total])
  | (unfold SE_cstheory_2312_a2318_Census.total SE_cstheory_2312_a2318_Census.Ref.total; omega)
theorem agree_5 : SE_cstheory_2312_a2318_Census.total 2 0 3 1 = SE_cstheory_2312_a2318_Census.Ref.total 2 0 3 1 := by
  first
  | decide
  | rfl
  | (simp [SE_cstheory_2312_a2318_Census.total, SE_cstheory_2312_a2318_Census.Ref.total])
  | (unfold SE_cstheory_2312_a2318_Census.total SE_cstheory_2312_a2318_Census.Ref.total; omega)
theorem agree_6 : SE_cstheory_2312_a2318_Census.total 5 5 4 1 = SE_cstheory_2312_a2318_Census.Ref.total 5 5 4 1 := by
  first
  | decide
  | rfl
  | (simp [SE_cstheory_2312_a2318_Census.total, SE_cstheory_2312_a2318_Census.Ref.total])
  | (unfold SE_cstheory_2312_a2318_Census.total SE_cstheory_2312_a2318_Census.Ref.total; omega)
theorem agree_7 : SE_cstheory_2312_a2318_Census.total 0 0 10 3 = SE_cstheory_2312_a2318_Census.Ref.total 0 0 10 3 := by
  first
  | decide
  | rfl
  | (simp [SE_cstheory_2312_a2318_Census.total, SE_cstheory_2312_a2318_Census.Ref.total])
  | (unfold SE_cstheory_2312_a2318_Census.total SE_cstheory_2312_a2318_Census.Ref.total; omega)
theorem agree_8 : SE_cstheory_2312_a2318_Census.total 7 (-3) 5 (-2) = SE_cstheory_2312_a2318_Census.Ref.total 7 (-3) 5 (-2) := by
  first
  | decide
  | rfl
  | (simp [SE_cstheory_2312_a2318_Census.total, SE_cstheory_2312_a2318_Census.Ref.total])
  | (unfold SE_cstheory_2312_a2318_Census.total SE_cstheory_2312_a2318_Census.Ref.total; omega)
#print axioms agree_0
#print axioms agree_1
#print axioms agree_2
#print axioms agree_3
#print axioms agree_4
#print axioms agree_5
#print axioms agree_6
#print axioms agree_7
#print axioms agree_8
