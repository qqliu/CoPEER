import SUBMISSION
import reference
set_option linter.unreachableTactic false
set_option linter.unusedTactic false
/- EVALUATOR-ONLY hidden-instance agreement for E16: the submitted line condition must be equivalent to the reference
y = x at the listed points (on the line and off it, including points of the source's claimed line x + y = 0). -/
theorem agree_0 : ProofWiki120506CodexExpansion.onImageLine ((0 : ℝ), (0 : ℝ)) ↔ ProofWiki120506CodexExpansion.Ref.onImageLine ((0 : ℝ), (0 : ℝ)) := by
  first
  | (simp only [ProofWiki120506CodexExpansion.onImageLine, ProofWiki120506CodexExpansion.Ref.onImageLine]; norm_num)
  | (norm_num [ProofWiki120506CodexExpansion.onImageLine, ProofWiki120506CodexExpansion.Ref.onImageLine])
  | (constructor <;> intro h <;> simp_all [ProofWiki120506CodexExpansion.onImageLine, ProofWiki120506CodexExpansion.Ref.onImageLine] <;> linarith)
theorem agree_1 : ProofWiki120506CodexExpansion.onImageLine ((1 : ℝ), (1 : ℝ)) ↔ ProofWiki120506CodexExpansion.Ref.onImageLine ((1 : ℝ), (1 : ℝ)) := by
  first
  | (simp only [ProofWiki120506CodexExpansion.onImageLine, ProofWiki120506CodexExpansion.Ref.onImageLine]; norm_num)
  | (norm_num [ProofWiki120506CodexExpansion.onImageLine, ProofWiki120506CodexExpansion.Ref.onImageLine])
  | (constructor <;> intro h <;> simp_all [ProofWiki120506CodexExpansion.onImageLine, ProofWiki120506CodexExpansion.Ref.onImageLine] <;> linarith)
theorem agree_2 : ProofWiki120506CodexExpansion.onImageLine ((-2 : ℝ), (-2 : ℝ)) ↔ ProofWiki120506CodexExpansion.Ref.onImageLine ((-2 : ℝ), (-2 : ℝ)) := by
  first
  | (simp only [ProofWiki120506CodexExpansion.onImageLine, ProofWiki120506CodexExpansion.Ref.onImageLine]; norm_num)
  | (norm_num [ProofWiki120506CodexExpansion.onImageLine, ProofWiki120506CodexExpansion.Ref.onImageLine])
  | (constructor <;> intro h <;> simp_all [ProofWiki120506CodexExpansion.onImageLine, ProofWiki120506CodexExpansion.Ref.onImageLine] <;> linarith)
theorem agree_3 : ProofWiki120506CodexExpansion.onImageLine ((1/2 : ℝ), (1/2 : ℝ)) ↔ ProofWiki120506CodexExpansion.Ref.onImageLine ((1/2 : ℝ), (1/2 : ℝ)) := by
  first
  | (simp only [ProofWiki120506CodexExpansion.onImageLine, ProofWiki120506CodexExpansion.Ref.onImageLine]; norm_num)
  | (norm_num [ProofWiki120506CodexExpansion.onImageLine, ProofWiki120506CodexExpansion.Ref.onImageLine])
  | (constructor <;> intro h <;> simp_all [ProofWiki120506CodexExpansion.onImageLine, ProofWiki120506CodexExpansion.Ref.onImageLine] <;> linarith)
theorem agree_4 : ProofWiki120506CodexExpansion.onImageLine ((3 : ℝ), (3 : ℝ)) ↔ ProofWiki120506CodexExpansion.Ref.onImageLine ((3 : ℝ), (3 : ℝ)) := by
  first
  | (simp only [ProofWiki120506CodexExpansion.onImageLine, ProofWiki120506CodexExpansion.Ref.onImageLine]; norm_num)
  | (norm_num [ProofWiki120506CodexExpansion.onImageLine, ProofWiki120506CodexExpansion.Ref.onImageLine])
  | (constructor <;> intro h <;> simp_all [ProofWiki120506CodexExpansion.onImageLine, ProofWiki120506CodexExpansion.Ref.onImageLine] <;> linarith)
theorem agree_5 : ProofWiki120506CodexExpansion.onImageLine ((-1 : ℝ), (-1 : ℝ)) ↔ ProofWiki120506CodexExpansion.Ref.onImageLine ((-1 : ℝ), (-1 : ℝ)) := by
  first
  | (simp only [ProofWiki120506CodexExpansion.onImageLine, ProofWiki120506CodexExpansion.Ref.onImageLine]; norm_num)
  | (norm_num [ProofWiki120506CodexExpansion.onImageLine, ProofWiki120506CodexExpansion.Ref.onImageLine])
  | (constructor <;> intro h <;> simp_all [ProofWiki120506CodexExpansion.onImageLine, ProofWiki120506CodexExpansion.Ref.onImageLine] <;> linarith)
theorem agree_6 : ProofWiki120506CodexExpansion.onImageLine ((1 : ℝ), (-1 : ℝ)) ↔ ProofWiki120506CodexExpansion.Ref.onImageLine ((1 : ℝ), (-1 : ℝ)) := by
  first
  | (simp only [ProofWiki120506CodexExpansion.onImageLine, ProofWiki120506CodexExpansion.Ref.onImageLine]; norm_num)
  | (norm_num [ProofWiki120506CodexExpansion.onImageLine, ProofWiki120506CodexExpansion.Ref.onImageLine])
  | (constructor <;> intro h <;> simp_all [ProofWiki120506CodexExpansion.onImageLine, ProofWiki120506CodexExpansion.Ref.onImageLine] <;> linarith)
theorem agree_7 : ProofWiki120506CodexExpansion.onImageLine ((-2 : ℝ), (2 : ℝ)) ↔ ProofWiki120506CodexExpansion.Ref.onImageLine ((-2 : ℝ), (2 : ℝ)) := by
  first
  | (simp only [ProofWiki120506CodexExpansion.onImageLine, ProofWiki120506CodexExpansion.Ref.onImageLine]; norm_num)
  | (norm_num [ProofWiki120506CodexExpansion.onImageLine, ProofWiki120506CodexExpansion.Ref.onImageLine])
  | (constructor <;> intro h <;> simp_all [ProofWiki120506CodexExpansion.onImageLine, ProofWiki120506CodexExpansion.Ref.onImageLine] <;> linarith)
theorem agree_8 : ProofWiki120506CodexExpansion.onImageLine ((0 : ℝ), (1 : ℝ)) ↔ ProofWiki120506CodexExpansion.Ref.onImageLine ((0 : ℝ), (1 : ℝ)) := by
  first
  | (simp only [ProofWiki120506CodexExpansion.onImageLine, ProofWiki120506CodexExpansion.Ref.onImageLine]; norm_num)
  | (norm_num [ProofWiki120506CodexExpansion.onImageLine, ProofWiki120506CodexExpansion.Ref.onImageLine])
  | (constructor <;> intro h <;> simp_all [ProofWiki120506CodexExpansion.onImageLine, ProofWiki120506CodexExpansion.Ref.onImageLine] <;> linarith)
theorem agree_9 : ProofWiki120506CodexExpansion.onImageLine ((1 : ℝ), (0 : ℝ)) ↔ ProofWiki120506CodexExpansion.Ref.onImageLine ((1 : ℝ), (0 : ℝ)) := by
  first
  | (simp only [ProofWiki120506CodexExpansion.onImageLine, ProofWiki120506CodexExpansion.Ref.onImageLine]; norm_num)
  | (norm_num [ProofWiki120506CodexExpansion.onImageLine, ProofWiki120506CodexExpansion.Ref.onImageLine])
  | (constructor <;> intro h <;> simp_all [ProofWiki120506CodexExpansion.onImageLine, ProofWiki120506CodexExpansion.Ref.onImageLine] <;> linarith)
theorem agree_10 : ProofWiki120506CodexExpansion.onImageLine ((2 : ℝ), (3 : ℝ)) ↔ ProofWiki120506CodexExpansion.Ref.onImageLine ((2 : ℝ), (3 : ℝ)) := by
  first
  | (simp only [ProofWiki120506CodexExpansion.onImageLine, ProofWiki120506CodexExpansion.Ref.onImageLine]; norm_num)
  | (norm_num [ProofWiki120506CodexExpansion.onImageLine, ProofWiki120506CodexExpansion.Ref.onImageLine])
  | (constructor <;> intro h <;> simp_all [ProofWiki120506CodexExpansion.onImageLine, ProofWiki120506CodexExpansion.Ref.onImageLine] <;> linarith)
theorem agree_11 : ProofWiki120506CodexExpansion.onImageLine ((-1 : ℝ), (1 : ℝ)) ↔ ProofWiki120506CodexExpansion.Ref.onImageLine ((-1 : ℝ), (1 : ℝ)) := by
  first
  | (simp only [ProofWiki120506CodexExpansion.onImageLine, ProofWiki120506CodexExpansion.Ref.onImageLine]; norm_num)
  | (norm_num [ProofWiki120506CodexExpansion.onImageLine, ProofWiki120506CodexExpansion.Ref.onImageLine])
  | (constructor <;> intro h <;> simp_all [ProofWiki120506CodexExpansion.onImageLine, ProofWiki120506CodexExpansion.Ref.onImageLine] <;> linarith)
theorem agree_12 : ProofWiki120506CodexExpansion.onImageLine ((1 : ℝ), (2 : ℝ)) ↔ ProofWiki120506CodexExpansion.Ref.onImageLine ((1 : ℝ), (2 : ℝ)) := by
  first
  | (simp only [ProofWiki120506CodexExpansion.onImageLine, ProofWiki120506CodexExpansion.Ref.onImageLine]; norm_num)
  | (norm_num [ProofWiki120506CodexExpansion.onImageLine, ProofWiki120506CodexExpansion.Ref.onImageLine])
  | (constructor <;> intro h <;> simp_all [ProofWiki120506CodexExpansion.onImageLine, ProofWiki120506CodexExpansion.Ref.onImageLine] <;> linarith)
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
#print axioms agree_12
