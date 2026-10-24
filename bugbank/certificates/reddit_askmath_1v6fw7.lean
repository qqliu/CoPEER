import Mathlib.Combinatorics.SimpleGraph.Acyclic
import Mathlib.Combinatorics.SimpleGraph.Metric
import Mathlib.Combinatorics.SimpleGraph.Coloring.VertexColoring
import Mathlib.Tactic.NormNum
import Mathlib.Tactic.FinCases
import Mathlib.Tactic.Tauto

namespace RedditAskmath1v6fw7

def oldG : SimpleGraph (Fin 2) := ⊤
def newG : SimpleGraph (Fin 3) where
  Adj i j := i ≠ j ∧ (i=0 ∨ j=0)
  symm := by intros a b h; exact ⟨h.1.symm,h.2.symm⟩
  loopless := ⟨by simp⟩
instance : DecidableRel oldG.Adj := fun _ _ => inferInstanceAs (Decidable (_ ≠ _))
instance : DecidableRel newG.Adj := fun i j => inferInstanceAs (Decidable (i ≠ j ∧ (i=0 ∨ j=0)))

def oldOdd : Finset (Fin 2) := Finset.univ.filter (fun v => newG.Adj 2 v.castSucc ∧ Odd (oldG.degree v))
def oldEven : Finset (Fin 2) := Finset.univ.filter (fun v => newG.Adj 2 v.castSucc ∧ Even (oldG.degree v))

/-- The same original graph and inserted leaf; the literal second case repeats the first. -/
theorem audited_counterexample :
    (∀ i j : Fin 2, oldG.Adj i j ↔ newG.Adj i.castSucc j.castSucc) ∧
    oldG.degree 0 = 1 ∧ oldG.degree 1 = 1 ∧ newG.degree 2 = 1 ∧
    oldOdd.card = 1 ∧ oldEven.card = 0 ∧ Odd (newG.degree 2) ∧
    ¬ ((Even oldOdd.card ∧ Odd oldEven.card) ∨ (Odd oldEven.card ∧ Even oldOdd.card)) := by
  decide
end RedditAskmath1v6fw7
