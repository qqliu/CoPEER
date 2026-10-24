import Mathlib

namespace QEDReview39sol3
/-- Frozen eight-vertex witness: two K₄s and cross edges 04 and 15. -/
def graph : SimpleGraph (Fin 8) where
  Adj u v := u ≠ v ∧ (u.val / 4 = v.val / 4 ∨
    (u = 0 ∧ v = 4) ∨ (u = 4 ∧ v = 0) ∨ (u = 1 ∧ v = 5) ∨ (u = 5 ∧ v = 1))
  symm := by intro u v h; exact ⟨h.1.symm, by rcases h.2 with h | h | h | h | h <;> aesop⟩
  loopless := ⟨fun u h => h.1 rfl⟩
instance : DecidableRel graph.Adj := fun _ _ => inferInstanceAs (Decidable (_ ∧ _))

def cross : Finset (Sym2 (Fin 8)) := {s(0,4),s(1,5)}
def leftSide : Set (Fin 8) := {v | v.val < 4}
instance : DecidablePred (fun v => v ∈ leftSide) := fun v => inferInstanceAs (Decidable (v.val < 4))

lemma degree_bound : ∀ v, 3 ≤ graph.degree v := by decide
/-- Uses Mathlib edge-connectivity, with quantification over every edge deletion. -/
lemma edgeConnected_two : graph.IsEdgeConnected 2 := by
  rw [SimpleGraph.isEdgeConnected_two]
  decide +kernel
lemma deleted_not_reachable : ¬ (graph.deleteEdges (↑cross)).Reachable 0 4 := by decide
lemma not_edgeReachable_three : ¬ graph.IsEdgeReachable 3 0 4 := by
  intro h
  apply deleted_not_reachable
  apply h
  rw [Set.encard_coe_eq_coe_finsetCard, show cross.card = 2 by decide]
  norm_num

/-- Exact induced-subgraph hypothesis: the frozen path 2--3 lies inside A. -/
def insidePath : (graph.induce leftSide).Walk ⟨2, by decide⟩ ⟨3, by decide⟩ :=
  .cons (by decide) .nil

lemma insidePath_isPath : insidePath.IsPath := by
  simp [insidePath, SimpleGraph.Walk.isPath_def]

/-- The graph satisfies the source branch with k=3 and lambda*=2. The lower bound
3-2=1 is compatible with the global lower bound2; it is not a contradiction.
The exact global minimum is witnessed by 2-edge-connectivity and the two-edge
cut separating0 from4. No cut enumeration or bounded reachability surrogate is used. -/
theorem refuted :
    (∀ v, 3 ≤ graph.degree v) ∧
    graph.IsEdgeConnected 2 ∧
    ¬ graph.IsEdgeReachable 3 0 4 ∧
    cross.card = 2 ∧
    (∀ u v, graph.Adj u v → (u ∈ leftSide ↔ v ∉ leftSide) → s(u,v) ∈ cross) ∧
    insidePath.IsPath ∧ (3 - 2 : ℕ) = 1 ∧ (1 : ℕ) < 2 ∧
    graph.IsEdgeReachable 2 2 3 := by
  exact ⟨degree_bound, edgeConnected_two, not_edgeReachable_three, by decide,
    by decide, insidePath_isPath, rfl, by decide, edgeConnected_two 2 3⟩
end QEDReview39sol3
