import Mathlib.Combinatorics.SimpleGraph.Acyclic
import Mathlib.Tactic.NormNum
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.Ring
import Mathlib.Tactic.FinCases
import Mathlib.Tactic.Tauto

/- Audit 2026-09-15. Historical source packets and human judgments remain unchanged. -/
namespace RedditAskmath1tgrwlt

def G : SimpleGraph (Fin 2) := ⊤
instance : DecidableRel G.Adj := fun _ _ => inferInstanceAs (Decidable (_ ≠ _))

def witnessWalk : G.Walk 0 1 :=
  .cons (v := 1) (by decide) (.cons (v := 0) (by decide) (.cons (by decide) .nil))

theorem audited_counterexample : G.IsTree ∧ witnessWalk.support = [0,1,0,1] ∧
    ¬ witnessWalk.IsPath := by
  refine ⟨?_, rfl, ?_⟩
  · rw [SimpleGraph.isTree_iff_connected_and_card]
    constructor
    · exact SimpleGraph.connected_top
    · rw [Nat.card_eq_fintype_card, Nat.card_eq_fintype_card]
      decide
  · simp [SimpleGraph.Walk.isPath_def, witnessWalk]

end RedditAskmath1tgrwlt
