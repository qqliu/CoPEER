import Mathlib
/-! The original S3 witness. H1=G, H2=N2={1,(12)}, N1=G.
Normality in H2 does not imply normality in H1. This refutes only the
printed normality assertion; the Zassenhaus conclusion remains true. -/
namespace ProofWiki13715CodexExpansion
abbrev G := Equiv.Perm (Fin 3)
def N2 : Subgroup G := MulAction.stabilizer G (2 : Fin 3)
def n : G := Equiv.swap 0 1
def g : G := Equiv.swap 0 1 * Equiv.swap 1 2

theorem n_mem : n ∈ N2 := by
  change n 2 = 2
  decide

theorem normal_in_H2 : (N2.comap N2.subtype).Normal := by
  have h : N2.comap N2.subtype = ⊤ := by
    ext x
    simp [Subgroup.mem_comap]
  rw [h]
  infer_instance

theorem not_normal_in_H1 : ¬ N2.Normal := by
  intro h
  have hc := h.conj_mem n n_mem g
  exact (by change (g * n * g⁻¹) 2 ≠ 2; decide : g * n * g⁻¹ ∉ N2) hc

theorem refutes_intersection_normality :
    (N2.comap N2.subtype).Normal ∧
    ¬ ((⊤ : Subgroup G) ⊓ N2).Normal := by
  simpa using And.intro normal_in_H2 not_normal_in_H1
end ProofWiki13715CodexExpansion
