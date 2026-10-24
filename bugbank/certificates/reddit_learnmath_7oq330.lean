import Mathlib.Data.Fintype.Fin
import Mathlib.Order.Fin.Basic
import Mathlib.Data.Fin.Basic
import Mathlib.Tactic.NormNum
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.Ring
import Mathlib.Tactic.FinCases
import Mathlib.Tactic.Tauto

/- Human-review repair, 2026-09-15.
The source-specific radius-two relation is the explicit disjunction of walks of length 0,1,2 over an actual finite vertex type. The tournament 0→1→2, 0→2 extends 0→1; its old sink 1 is unreachable from new vertex 2.
Historical source and human verdicts are preserved in the review packet. -/
namespace RedditLearnmath7oq330

def E (i j : Fin 3) : Prop := i < j

def reachesTwo (R : Fin 3 → Fin 3 → Prop) (i j : Fin 3) : Prop :=
  i = j ∨ R i j ∨ ∃ k, R i k ∧ R k j

theorem audited_counterexample :
    (∀ i j : Fin 3, i ≠ j → (E i j ∨ E j i)) ∧
    (∀ i : Fin 3, i < 2 → reachesTwo E i 1) ∧
    E 1 2 ∧ ¬ reachesTwo E 2 1 := by
  constructor
  · intro i j h
    exact lt_or_gt_of_ne h
  constructor
  · intro i hi
    fin_cases i <;> simp_all [reachesTwo, E]
  · constructor
    · exact (by decide : (1 : Fin 3) < 2)
    · simp [reachesTwo, E]
      decide

end RedditLearnmath7oq330
