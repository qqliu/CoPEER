import SUBMISSION
import reference
set_option linter.unreachableTactic false
set_option linter.unusedTactic false
/- EVALUATOR-ONLY hidden-instance agreement for E11: the submitted scalar factor must agree with |a| at the listed integers. -/
theorem agree_0 : ProofWiki25056Census.scalar_factor (-1) = ProofWiki25056Census.Ref.scalar_factor (-1) := by
  first
  | decide
  | rfl
  | (simp [ProofWiki25056Census.scalar_factor, ProofWiki25056Census.Ref.scalar_factor, ← Int.abs_eq_normalize])
  | (norm_num [ProofWiki25056Census.scalar_factor, ProofWiki25056Census.Ref.scalar_factor, ← Int.abs_eq_normalize])
  | (unfold ProofWiki25056Census.scalar_factor ProofWiki25056Census.Ref.scalar_factor; decide)
theorem agree_1 : ProofWiki25056Census.scalar_factor 0 = ProofWiki25056Census.Ref.scalar_factor 0 := by
  first
  | decide
  | rfl
  | (simp [ProofWiki25056Census.scalar_factor, ProofWiki25056Census.Ref.scalar_factor, ← Int.abs_eq_normalize])
  | (norm_num [ProofWiki25056Census.scalar_factor, ProofWiki25056Census.Ref.scalar_factor, ← Int.abs_eq_normalize])
  | (unfold ProofWiki25056Census.scalar_factor ProofWiki25056Census.Ref.scalar_factor; decide)
theorem agree_2 : ProofWiki25056Census.scalar_factor 1 = ProofWiki25056Census.Ref.scalar_factor 1 := by
  first
  | decide
  | rfl
  | (simp [ProofWiki25056Census.scalar_factor, ProofWiki25056Census.Ref.scalar_factor, ← Int.abs_eq_normalize])
  | (norm_num [ProofWiki25056Census.scalar_factor, ProofWiki25056Census.Ref.scalar_factor, ← Int.abs_eq_normalize])
  | (unfold ProofWiki25056Census.scalar_factor ProofWiki25056Census.Ref.scalar_factor; decide)
theorem agree_3 : ProofWiki25056Census.scalar_factor 2 = ProofWiki25056Census.Ref.scalar_factor 2 := by
  first
  | decide
  | rfl
  | (simp [ProofWiki25056Census.scalar_factor, ProofWiki25056Census.Ref.scalar_factor, ← Int.abs_eq_normalize])
  | (norm_num [ProofWiki25056Census.scalar_factor, ProofWiki25056Census.Ref.scalar_factor, ← Int.abs_eq_normalize])
  | (unfold ProofWiki25056Census.scalar_factor ProofWiki25056Census.Ref.scalar_factor; decide)
theorem agree_4 : ProofWiki25056Census.scalar_factor (-2) = ProofWiki25056Census.Ref.scalar_factor (-2) := by
  first
  | decide
  | rfl
  | (simp [ProofWiki25056Census.scalar_factor, ProofWiki25056Census.Ref.scalar_factor, ← Int.abs_eq_normalize])
  | (norm_num [ProofWiki25056Census.scalar_factor, ProofWiki25056Census.Ref.scalar_factor, ← Int.abs_eq_normalize])
  | (unfold ProofWiki25056Census.scalar_factor ProofWiki25056Census.Ref.scalar_factor; decide)
theorem agree_5 : ProofWiki25056Census.scalar_factor (-7) = ProofWiki25056Census.Ref.scalar_factor (-7) := by
  first
  | decide
  | rfl
  | (simp [ProofWiki25056Census.scalar_factor, ProofWiki25056Census.Ref.scalar_factor, ← Int.abs_eq_normalize])
  | (norm_num [ProofWiki25056Census.scalar_factor, ProofWiki25056Census.Ref.scalar_factor, ← Int.abs_eq_normalize])
  | (unfold ProofWiki25056Census.scalar_factor ProofWiki25056Census.Ref.scalar_factor; decide)
theorem agree_6 : ProofWiki25056Census.scalar_factor 5 = ProofWiki25056Census.Ref.scalar_factor 5 := by
  first
  | decide
  | rfl
  | (simp [ProofWiki25056Census.scalar_factor, ProofWiki25056Census.Ref.scalar_factor, ← Int.abs_eq_normalize])
  | (norm_num [ProofWiki25056Census.scalar_factor, ProofWiki25056Census.Ref.scalar_factor, ← Int.abs_eq_normalize])
  | (unfold ProofWiki25056Census.scalar_factor ProofWiki25056Census.Ref.scalar_factor; decide)
theorem agree_7 : ProofWiki25056Census.scalar_factor (-100) = ProofWiki25056Census.Ref.scalar_factor (-100) := by
  first
  | decide
  | rfl
  | (simp [ProofWiki25056Census.scalar_factor, ProofWiki25056Census.Ref.scalar_factor, ← Int.abs_eq_normalize])
  | (norm_num [ProofWiki25056Census.scalar_factor, ProofWiki25056Census.Ref.scalar_factor, ← Int.abs_eq_normalize])
  | (unfold ProofWiki25056Census.scalar_factor ProofWiki25056Census.Ref.scalar_factor; decide)
theorem agree_8 : ProofWiki25056Census.scalar_factor 3 = ProofWiki25056Census.Ref.scalar_factor 3 := by
  first
  | decide
  | rfl
  | (simp [ProofWiki25056Census.scalar_factor, ProofWiki25056Census.Ref.scalar_factor, ← Int.abs_eq_normalize])
  | (norm_num [ProofWiki25056Census.scalar_factor, ProofWiki25056Census.Ref.scalar_factor, ← Int.abs_eq_normalize])
  | (unfold ProofWiki25056Census.scalar_factor ProofWiki25056Census.Ref.scalar_factor; decide)
#print axioms agree_0
#print axioms agree_1
#print axioms agree_2
#print axioms agree_3
#print axioms agree_4
#print axioms agree_5
#print axioms agree_6
#print axioms agree_7
#print axioms agree_8
