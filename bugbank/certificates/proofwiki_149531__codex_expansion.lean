/-
Record: proofwiki_149531__codex_expansion
Source: https://proofwiki.org/wiki/Characterization_of_Natural_Transformation_Between_Bifunctors/Proof_2
Witness action: KEPT.

Keep the original walking arrow with Unit at the source and Bool at the target,
F(f)(*)=false, G(f)(*)=true, alpha at the source=identity and alpha at the
target=Bool.not. Actual Mathlib Functor and NatTrans structures prove naturality for
all product arrows. The printed G-on-both-sides equation yields true=false at *. The
challenged equation occurs in the sufficient condition at source line 76, not the
correct equation3 in the necessary condition at line 9. Source line 94 already uses
the correct F. The main characterization remains valid.
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
namespace ProofWiki149531CodexExpansion
abbrev D := Discrete Unit

def X : Bool → Type
  | false => Unit
  | true => Bool

def mapFn (v : Bool) : ∀ {a b : Bool}, (a ⟶ b) → (X a → X b)
  | false, false, _ => id
  | false, true, _ => fun _ => v
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
  have hval := congrArg (fun k : Unit ⟶ Bool => k ()) h
  change true = false at hval
  cases hval
end ProofWiki149531CodexExpansion
