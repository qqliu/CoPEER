import SUBMISSION
import reference
set_option maxRecDepth 100000
/- EVALUATOR-ONLY hidden-instance agreement for E01: the submitted program must return the integer square root
(the reference strict-guard program's value) at every listed input. Core record: decide / rfl / simp only. -/
theorem agree_0 : SqrtFailureBoundary.progC 0 = SqrtFailureBoundary.Ref.progC 0 := by
  first
  | decide
  | rfl
  | (simp [SqrtFailureBoundary.progC, SqrtFailureBoundary.step, SqrtFailureBoundary.Ref.progC, SqrtFailureBoundary.Ref.step])
theorem agree_1 : SqrtFailureBoundary.progC 1 = SqrtFailureBoundary.Ref.progC 1 := by
  first
  | decide
  | rfl
  | (simp [SqrtFailureBoundary.progC, SqrtFailureBoundary.step, SqrtFailureBoundary.Ref.progC, SqrtFailureBoundary.Ref.step])
theorem agree_2 : SqrtFailureBoundary.progC 2 = SqrtFailureBoundary.Ref.progC 2 := by
  first
  | decide
  | rfl
  | (simp [SqrtFailureBoundary.progC, SqrtFailureBoundary.step, SqrtFailureBoundary.Ref.progC, SqrtFailureBoundary.Ref.step])
theorem agree_3 : SqrtFailureBoundary.progC 3 = SqrtFailureBoundary.Ref.progC 3 := by
  first
  | decide
  | rfl
  | (simp [SqrtFailureBoundary.progC, SqrtFailureBoundary.step, SqrtFailureBoundary.Ref.progC, SqrtFailureBoundary.Ref.step])
theorem agree_4 : SqrtFailureBoundary.progC 4 = SqrtFailureBoundary.Ref.progC 4 := by
  first
  | decide
  | rfl
  | (simp [SqrtFailureBoundary.progC, SqrtFailureBoundary.step, SqrtFailureBoundary.Ref.progC, SqrtFailureBoundary.Ref.step])
theorem agree_5 : SqrtFailureBoundary.progC 5 = SqrtFailureBoundary.Ref.progC 5 := by
  first
  | decide
  | rfl
  | (simp [SqrtFailureBoundary.progC, SqrtFailureBoundary.step, SqrtFailureBoundary.Ref.progC, SqrtFailureBoundary.Ref.step])
theorem agree_8 : SqrtFailureBoundary.progC 8 = SqrtFailureBoundary.Ref.progC 8 := by
  first
  | decide
  | rfl
  | (simp [SqrtFailureBoundary.progC, SqrtFailureBoundary.step, SqrtFailureBoundary.Ref.progC, SqrtFailureBoundary.Ref.step])
theorem agree_9 : SqrtFailureBoundary.progC 9 = SqrtFailureBoundary.Ref.progC 9 := by
  first
  | decide
  | rfl
  | (simp [SqrtFailureBoundary.progC, SqrtFailureBoundary.step, SqrtFailureBoundary.Ref.progC, SqrtFailureBoundary.Ref.step])
theorem agree_10 : SqrtFailureBoundary.progC 10 = SqrtFailureBoundary.Ref.progC 10 := by
  first
  | decide
  | rfl
  | (simp [SqrtFailureBoundary.progC, SqrtFailureBoundary.step, SqrtFailureBoundary.Ref.progC, SqrtFailureBoundary.Ref.step])
theorem agree_15 : SqrtFailureBoundary.progC 15 = SqrtFailureBoundary.Ref.progC 15 := by
  first
  | decide
  | rfl
  | (simp [SqrtFailureBoundary.progC, SqrtFailureBoundary.step, SqrtFailureBoundary.Ref.progC, SqrtFailureBoundary.Ref.step])
theorem agree_16 : SqrtFailureBoundary.progC 16 = SqrtFailureBoundary.Ref.progC 16 := by
  first
  | decide
  | rfl
  | (simp [SqrtFailureBoundary.progC, SqrtFailureBoundary.step, SqrtFailureBoundary.Ref.progC, SqrtFailureBoundary.Ref.step])
theorem agree_17 : SqrtFailureBoundary.progC 17 = SqrtFailureBoundary.Ref.progC 17 := by
  first
  | decide
  | rfl
  | (simp [SqrtFailureBoundary.progC, SqrtFailureBoundary.step, SqrtFailureBoundary.Ref.progC, SqrtFailureBoundary.Ref.step])
theorem agree_24 : SqrtFailureBoundary.progC 24 = SqrtFailureBoundary.Ref.progC 24 := by
  first
  | decide
  | rfl
  | (simp [SqrtFailureBoundary.progC, SqrtFailureBoundary.step, SqrtFailureBoundary.Ref.progC, SqrtFailureBoundary.Ref.step])
theorem agree_25 : SqrtFailureBoundary.progC 25 = SqrtFailureBoundary.Ref.progC 25 := by
  first
  | decide
  | rfl
  | (simp [SqrtFailureBoundary.progC, SqrtFailureBoundary.step, SqrtFailureBoundary.Ref.progC, SqrtFailureBoundary.Ref.step])
theorem agree_26 : SqrtFailureBoundary.progC 26 = SqrtFailureBoundary.Ref.progC 26 := by
  first
  | decide
  | rfl
  | (simp [SqrtFailureBoundary.progC, SqrtFailureBoundary.step, SqrtFailureBoundary.Ref.progC, SqrtFailureBoundary.Ref.step])
theorem agree_35 : SqrtFailureBoundary.progC 35 = SqrtFailureBoundary.Ref.progC 35 := by
  first
  | decide
  | rfl
  | (simp [SqrtFailureBoundary.progC, SqrtFailureBoundary.step, SqrtFailureBoundary.Ref.progC, SqrtFailureBoundary.Ref.step])
theorem agree_36 : SqrtFailureBoundary.progC 36 = SqrtFailureBoundary.Ref.progC 36 := by
  first
  | decide
  | rfl
  | (simp [SqrtFailureBoundary.progC, SqrtFailureBoundary.step, SqrtFailureBoundary.Ref.progC, SqrtFailureBoundary.Ref.step])
theorem agree_48 : SqrtFailureBoundary.progC 48 = SqrtFailureBoundary.Ref.progC 48 := by
  first
  | decide
  | rfl
  | (simp [SqrtFailureBoundary.progC, SqrtFailureBoundary.step, SqrtFailureBoundary.Ref.progC, SqrtFailureBoundary.Ref.step])
theorem agree_49 : SqrtFailureBoundary.progC 49 = SqrtFailureBoundary.Ref.progC 49 := by
  first
  | decide
  | rfl
  | (simp [SqrtFailureBoundary.progC, SqrtFailureBoundary.step, SqrtFailureBoundary.Ref.progC, SqrtFailureBoundary.Ref.step])
#print axioms agree_0
#print axioms agree_1
#print axioms agree_2
#print axioms agree_3
#print axioms agree_4
#print axioms agree_5
#print axioms agree_8
#print axioms agree_9
#print axioms agree_10
#print axioms agree_15
#print axioms agree_16
#print axioms agree_17
#print axioms agree_24
#print axioms agree_25
#print axioms agree_26
#print axioms agree_35
#print axioms agree_36
#print axioms agree_48
#print axioms agree_49
