import Mathlib.Combinatorics.SimpleGraph.Connectivity.Finite
import Mathlib.Tactic
set_option autoImplicit false
set_option maxRecDepth 50000
set_option maxHeartbeats 2000000
namespace Arxiv1201_5203v4Mathlib
abbrev V := Fin 5
/-- Original bowtie: 0=c, 1=u, 2=a, 3=v, 4=b. -/
def G : SimpleGraph V := SimpleGraph.fromEdgeSet
  ({s(0,1),s(1,2),s(2,0),s(0,3),s(3,4),s(4,0)} : Set (Sym2 V))
instance : DecidableRel G.Adj := by unfold G; infer_instance
theorem connected : G.Connected := by decide
theorem bridgeless : ∀ e : Sym2 V, ¬G.IsBridge e := by
  intro e
  induction e using Sym2.inductionOn with
  | hf u v =>
    rw [SimpleGraph.isBridge_iff]
    fin_cases u <;> fin_cases v <;> decide
theorem side_preserved : ∀ u v : V,
    G.Adj u v → u ≠ 0 → v ≠ 0 → (u.val ≤ 2 ↔ v.val ≤ 2) := by decide
/-- The cut-vertex obstruction holds for walks of arbitrary length. -/
theorem avoiding_walk {u v : V} (p : G.Walk u v) (h : 0 ∉ p.support) :
    (u.val ≤ 2 ↔ v.val ≤ 2) := by
  induction p with
  | nil => rfl
  | @cons u w v huw p ih =>
    have hu : u ≠ 0 := by intro he; apply h; simp [he]
    have ht : 0 ∉ p.support := by intro hm; apply h; simp [hm]
    have hw : w ≠ 0 := by intro he; apply ht; simpa [he] using p.start_mem_support
    exact (side_preserved u w huw hu hw).trans (ih ht)
theorem every_walk_hits_c (p : G.Walk 1 3) : (0 : V) ∈ p.support := by
  by_contra h
  have := avoiding_walk p h
  norm_num at this
/-- The ordinary internal vertex set is the support with the two endpoints removed. -/
def interior (p : G.Walk 1 3) : Finset V := p.support.toFinset \ {1,3}
theorem c_internal (p : G.Walk 1 3) : (0 : V) ∈ interior p := by
  simp [interior, every_walk_hits_c p]
theorem original_witness_refutes :
    G.Connected ∧ (∀ e : Sym2 V, ¬G.IsBridge e) ∧
    ¬ ∃ p q : G.Walk 1 3,
      p.IsPath ∧ q.IsPath ∧ Disjoint (interior p) (interior q) := by
  refine ⟨connected,bridgeless,?_⟩
  rintro ⟨p,q,hp,hq,hd⟩
  exact Finset.disjoint_left.mp hd (c_internal p) (c_internal q)
end Arxiv1201_5203v4Mathlib
#print axioms Arxiv1201_5203v4Mathlib.original_witness_refutes
