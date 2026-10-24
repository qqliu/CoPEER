/-
Record: proofwiki_148090__codex_expansion
Source: https://proofwiki.org/wiki/Slice_Category_is_Isomorphic_to_Identity_Functor_Over_Object_Comma_Category
Witness action: KEPT.

The original thin category 0<1 is Mathlib Bool with its preorder category. F has the
required terminal domain and selects true (1). The declared input category is
CostructuredArrow (identity) true, the printed input label is StructuredArrow true F,
and the target is Comma (identity) F. The original x=(false,*,false→true) is kept.
Every printed-domain input indexes only an object with left object true, so neither x
nor its identity has a supplied clause. Correcting the domain labels gives an actual
identity functor on the standard comma presentation. This certifies the literal
incomplete definition, not falsity of the intended slice-category isomorphism.
-/

import Mathlib.CategoryTheory.Category.Preorder
import Mathlib.CategoryTheory.Comma.StructuredArrow.Basic
import Mathlib.Data.Bool.Basic

open CategoryTheory
namespace ProofWiki148090CodexExpansion

-- The same terminal-source functor is both C-hat and the source's F.
def F : Discrete PUnit.{1} ⥤ Bool := Functor.fromPUnit.{0} true
abbrev DeclaredDomain := CostructuredArrow (𝟭 Bool) true
abbrev WrittenDomain := StructuredArrow true F
abbrev Codomain := Comma (𝟭 Bool) F

def x : DeclaredDomain := CostructuredArrow.mk (homOfLE (by decide : false ≤ true))
def y : DeclaredDomain := CostructuredArrow.mk (𝟙 true)
def onlyWrittenObject : WrittenDomain := StructuredArrow.mk (Y := ⟨PUnit.unit⟩) (𝟙 true)

-- Even after translating the written domain's terminal index into C, every
-- supplied object case has left object true. It cannot supply the case x.
def writtenInput : WrittenDomain ⥤ DeclaredDomain where
  obj z := CostructuredArrow.mk (Y := F.obj z.right) z.hom
  map f := CostructuredArrow.homMk (F.map f.right) (by apply Subsingleton.elim)

def ObjectHasCase (z : DeclaredDomain) : Prop := ∃ w, writtenInput.obj w = z

def IdentityHasCase (z : DeclaredDomain) : Prop :=
  ∃ w : WrittenDomain, ∃ h : writtenInput.obj w = z,
    eqToHom h.symm ≫ writtenInput.map (𝟙 w) ≫ eqToHom h = 𝟙 z

-- Replacing both erroneous domain labels by the declared domain gives this
-- actual Mathlib functor: the standard tuple map (E,g) ↦ (E,*,g).
def repairedFunctor : DeclaredDomain ⥤ Codomain := 𝟭 _

theorem x_has_no_written_case : ¬ ObjectHasCase x := by
  rintro ⟨w, h⟩
  have hv := congrArg (fun z : DeclaredDomain => z.left) h
  change true = false at hv
  cases hv

theorem refutes_literal_I2_functor_definition :
    ¬ ObjectHasCase x ∧ ¬ IdentityHasCase x ∧
    ¬ Function.Surjective writtenInput.obj ∧
    ObjectHasCase y ∧
    repairedFunctor.obj x = (x : Codomain) ∧
    repairedFunctor.map (𝟙 x) = 𝟙 (repairedFunctor.obj x) := by
  refine ⟨x_has_no_written_case, ?_, ?_, ⟨onlyWrittenObject, rfl⟩, rfl, rfl⟩
  · rintro ⟨w, h, _⟩
    exact x_has_no_written_case ⟨w, h⟩
  · intro h
    exact x_has_no_written_case (h x)

end ProofWiki148090CodexExpansion
