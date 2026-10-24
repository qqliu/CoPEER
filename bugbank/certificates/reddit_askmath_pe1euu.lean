import Mathlib.Combinatorics.SimpleGraph.Acyclic
import Mathlib.Combinatorics.SimpleGraph.Metric
import Mathlib.Combinatorics.SimpleGraph.Coloring.VertexColoring
import Mathlib.Tactic.NormNum
import Mathlib.Tactic.FinCases
import Mathlib.Tactic.Tauto

namespace RedditAskmathPe1euu

/-- Original triangle predecessor was not two-colorable. Replace it by the even square
0--1--2--3--0; insert leaf 4 adjacent only to 0. This challenges the SAME tree conclusion. -/
def G : SimpleGraph (Fin 5) where
  Adj i j := (i<4 ∧ j<4 ∧ i.val%2 ≠ j.val%2) ∨ (i=0 ∧ j=4) ∨ (i=4 ∧ j=0)
  symm := by intros a b h; rcases h with ⟨ha,hb,h⟩|h|h; exact Or.inl ⟨hb,ha,h.symm⟩; exact Or.inr (Or.inr h.symm); exact Or.inr (Or.inl h.symm)
  loopless := ⟨by intro i h; rcases h with h|h|h <;> omega⟩
instance : DecidableRel G.Adj := fun i j => inferInstanceAs (Decidable ((i<4 ∧ j<4 ∧ i.val%2 ≠ j.val%2) ∨ (i=0 ∧ j=4) ∨ (i=4 ∧ j=0)))

def square : G.Walk 0 0 :=
  .cons (v:=1) (by decide) (.cons (v:=2) (by decide) (.cons (v:=3) (by decide) (.cons (by decide) .nil)))

def coloring : G.Coloring (Fin 2) where
  toFun := fun i => if i=0 ∨ i=2 then 0 else 1
  map_rel' := by intro i j h; fin_cases i <;> fin_cases j <;> simp_all [G,SimpleGraph.top_adj]

def predecessor := G.induce {v : Fin 5 | v < 4}

def predecessorColoring : predecessor.Coloring (Fin 2) where
  toFun v := coloring v.val
  map_rel' := fun h => coloring.map_rel h

theorem no_new_cycle (w : G.Walk 4 4) : ¬ w.IsCycle := by
  intro h
  have hs := w.adj_snd h.not_nil
  have hp := (w.adj_penultimate h.not_nil).symm
  have hs0 : w.snd = 0 := by simpa [G] using hs
  have hp0 : w.penultimate = 0 := by simpa [G] using hp
  exact h.snd_ne_penultimate (hs0.trans hp0.symm)

theorem audited_counterexample :
    G.Connected ∧ G.Colorable 2 ∧ predecessor.Colorable 2 ∧
    (∀ v, G.Adj 4 v ↔ v=0) ∧
    (∀ w : G.Walk 4 4, ¬ w.IsCycle) ∧
    square.IsCycle ∧ ¬ G.IsTree := by
  have hc : square.IsCycle := by
    simp [SimpleGraph.Walk.isCycle_def,SimpleGraph.Walk.isTrail_def,square]
  refine ⟨?_, ⟨coloring⟩, ⟨predecessorColoring⟩, by decide, no_new_cycle, hc, fun h => h.isAcyclic square hc⟩
  rw [SimpleGraph.connected_iff_exists_forall_reachable]
  refine ⟨0, ?_⟩
  intro w
  fin_cases w
  · exact SimpleGraph.Reachable.refl 0
  · exact SimpleGraph.Adj.reachable (by decide : G.Adj 0 1)
  · exact (SimpleGraph.Adj.reachable (by decide : G.Adj 0 1)).trans (SimpleGraph.Adj.reachable (by decide : G.Adj 1 2))
  · exact SimpleGraph.Adj.reachable (by decide : G.Adj 0 3)
  · exact SimpleGraph.Adj.reachable (by decide : G.Adj 0 4)
end RedditAskmathPe1euu
