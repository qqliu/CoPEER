/-
Record: proofwiki_149255__codex_expansion
Source: https://proofwiki.org/wiki/Characterization_of_Natural_Transformation_Between_Bifunctors
Witness action: KEPT.

Keep the original walking arrow, terminal second category, Bool objects,
F(f)=identity, G(f)=Bool.not, alpha at zero=identity and alpha at one=Bool.not.
Mathlib Bool preorder, Discrete Unit, actual product categories, Functor and NatTrans
now enforce all structural assumptions. The final theorem establishes naturality on
every product morphism and refutes the printed equation at false. Source line 218
prints G on the right; line 236 already uses the correct F. This is a local displayed
typo; the main characterization is not refuted.
-/

import Mathlib.CategoryTheory.Category.Preorder
import Mathlib.CategoryTheory.Category.Cat
import Mathlib.CategoryTheory.Products.Basic
import Mathlib.CategoryTheory.Types.Basic
import Mathlib.CategoryTheory.Functor.Const
import Mathlib.CategoryTheory.Whiskering
import Mathlib.Order.BoundedOrder.Basic
import Mathlib.Data.Bool.Basic

open CategoryTheory
namespace ProofWiki149255CodexExpansion
abbrev D := Discrete Unit

def X : Bool → Type
  | false => Bool
  | true => Bool

def mapFn (v : Bool) : ∀ {a b : Bool}, (a ⟶ b) → (X a → X b)
  | false, false, _ => id
  | false, true, _ => if v then Bool.not else id
  | true, true, _ => id
  | true, false, f => False.elim ((by decide : ¬ (true ≤ false)) (leOfHom f))

def diagram (v : Bool) : Bool ⥤ Type where
  obj := X
  map f := TypeCat.ofHom (mapFn v f)
  map_id a := by cases a <;> rfl
  map_comp {a b c} f g := by
    have hf := leOfHom f
    have hg := leOfHom g
    cases a <;> cases b <;> cases c
    all_goals first | exact False.elim ((by decide : ¬ (true ≤ false)) hf) | exact False.elim ((by decide : ¬ (true ≤ false)) hg) | rfl

def alphaBase : diagram false ⟶ diagram true where
  app a := TypeCat.ofHom (match a with | false => id | true => Bool.not)
  naturality {a b} f := by
    have hf := leOfHom f
    cases a <;> cases b
    all_goals first | exact False.elim ((by decide : ¬ (true ≤ false)) hf) | rfl

def F : Bool × D ⥤ Type := CategoryTheory.Prod.fst Bool D ⋙ diagram false
def G : Bool × D ⥤ Type := CategoryTheory.Prod.fst Bool D ⋙ diagram true
def alpha : F ⟶ G := Functor.whiskerLeft (CategoryTheory.Prod.fst Bool D) alphaBase

def a : Bool × D := (false, ⟨()⟩)
def b : Bool × D := (true, ⟨()⟩)
def f : a ⟶ b := (homOfLE (by decide), 𝟙 _)

theorem genuine_naturality : F.map f ≫ alpha.app b = alpha.app a ≫ G.map f :=
  alpha.naturality f

theorem refutes_printed_equation :
    (∀ {p q : Bool × D} (g : p ⟶ q),
      F.map g ≫ alpha.app q = alpha.app p ≫ G.map g) ∧
    (alpha.app a ≫ G.map f ≠ G.map f ≫ alpha.app b) := by
  refine ⟨fun g => alpha.naturality g, ?_⟩
  intro h
  have hval := congrArg (fun k : Bool ⟶ Bool => k false) h
  change true = false at hval
  cases hval
end ProofWiki149255CodexExpansion
