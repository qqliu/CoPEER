import Mathlib
/-! Original disjoint singleton sets S={0},T={1}, with bijection0↦1.
Use Mathlib relations and image to retain domains in the swapped-identity
comparison. A function's graph, not an ill-typed homogeneous function
comparison, is the common set-theoretic representation used by the source. -/
namespace ProofWiki145181
abbrev E := Fin 2
def f : SetRel E E := {(0,1)}
def idS : SetRel E E := {(0,0)}

theorem bijection_on_singletons :
    (∀ x : E, x ∈ ({0} : Set E) → ∃! y : E, y ∈ ({1} : Set E) ∧ (x,y) ∈ f) ∧
    (∀ y : E, y ∈ ({1} : Set E) → ∃! x : E, x ∈ ({0} : Set E) ∧ (x,y) ∈ f) := by
  simp [f]

theorem refutes_swapped_identity_subscripts :
    (1,1) ∈ f.inv.comp f ∧ (1,1) ∉ idS ∧ f.inv.comp f ≠ idS ∧
    SetRel.image f (SetRel.image f.inv {1}) = {1} ∧
    SetRel.image f (SetRel.image f.inv {1}) ≠ ({0} : Set E) := by
  have hm : (1,1) ∈ f.inv.comp f := ⟨0, by simp [f], by simp [f]⟩
  have hn : (1,1) ∉ idS := by simp [idS]
  have him : SetRel.image f (SetRel.image f.inv {1}) = {1} := by
    ext y
    fin_cases y <;> simp [f,SetRel.image,SetRel.inv,Fin.exists_fin_succ]
  refine ⟨hm, hn, fun h => hn (h ▸ hm), him, ?_⟩
  rw [him]
  intro h
  have hh := Set.ext_iff.mp h (1 : E)
  simpa using hh

/-- Compare the two direct-image expressions from the challenged line on
the original singleton {1}. The image under the graph of identity on S={0}
is empty here, whereas the image under f after its inverse is {1}. -/
theorem refutes_swapped_direct_image_identity :
    SetRel.image idS ({1} : Set E) = ∅ ∧
    SetRel.image f (SetRel.image f.inv {1}) ≠ SetRel.image idS {1} := by
  have hid : SetRel.image idS ({1} : Set E) = ∅ := by
    ext y
    fin_cases y <;> simp [idS, SetRel.image, Fin.exists_fin_succ]
  refine ⟨hid, ?_⟩
  rw [refutes_swapped_identity_subscripts.2.2.2.1, hid]
  simp
end ProofWiki145181
