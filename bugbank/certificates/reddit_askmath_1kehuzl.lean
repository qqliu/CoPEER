import Mathlib.Data.Finset.Card
import Mathlib.Algebra.Ring.Parity
import Mathlib.Tactic.NormNum
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.Ring
import Mathlib.Tactic.FinCases
import Mathlib.Tactic.Tauto

/- Human-review repair, 2026-09-15.
Positive witness {2,4} removes the human reviewer’s zero-in-the-naturals ambiguity. It is not any consecutive pair, even before the evenness restriction.
Historical source and human verdicts are preserved in the review packet. -/
namespace RedditAskmath1kehuzl

theorem audited_counterexample :
    ({2,4} : Finset ℕ).card = 2 ∧
    (∀ n ∈ ({2,4} : Finset ℕ), 0 < n) ∧
    ¬ ∃ n : ℕ, Even n ∧ ({n,n+1} : Finset ℕ) = {2,4} := by
  refine ⟨by decide, by simp, ?_⟩
  rintro ⟨n, _, h⟩
  have hn : n ∈ ({2,4} : Finset ℕ) := h ▸ (by simp : n ∈ ({n,n+1} : Finset ℕ))
  have hs : n+1 ∈ ({2,4} : Finset ℕ) := h ▸ (by simp : n+1 ∈ ({n,n+1} : Finset ℕ))
  simp only [Finset.mem_insert, Finset.mem_singleton] at hn hs
  omega

end RedditAskmath1kehuzl
