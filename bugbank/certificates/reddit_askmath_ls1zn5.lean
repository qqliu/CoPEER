import Mathlib.Combinatorics.SimpleGraph.Acyclic
import Mathlib.Combinatorics.SimpleGraph.Metric
import Mathlib.Tactic.NormNum
import Mathlib.Tactic.FinCases
import Mathlib.Tactic.Tauto

namespace RedditAskmathLs1zn5

def G : SimpleGraph (Fin 3) where
  Adj i j := (i=0 ∧ j=1) ∨ (i=1 ∧ j=0) ∨ (i=1 ∧ j=2) ∨ (i=2 ∧ j=1)
  symm := by intros a b h; tauto
  loopless := ⟨by intro i h; rcases h with h|h|h|h <;> omega⟩
instance : DecidableRel G.Adj := fun i j => inferInstanceAs (Decidable ((i=0 ∧ j=1) ∨ (i=1 ∧ j=0) ∨ (i=1 ∧ j=2) ∨ (i=2 ∧ j=1)))
def T : SimpleGraph (Fin 3) := ⊤
instance : DecidableRel T.Adj := fun _ _ => inferInstanceAs (Decidable (_ ≠ _))

theorem conn : G.Connected := by
  rw [SimpleGraph.connected_iff_exists_forall_reachable]
  refine ⟨1, ?_⟩
  intro w
  fin_cases w
  · exact SimpleGraph.Adj.reachable (by decide : G.Adj 1 0)
  · exact SimpleGraph.Reachable.refl 1
  · exact SimpleGraph.Adj.reachable (by decide : G.Adj 1 2)

theorem tree : G.IsTree := by
  rw [SimpleGraph.isTree_iff_connected_and_card]
  refine ⟨conn, ?_⟩
  rw [Nat.card_eq_fintype_card, Nat.card_eq_fintype_card]
  decide

theorem distance : G.dist 0 2 = 2 ∧ T.dist 0 2 = 1 := by
  constructor
  · have h : G.edist 0 2 = 2 := SimpleGraph.edist_eq_two_iff.mpr ⟨by decide, by decide, ⟨1, by decide⟩⟩
    simp [SimpleGraph.dist, h]
  · exact SimpleGraph.dist_eq_one_iff_adj.mpr (by decide)
theorem audited_counterexample :
    G.IsTree ∧ G ≤ T ∧ T.Connected ∧ ¬ T.IsTree ∧
    G.dist 0 2 = 2 ∧ T.dist 0 2 = 1 ∧ G.dist 0 2 ≠ T.dist 0 2 := by
  refine ⟨tree, le_top, SimpleGraph.connected_top, ?_, distance.1, distance.2, ?_⟩
  · intro h
    have hh := (SimpleGraph.isTree_iff_connected_and_card.mp h).2
    have ht : Nat.card T.edgeSet = 3 := by rw [Nat.card_eq_fintype_card]; decide
    rw [ht] at hh
    norm_num at hh
  · rw [distance.1,distance.2]; decide
end RedditAskmathLs1zn5
