import SUBMISSION
import reference
set_option linter.unreachableTactic false
set_option linter.unusedTactic false
/- EVALUATOR-ONLY hidden-instance agreement for E07: the submitted count must equal the reference count k at every
listed k ≥ 2 (exact, line 257: SentenceWith k c ↔ c = k for k ≥ 2, so every admissible count agrees here). -/
theorem agree_2 : Census_SE_math_1291495__q.edge_count 2 = Census_SE_math_1291495__q.Ref.edge_count 2 := by
  first
  | decide
  | rfl
  | (norm_num [Census_SE_math_1291495__q.edge_count, Census_SE_math_1291495__q.Ref.edge_count])
  | (simp [Census_SE_math_1291495__q.edge_count, Census_SE_math_1291495__q.Ref.edge_count])
  | (unfold Census_SE_math_1291495__q.edge_count Census_SE_math_1291495__q.Ref.edge_count; omega)
theorem agree_3 : Census_SE_math_1291495__q.edge_count 3 = Census_SE_math_1291495__q.Ref.edge_count 3 := by
  first
  | decide
  | rfl
  | (norm_num [Census_SE_math_1291495__q.edge_count, Census_SE_math_1291495__q.Ref.edge_count])
  | (simp [Census_SE_math_1291495__q.edge_count, Census_SE_math_1291495__q.Ref.edge_count])
  | (unfold Census_SE_math_1291495__q.edge_count Census_SE_math_1291495__q.Ref.edge_count; omega)
theorem agree_4 : Census_SE_math_1291495__q.edge_count 4 = Census_SE_math_1291495__q.Ref.edge_count 4 := by
  first
  | decide
  | rfl
  | (norm_num [Census_SE_math_1291495__q.edge_count, Census_SE_math_1291495__q.Ref.edge_count])
  | (simp [Census_SE_math_1291495__q.edge_count, Census_SE_math_1291495__q.Ref.edge_count])
  | (unfold Census_SE_math_1291495__q.edge_count Census_SE_math_1291495__q.Ref.edge_count; omega)
theorem agree_5 : Census_SE_math_1291495__q.edge_count 5 = Census_SE_math_1291495__q.Ref.edge_count 5 := by
  first
  | decide
  | rfl
  | (norm_num [Census_SE_math_1291495__q.edge_count, Census_SE_math_1291495__q.Ref.edge_count])
  | (simp [Census_SE_math_1291495__q.edge_count, Census_SE_math_1291495__q.Ref.edge_count])
  | (unfold Census_SE_math_1291495__q.edge_count Census_SE_math_1291495__q.Ref.edge_count; omega)
theorem agree_10 : Census_SE_math_1291495__q.edge_count 10 = Census_SE_math_1291495__q.Ref.edge_count 10 := by
  first
  | decide
  | rfl
  | (norm_num [Census_SE_math_1291495__q.edge_count, Census_SE_math_1291495__q.Ref.edge_count])
  | (simp [Census_SE_math_1291495__q.edge_count, Census_SE_math_1291495__q.Ref.edge_count])
  | (unfold Census_SE_math_1291495__q.edge_count Census_SE_math_1291495__q.Ref.edge_count; omega)
theorem agree_100 : Census_SE_math_1291495__q.edge_count 100 = Census_SE_math_1291495__q.Ref.edge_count 100 := by
  first
  | decide
  | rfl
  | (norm_num [Census_SE_math_1291495__q.edge_count, Census_SE_math_1291495__q.Ref.edge_count])
  | (simp [Census_SE_math_1291495__q.edge_count, Census_SE_math_1291495__q.Ref.edge_count])
  | (unfold Census_SE_math_1291495__q.edge_count Census_SE_math_1291495__q.Ref.edge_count; omega)
#print axioms agree_2
#print axioms agree_3
#print axioms agree_4
#print axioms agree_5
#print axioms agree_10
#print axioms agree_100
