import Mathlib.Tactic.NormNum
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.Ring
import Mathlib.Tactic.FieldSimp
import Mathlib.Tactic.FinCases
import Mathlib.Tactic.Tauto
import Mathlib.Tactic.IntervalCases

/- Human-guided audit: Original I={3} violates the explicitly proved base I(1). Replace by I={1,3}, keeping n=3;2 is a smaller positive noninteresting number than4. This addresses the same invalid weak-induction minimality inference.
   Original witness action: REPLACED_INVALID. -/
namespace Audit_reddit_mathematics_i3ob36
def I (k : ℕ) : Prop := k = 1 ∨ k = 3
theorem certificate : I 1 ∧ I 3 ∧ ¬ I 4 ∧ ¬ I 2 ∧ (0 < (2 : ℕ) ∧ 2 < 4) := by norm_num [I]
end Audit_reddit_mathematics_i3ob36
