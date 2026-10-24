import SUBMISSION
import reference
/- EVALUATOR-ONLY hidden-instance agreement for E14: the submitted digit count must equal the reference constant
(the hole is a constant, so the agreement test is the constant itself) and must not be the source's printed figure. -/
theorem agree_0 : Audit_reddit_math_2s4u2m.digitBound = Audit_reddit_math_2s4u2m.Ref.digitBound := by
  first
  | decide
  | rfl
  | (norm_num [Audit_reddit_math_2s4u2m.digitBound, Audit_reddit_math_2s4u2m.Ref.digitBound])
theorem agree_1 : Audit_reddit_math_2s4u2m.digitBound ≠ 390000 := by
  first
  | decide
  | (norm_num [Audit_reddit_math_2s4u2m.digitBound])
#print axioms agree_0
#print axioms agree_1
