import Mathlib.Topology.Algebra.InfiniteSum.Real
import Mathlib.Tactic.NormNum
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.Ring
import Mathlib.Tactic.FinCases
import Mathlib.Tactic.Tauto

/- Human-review repair, 2026-09-15.
Actual Mathlib summability and infinite sums replace stabilized finite sums. The absolute sum 1 differs from the signed sum -1 even under identity rearrangement; the valid rearrangement theorem preserves the signed sum.
Historical source and human verdicts are preserved in the review packet. -/
namespace RedditAskmath1837jgc

def a (n : ℕ) : ℝ := if n = 1 then -1 else 0

theorem audited_counterexample :
    Summable (fun n => |a n|) ∧
    (∑' n, |a n|) = 1 ∧ (∑' n, a n) = -1 ∧
    Function.Bijective (id : ℕ → ℕ) ∧ (∑' n, a (id n)) ≠ 1 := by
  have ha : HasSum a (-1) := by simpa [a] using (hasSum_ite_eq 1 (-1 : ℝ))
  have hab : HasSum (fun n => |a n|) 1 := by
    convert (hasSum_ite_eq 1 (1 : ℝ)) using 1
    ext n
    by_cases h : n=1 <;> simp [a,h]
  refine ⟨hab.summable, hab.tsum_eq, ha.tsum_eq, Function.bijective_id, ?_⟩
  norm_num [ha.tsum_eq]

end RedditAskmath1837jgc
