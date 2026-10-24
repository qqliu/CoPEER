import Mathlib.Combinatorics.SimpleGraph.Clique
import Mathlib.Combinatorics.SimpleGraph.Connectivity.Finite
import Mathlib.Tactic
set_option autoImplicit false
namespace Arxiv1604_01374v4Mathlib
abbrev V := Fin 2
def G : SimpleGraph V := ⊤
instance : DecidableRel G.Adj := by unfold G; infer_instance
def idx (i : V) : Fin 3 := ⟨i.val+1,by omega⟩
def pair (i : V) : Finset (Fin 3) := {0,idx i}
/-- The source's two-branch vertex construction, including the degree>1 branch. -/
def constructed : Finset (Finset (Fin 3)) :=
  ((Finset.univ.filter (fun i => G.degree i = 1)).image pair) ∪
  (((Finset.univ.product Finset.univ).filter
    (fun ij : V × V => G.Adj ij.1 ij.2 ∧ 1 < G.degree ij.1)).image
      (fun ij => ({idx ij.1,idx ij.2} : Finset (Fin 3))))
/-- Vertices 0,1 encode precisely the two constructed pairs; injectivity and
surjectivity onto the constructed vertex set are proved in the headline. -/
def H : SimpleGraph V where
  Adj i j := i ≠ j ∧ (pair i ∩ pair j).Nonempty
  symm := by intro i j h; exact ⟨h.1.symm, by simpa [Finset.inter_comm] using h.2⟩
  loopless := ⟨by intro i h; exact h.1 rfl⟩
instance : DecidableRel H.Adj := by unfold H; infer_instance
instance (s : Finset V) : Decidable (H.IsClique (s : Set V)) := by
  unfold SimpleGraph.IsClique Set.Pairwise
  infer_instance
/-- Literal source edge-equivalence class, using actual unordered edges and
Mathlib clique membership for their union of endpoints. -/
def block (e : Sym2 V) : Finset V :=
  (H.edgeFinset.filter (fun f => H.IsClique (↑(e.toFinset ∪ f.toFinset)))).biUnion Sym2.toFinset
def blocks : Finset (Finset V) := H.edgeFinset.image block
abbrev BV := {s : Finset V // s ∈ blocks}
def B : SimpleGraph BV where
  Adj C D := C ≠ D ∧ (C.val ∩ D.val).Nonempty
  symm := by intro C D h; exact ⟨h.1.symm, by simpa [Finset.inter_comm] using h.2⟩
  loopless := ⟨by intro C h; exact h.1 rfl⟩
theorem construction_exact : constructed = Finset.univ.image pair := by decide
theorem pair_injective : Function.Injective pair := by decide
theorem block_count : Fintype.card BV = 1 := by decide
theorem not_isomorphic : ¬ Nonempty (B ≃g G) := by
  rintro ⟨h⟩
  have hc := Fintype.card_congr h.toEquiv
  rw [block_count] at hc
  norm_num at hc
theorem original_witness_refutes :
    G.Connected ∧ G.CliqueFree 3 ∧ (∀ i, G.degree i = 1) ∧
    constructed = Finset.univ.image pair ∧ Function.Injective pair ∧
    H.Adj 0 1 ∧ Fintype.card BV = 1 ∧ ¬ Nonempty (B ≃g G) := by
  refine ⟨by decide, ?_, by decide, construction_exact, pair_injective,
    by decide, block_count, not_isomorphic⟩
  exact SimpleGraph.cliqueFree_of_card_lt (by decide)
end Arxiv1604_01374v4Mathlib
#print axioms Arxiv1604_01374v4Mathlib.original_witness_refutes
