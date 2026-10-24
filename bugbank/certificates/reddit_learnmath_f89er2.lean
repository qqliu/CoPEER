import Mathlib.Data.Int.Basic
import Mathlib.Tactic.NormNum
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.Ring
import Mathlib.Tactic.FieldSimp
import Mathlib.Tactic.FinCases
import Mathlib.Tactic.Tauto
import Mathlib.Tactic.IntervalCases

/- Human-guided audit: The separately quantified lemma allows composite p; p=4,n=2 satisfies divisibility of n² but not n. The primality-like assumption earlier belongs to q, not lemma parameter p. Uses integer divisibility.
   Original witness action: KEPT. -/
namespace Audit_reddit_learnmath_f89er2
theorem certificate : (4 : ℤ) ∣ 2^2 ∧ ¬ (4 : ℤ) ∣ 2 := by norm_num
end Audit_reddit_learnmath_f89er2
