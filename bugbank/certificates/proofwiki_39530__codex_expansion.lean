import Mathlib
/-! Keep the original two-point Sierpinski witness. Prop has exactly the two
points False and True (by propositional extensionality), with opens empty,
{True}, and univ. This is the original {0,1} witness relabeled 0=False,1=True.
No metric hypothesis occurs in the source theorem. -/
namespace ProofWiki39530CodexExpansion
open Set Topology

def A : Set Prop := {False}
def U : Set Prop := (closure A)ᶜ

theorem closure_A : closure A = {False} := by
  have h : ({False} : Set Prop) = ({True} : Set Prop)ᶜ := by
    ext p
    simp only [mem_singleton_iff, mem_compl_iff]
    by_cases hp : p <;> simp [hp]
  rw [A, h]
  exact isOpen_singleton_true.isClosed_compl.closure_eq

theorem closure_U : closure U = univ := by
  have hu : U = ({True} : Set Prop) := by
    ext p
    simp only [U, closure_A, mem_compl_iff, mem_singleton_iff]
    by_cases hp : p <;> simp [hp]
  rw [hu]
  ext p
  by_cases hp : p
  · have he : p = True := propext (iff_true_intro hp)
    rw [he]
    simp [subset_closure (mem_singleton True)]
  · have he : p = False := propext (iff_false_intro hp)
    rw [he]
    simp [mem_closure_iff_nhds, nhds_false]

theorem refutes_published_membership_equivalence :
    closure A = {False} ∧ closure U = univ ∧
    False ∈ interior (closure U) ∧ False ∉ U ∧
    ¬ (∀ x : Prop, x ∈ interior (closure U) ↔ x ∈ U) := by
  have hin : False ∈ interior (closure U) := by simp [closure_U]
  have hout : False ∉ U := by simp [U, closure_A]
  exact ⟨closure_A, closure_U, hin, hout, fun h => hout ((h False).mp hin)⟩
end ProofWiki39530CodexExpansion
