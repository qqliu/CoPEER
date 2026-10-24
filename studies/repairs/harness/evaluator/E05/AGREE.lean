import SUBMISSION
import reference
set_option linter.unreachableTactic false
set_option linter.unusedTactic false
/- EVALUATOR-ONLY hidden-instance agreement for E05 (Nat model): the submitted rhs must agree with the reference
(b^L)^p * sum_{i<L} (i+1)^k at the listed (b, p, k, L) with b ≥ 2. -/
theorem agree_0 : SE_cs_1957_a2388_Census.rhs 2 1 1 2 = SE_cs_1957_a2388_Census.Ref.rhs 2 1 1 2 := by
  first
  | decide
  | rfl
  | (norm_num [SE_cs_1957_a2388_Census.rhs, SE_cs_1957_a2388_Census.Ref.rhs, Finset.sum_range_succ])
  | (simp [SE_cs_1957_a2388_Census.rhs, SE_cs_1957_a2388_Census.Ref.rhs, Finset.sum_range_succ])
  | (unfold SE_cs_1957_a2388_Census.rhs SE_cs_1957_a2388_Census.Ref.rhs; decide)
theorem agree_1 : SE_cs_1957_a2388_Census.rhs 2 1 0 2 = SE_cs_1957_a2388_Census.Ref.rhs 2 1 0 2 := by
  first
  | decide
  | rfl
  | (norm_num [SE_cs_1957_a2388_Census.rhs, SE_cs_1957_a2388_Census.Ref.rhs, Finset.sum_range_succ])
  | (simp [SE_cs_1957_a2388_Census.rhs, SE_cs_1957_a2388_Census.Ref.rhs, Finset.sum_range_succ])
  | (unfold SE_cs_1957_a2388_Census.rhs SE_cs_1957_a2388_Census.Ref.rhs; decide)
theorem agree_2 : SE_cs_1957_a2388_Census.rhs 2 0 1 2 = SE_cs_1957_a2388_Census.Ref.rhs 2 0 1 2 := by
  first
  | decide
  | rfl
  | (norm_num [SE_cs_1957_a2388_Census.rhs, SE_cs_1957_a2388_Census.Ref.rhs, Finset.sum_range_succ])
  | (simp [SE_cs_1957_a2388_Census.rhs, SE_cs_1957_a2388_Census.Ref.rhs, Finset.sum_range_succ])
  | (unfold SE_cs_1957_a2388_Census.rhs SE_cs_1957_a2388_Census.Ref.rhs; decide)
theorem agree_3 : SE_cs_1957_a2388_Census.rhs 3 1 1 2 = SE_cs_1957_a2388_Census.Ref.rhs 3 1 1 2 := by
  first
  | decide
  | rfl
  | (norm_num [SE_cs_1957_a2388_Census.rhs, SE_cs_1957_a2388_Census.Ref.rhs, Finset.sum_range_succ])
  | (simp [SE_cs_1957_a2388_Census.rhs, SE_cs_1957_a2388_Census.Ref.rhs, Finset.sum_range_succ])
  | (unfold SE_cs_1957_a2388_Census.rhs SE_cs_1957_a2388_Census.Ref.rhs; decide)
theorem agree_4 : SE_cs_1957_a2388_Census.rhs 2 1 2 3 = SE_cs_1957_a2388_Census.Ref.rhs 2 1 2 3 := by
  first
  | decide
  | rfl
  | (norm_num [SE_cs_1957_a2388_Census.rhs, SE_cs_1957_a2388_Census.Ref.rhs, Finset.sum_range_succ])
  | (simp [SE_cs_1957_a2388_Census.rhs, SE_cs_1957_a2388_Census.Ref.rhs, Finset.sum_range_succ])
  | (unfold SE_cs_1957_a2388_Census.rhs SE_cs_1957_a2388_Census.Ref.rhs; decide)
theorem agree_5 : SE_cs_1957_a2388_Census.rhs 2 2 1 3 = SE_cs_1957_a2388_Census.Ref.rhs 2 2 1 3 := by
  first
  | decide
  | rfl
  | (norm_num [SE_cs_1957_a2388_Census.rhs, SE_cs_1957_a2388_Census.Ref.rhs, Finset.sum_range_succ])
  | (simp [SE_cs_1957_a2388_Census.rhs, SE_cs_1957_a2388_Census.Ref.rhs, Finset.sum_range_succ])
  | (unfold SE_cs_1957_a2388_Census.rhs SE_cs_1957_a2388_Census.Ref.rhs; decide)
theorem agree_6 : SE_cs_1957_a2388_Census.rhs 5 1 1 1 = SE_cs_1957_a2388_Census.Ref.rhs 5 1 1 1 := by
  first
  | decide
  | rfl
  | (norm_num [SE_cs_1957_a2388_Census.rhs, SE_cs_1957_a2388_Census.Ref.rhs, Finset.sum_range_succ])
  | (simp [SE_cs_1957_a2388_Census.rhs, SE_cs_1957_a2388_Census.Ref.rhs, Finset.sum_range_succ])
  | (unfold SE_cs_1957_a2388_Census.rhs SE_cs_1957_a2388_Census.Ref.rhs; decide)
theorem agree_7 : SE_cs_1957_a2388_Census.rhs 2 1 1 0 = SE_cs_1957_a2388_Census.Ref.rhs 2 1 1 0 := by
  first
  | decide
  | rfl
  | (norm_num [SE_cs_1957_a2388_Census.rhs, SE_cs_1957_a2388_Census.Ref.rhs, Finset.sum_range_succ])
  | (simp [SE_cs_1957_a2388_Census.rhs, SE_cs_1957_a2388_Census.Ref.rhs, Finset.sum_range_succ])
  | (unfold SE_cs_1957_a2388_Census.rhs SE_cs_1957_a2388_Census.Ref.rhs; decide)
theorem agree_8 : SE_cs_1957_a2388_Census.rhs 3 2 3 2 = SE_cs_1957_a2388_Census.Ref.rhs 3 2 3 2 := by
  first
  | decide
  | rfl
  | (norm_num [SE_cs_1957_a2388_Census.rhs, SE_cs_1957_a2388_Census.Ref.rhs, Finset.sum_range_succ])
  | (simp [SE_cs_1957_a2388_Census.rhs, SE_cs_1957_a2388_Census.Ref.rhs, Finset.sum_range_succ])
  | (unfold SE_cs_1957_a2388_Census.rhs SE_cs_1957_a2388_Census.Ref.rhs; decide)
theorem agree_9 : SE_cs_1957_a2388_Census.rhs 2 3 2 4 = SE_cs_1957_a2388_Census.Ref.rhs 2 3 2 4 := by
  first
  | decide
  | rfl
  | (norm_num [SE_cs_1957_a2388_Census.rhs, SE_cs_1957_a2388_Census.Ref.rhs, Finset.sum_range_succ])
  | (simp [SE_cs_1957_a2388_Census.rhs, SE_cs_1957_a2388_Census.Ref.rhs, Finset.sum_range_succ])
  | (unfold SE_cs_1957_a2388_Census.rhs SE_cs_1957_a2388_Census.Ref.rhs; decide)
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
