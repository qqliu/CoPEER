import Mathlib.Combinatorics.SimpleGraph.Clique
import Mathlib.Data.Real.Archimedean
import Mathlib.Tactic.NormNum
import Mathlib.Tactic.Tauto

/-! Retains n=6,r=1. The graph is K3,3 plus edge {0,1}; it has the required
floor(n²/4)+1=10 edges. Triangle {0,1,3} is maximal in a disjoint triangle
packing, because the remaining graph is a two-edge star. Thus these numeric
parameters occur in the original proof, not just in its isolated inequality. -/
namespace MSE4515175
open scoped BigOperators

def graph : SimpleGraph (Fin 6) where
  Adj x y := (x < 3 ∧ 3 ≤ y) ∨ (y < 3 ∧ 3 ≤ x) ∨
    (x=0 ∧ y=1) ∨ (x=1 ∧ y=0)
  symm := by intro x y h; tauto
  loopless := ⟨by intro x h; rcases h with h|h|h|h <;> omega⟩
instance : DecidableRel graph.Adj := fun x y => inferInstanceAs (Decidable
  ((x < 3 ∧ 3 ≤ y) ∨ (y < 3 ∧ 3 ≤ x) ∨ (x=0 ∧ y=1) ∨ (x=1 ∧ y=0)))

def triangle : Finset (Fin 6) := {0,1,3}

theorem source_graph_hypotheses :
    graph.edgeFinset.card = 10 ∧ graph.IsClique (triangle : Set (Fin 6)) ∧
    triangle.card = 3 ∧
    (∀ S : Finset (Fin 6), Disjoint S triangle → graph.IsClique (S : Set (Fin 6)) → S.card ≤ 2) ∧
    graph.degree 0 + graph.degree 1 + graph.degree 3 ≤ 12 := by decide

noncomputable def printedLHS : ℝ :=
  (∑ i ∈ Finset.Icc (1 : ℕ) 1, (5*(6:ℝ)/2-3*i)) - 3 + ⌊((6-3:ℝ)^2)/4⌋
noncomputable def printedRHS : ℝ := ⌊((6:ℝ)^2)/4⌋

theorem certificate : printedLHS = 11 ∧ printedRHS = 9 ∧ ¬ printedLHS ≤ printedRHS := by
  norm_num [printedLHS, printedRHS]
end MSE4515175
