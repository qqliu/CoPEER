import Mathlib.Data.Int.Basic
import Mathlib.Tactic.NormNum
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.Ring
import Mathlib.Tactic.FinCases
import Mathlib.Tactic.Tauto

/- Human-review repair, 2026-09-15.
Typographical factorization error at q=0. This isolates the displayed arithmetic identity, not the prime >3 case or its true 6k±1 conclusion.
Historical source and human verdicts are preserved in the review packet. -/
namespace RedditAskmath1bq1jtc

theorem audited_counterexample :
    (6*(0 : ℤ)+2) ≠ 2*(3*0+2) := by norm_num

end RedditAskmath1bq1jtc
