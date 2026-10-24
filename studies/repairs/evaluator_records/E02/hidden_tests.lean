import SUBMISSION
import reference
/- EVALUATOR-ONLY hidden-instance agreement for E02: the submitted postcondition must agree with the reference
(A[0] = 2 ∧ A[1] = 2, length ≥ 2) on every listed store. Core record: decide / rfl / simp. -/
theorem agree_0 : SE_cs_1200_a1206_Census.postC ([2, 2] : SE_cs_1200_a1206_Census.Store) = SE_cs_1200_a1206_Census.Ref.postC ([2, 2] : SE_cs_1200_a1206_Census.Store) := by
  first
  | decide
  | rfl
  | (simp [SE_cs_1200_a1206_Census.postC, SE_cs_1200_a1206_Census.Ref.postC, SE_cs_1200_a1206_Census.getI])
theorem agree_1 : SE_cs_1200_a1206_Census.postC ([2, 2, 0] : SE_cs_1200_a1206_Census.Store) = SE_cs_1200_a1206_Census.Ref.postC ([2, 2, 0] : SE_cs_1200_a1206_Census.Store) := by
  first
  | decide
  | rfl
  | (simp [SE_cs_1200_a1206_Census.postC, SE_cs_1200_a1206_Census.Ref.postC, SE_cs_1200_a1206_Census.getI])
theorem agree_2 : SE_cs_1200_a1206_Census.postC ([2, 2, 7, 7] : SE_cs_1200_a1206_Census.Store) = SE_cs_1200_a1206_Census.Ref.postC ([2, 2, 7, 7] : SE_cs_1200_a1206_Census.Store) := by
  first
  | decide
  | rfl
  | (simp [SE_cs_1200_a1206_Census.postC, SE_cs_1200_a1206_Census.Ref.postC, SE_cs_1200_a1206_Census.getI])
theorem agree_3 : SE_cs_1200_a1206_Census.postC ([1, 1] : SE_cs_1200_a1206_Census.Store) = SE_cs_1200_a1206_Census.Ref.postC ([1, 1] : SE_cs_1200_a1206_Census.Store) := by
  first
  | decide
  | rfl
  | (simp [SE_cs_1200_a1206_Census.postC, SE_cs_1200_a1206_Census.Ref.postC, SE_cs_1200_a1206_Census.getI])
theorem agree_4 : SE_cs_1200_a1206_Census.postC ([2, 3] : SE_cs_1200_a1206_Census.Store) = SE_cs_1200_a1206_Census.Ref.postC ([2, 3] : SE_cs_1200_a1206_Census.Store) := by
  first
  | decide
  | rfl
  | (simp [SE_cs_1200_a1206_Census.postC, SE_cs_1200_a1206_Census.Ref.postC, SE_cs_1200_a1206_Census.getI])
theorem agree_5 : SE_cs_1200_a1206_Census.postC ([2] : SE_cs_1200_a1206_Census.Store) = SE_cs_1200_a1206_Census.Ref.postC ([2] : SE_cs_1200_a1206_Census.Store) := by
  first
  | decide
  | rfl
  | (simp [SE_cs_1200_a1206_Census.postC, SE_cs_1200_a1206_Census.Ref.postC, SE_cs_1200_a1206_Census.getI])
theorem agree_6 : SE_cs_1200_a1206_Census.postC ([] : SE_cs_1200_a1206_Census.Store) = SE_cs_1200_a1206_Census.Ref.postC ([] : SE_cs_1200_a1206_Census.Store) := by
  first
  | decide
  | rfl
  | (simp [SE_cs_1200_a1206_Census.postC, SE_cs_1200_a1206_Census.Ref.postC, SE_cs_1200_a1206_Census.getI])
theorem agree_7 : SE_cs_1200_a1206_Census.postC ([3, 2] : SE_cs_1200_a1206_Census.Store) = SE_cs_1200_a1206_Census.Ref.postC ([3, 2] : SE_cs_1200_a1206_Census.Store) := by
  first
  | decide
  | rfl
  | (simp [SE_cs_1200_a1206_Census.postC, SE_cs_1200_a1206_Census.Ref.postC, SE_cs_1200_a1206_Census.getI])
theorem agree_8 : SE_cs_1200_a1206_Census.postC ([2, 2, 5] : SE_cs_1200_a1206_Census.Store) = SE_cs_1200_a1206_Census.Ref.postC ([2, 2, 5] : SE_cs_1200_a1206_Census.Store) := by
  first
  | decide
  | rfl
  | (simp [SE_cs_1200_a1206_Census.postC, SE_cs_1200_a1206_Census.Ref.postC, SE_cs_1200_a1206_Census.getI])
theorem agree_9 : SE_cs_1200_a1206_Census.postC ([0, 2] : SE_cs_1200_a1206_Census.Store) = SE_cs_1200_a1206_Census.Ref.postC ([0, 2] : SE_cs_1200_a1206_Census.Store) := by
  first
  | decide
  | rfl
  | (simp [SE_cs_1200_a1206_Census.postC, SE_cs_1200_a1206_Census.Ref.postC, SE_cs_1200_a1206_Census.getI])
theorem agree_10 : SE_cs_1200_a1206_Census.postC ([2, 2, -1, 3] : SE_cs_1200_a1206_Census.Store) = SE_cs_1200_a1206_Census.Ref.postC ([2, 2, -1, 3] : SE_cs_1200_a1206_Census.Store) := by
  first
  | decide
  | rfl
  | (simp [SE_cs_1200_a1206_Census.postC, SE_cs_1200_a1206_Census.Ref.postC, SE_cs_1200_a1206_Census.getI])
theorem agree_11 : SE_cs_1200_a1206_Census.postC ([2, 1] : SE_cs_1200_a1206_Census.Store) = SE_cs_1200_a1206_Census.Ref.postC ([2, 1] : SE_cs_1200_a1206_Census.Store) := by
  first
  | decide
  | rfl
  | (simp [SE_cs_1200_a1206_Census.postC, SE_cs_1200_a1206_Census.Ref.postC, SE_cs_1200_a1206_Census.getI])
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
#print axioms agree_10
#print axioms agree_11
