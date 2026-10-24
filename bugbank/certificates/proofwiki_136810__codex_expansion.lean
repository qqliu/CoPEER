/-
Record: proofwiki_136810__codex_expansion
Source: https://proofwiki.org/wiki/Locale_Isomorphism_is_Isomorphism_in_Loc
Witness action: KEPT.

The original C2 and C3 are exactly the finite chains Fin 2 and Fin 3. Their
complete lattice and frame structures come from Mathlib. The endpoint map
sends 0 to 0 and 1 to 2. Its FrameHom proves preservation of top, binary meets,
and arbitrary joins (not merely a sampled finite check). Its opposite is an
actual Mathlib Locale morphism. The missing middle element 1 prevents a
categorical inverse, refuting the printed local equivalence at source line17.
The surrounding theorem about locale isomorphisms remains true. The earlier
source lines explicitly mention a frame isomorphism; the error is the omitted
'isomorphism' condition in this subsequent displayed definition. The final
Mathlib isIso_op_iff supplies the corrected statement, and the original
identity control remains an isomorphism.
-/

import Mathlib.Topology.Category.Locale
import Mathlib.Data.Fintype.Order
import Mathlib.Tactic.FinCases

open CategoryTheory Opposite
namespace ProofWiki136810CodexExpansion
noncomputable section

def endpoint (x : Fin 2) : Fin 3 := if x = 0 then 0 else 2

def endpointFrameHom : FrameHom (Fin 2) (Fin 3) where
  toFun := endpoint
  map_top' := rfl
  map_inf' := by intro x y; fin_cases x <;> fin_cases y <;> decide
  map_sSup' s := by
    classical
    by_cases h1 : (1 : Fin 2) ∈ s
    · have hs : sSup s = (1 : Fin 2) := top_unique (le_sSup h1)
      have ht : sSup (endpoint '' s) = (2 : Fin 3) :=
        top_unique (le_sSup ⟨1, h1, rfl⟩)
      rw [hs, ht]
      rfl
    · have hs : sSup s = (0 : Fin 2) := by
        apply bot_unique
        apply sSup_le
        intro x hx
        fin_cases x
        · exact le_rfl
        · exact False.elim (h1 hx)
      have ht : sSup (endpoint '' s) = (0 : Fin 3) := by
        apply bot_unique
        apply sSup_le
        rintro y ⟨x, hx, rfl⟩
        fin_cases x
        · exact le_rfl
        · exact False.elim (h1 hx)
      rw [hs, ht]
      rfl

def h : Frm.of (Fin 2) ⟶ Frm.of (Fin 3) := Frm.ofHom endpointFrameHom
def f : Locale.of (Fin 3) ⟶ Locale.of (Fin 2) := h.op

theorem middle_missing (x : Fin 2) : endpoint x ≠ (1 : Fin 3) := by
  fin_cases x <;> decide

theorem not_locale_isomorphism : ¬ IsIso f := by
  intro hf
  haveI : IsIso h := (isIso_op_iff h).mp hf
  have hh := congrArg (fun m : Frm.of (Fin 3) ⟶ Frm.of (Fin 3) => m (1 : Fin 3))
    (IsIso.inv_hom_id h)
  change endpoint ((inv h) (1 : Fin 3)) = (1 : Fin 3) at hh
  exact middle_missing _ hh

theorem refutes_published_locale_equivalence :
    (∃ k : Frm.of (Fin 2) ⟶ Frm.of (Fin 3), f = k.op) ∧
    ¬ IsIso f ∧
    ¬ (IsIso f ↔ ∃ k : Frm.of (Fin 2) ⟶ Frm.of (Fin 3), f = k.op) := by
  refine ⟨⟨h, rfl⟩, not_locale_isomorphism, ?_⟩
  intro hc
  exact not_locale_isomorphism (hc.mpr ⟨h, rfl⟩)

-- Mathlib supplies the corrected condition: the frame map must be an isomorphism.
theorem corrected_opposition {A B : Frm} (k : A ⟶ B) : IsIso k.op ↔ IsIso k :=
  isIso_op_iff k

theorem negative_control_identity_op_is_locale_isomorphism :
    IsIso ((𝟙 (Frm.of (Fin 2))).op) := by infer_instance

end
end ProofWiki136810CodexExpansion
