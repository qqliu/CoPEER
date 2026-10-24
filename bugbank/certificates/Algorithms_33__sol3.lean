import Mathlib
namespace QEDReview33sol3
abbrev V := Fin 4
def graph : SimpleGraph V := SimpleGraph.fromEdgeSet {s(0,1),s(1,2),s(2,3),s(0,3)}
instance : DecidableRel graph.Adj := by unfold graph; infer_instance
abbrev S : Set V := {0,2}
abbrev T : Set V := {1,3}
def block : Finset (Sym2 V) := {s(0,1)}
def cut0 : Finset (Sym2 V) := graph.edgeFinset.filter (fun e => (0 : V) ∈ e)
lemma inducedS : graph.induce S = ⊥ := by
  ext u v
  change graph.Adj u.val v.val ↔ False
  have hu : u.val = 0 ∨ u.val = 2 := u.property
  have hv : v.val = 0 ∨ v.val = 2 := v.property
  rcases hu with hu | hu <;> rcases hv with hv | hv <;> rw [hu,hv] <;> decide
lemma inducedT : graph.induce T = ⊥ := by
  ext u v
  change graph.Adj u.val v.val ↔ False
  have hu : u.val = 1 ∨ u.val = 3 := u.property
  have hv : v.val = 1 ∨ v.val = 3 := v.property
  rcases hu with hu | hu <;> rcases hv with hv | hv <;> rw [hu,hv] <;> decide
/-- Original C₄ witness: the chosen induced components are singletons,
and deleting their sole connecting edge leaves the whole graph connected. -/
theorem refuted : graph.Connected ∧
    graph.induce S = ⊥ ∧ graph.induce T = ⊥ ∧
    (∀ u v : V, u ∈ S → v ∈ T → u = 0 → v = 1 → graph.Adj u v) ∧
    cut0 = {s(0,1),s(0,3)} ∧ block.Nonempty ∧ block ≠ cut0 ∧
    (graph.deleteEdges (↑block)).Connected := by
  refine ⟨by decide, inducedS, inducedT, ?_⟩
  decide
end QEDReview33sol3
