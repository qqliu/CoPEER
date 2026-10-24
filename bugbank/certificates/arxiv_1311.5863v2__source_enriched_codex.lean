import Mathlib.Combinatorics.SimpleGraph.Paths
import Mathlib.Combinatorics.SimpleGraph.Subgraph
import Mathlib.Tactic
set_option autoImplicit false
namespace Arxiv1311_5863v2Mathlib
abbrev V := Fin 3
def G : SimpleGraph V := ⊤
instance : DecidableRel G.Adj := by unfold G; infer_instance
/-- K3 has only three edges: every cycle, being a trail, has length at most three.
Hence it has no induced cycle of length at least four, the source definition of chordal. -/
theorem no_long_cycles : ∀ v (p : G.Walk v v), p.IsCycle → p.length < 4 := by
  intro v p hp
  have h := hp.isTrail.length_le_card_edgeFinset
  have hc : G.edgeFinset.card = 3 := by decide
  rw [hc] at h
  omega
/-- Even arbitrary subgraphs with proper vertex sets cannot paste to K3;
requiring their intersection to be a clique only restricts them further. -/
theorem no_proper_pasting : ∀ H₁ H₂ : G.Subgraph,
    H₁.verts ≠ Set.univ → H₂.verts ≠ Set.univ → H₁ ⊔ H₂ ≠ ⊤ := by
  intro H₁ H₂ h₁ h₂ h
  have hex₁ : ∃ x, x ∉ H₁.verts := by
    by_contra hn
    apply h₁
    ext x
    simp only [Set.mem_univ, iff_true]
    by_contra hx
    exact hn ⟨x,hx⟩
  have hex₂ : ∃ y, y ∉ H₂.verts := by
    by_contra hn
    apply h₂
    ext y
    simp only [Set.mem_univ, iff_true]
    by_contra hy
    exact hn ⟨y,hy⟩
  obtain ⟨x,hx⟩ := hex₁
  obtain ⟨y,hy⟩ := hex₂
  have hxy : x ≠ y := by
    intro heq
    have hm : x ∈ (H₁ ⊔ H₂).verts := by rw [h]; trivial
    change x ∈ H₁.verts ∨ x ∈ H₂.verts at hm
    exact hm.elim hx (fun ha => hy (heq ▸ ha))
  have ha : (H₁ ⊔ H₂).Adj x y := by rw [h]; exact hxy
  rcases ha with ha | ha
  · exact hx (H₁.edge_vert ha)
  · exact hy (H₂.edge_vert ha.symm)
theorem original_witness_refutes :
    (∀ v (p : G.Walk v v), p.IsCycle → p.length < 4) ∧
    ∀ H₁ H₂ : G.Subgraph,
      H₁.verts ≠ Set.univ → H₂.verts ≠ Set.univ → H₁ ⊔ H₂ ≠ ⊤ :=
  ⟨no_long_cycles,no_proper_pasting⟩
end Arxiv1311_5863v2Mathlib
#print axioms Arxiv1311_5863v2Mathlib.original_witness_refutes
