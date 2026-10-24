/-
Record: proofwiki_149536__codex_expansion
Source: https://proofwiki.org/wiki/Characterization_of_Natural_Transformation_Between_Bifunctors/Sufficient_Condition
Witness action: KEPT.

Keep the original Fin1-to-Fin3 witness in actual Mathlib FintypeCat: F(f)(0)=0,
G(f)(0)=1, alpha at the source=identity, alpha at the target maps 0→1, 1→2, 2→2.
Mathlib Functor and NatTrans enforce the full separate-naturality assumptions through
naturality for every product arrow. The printed equation produces 1=2 at 0. Source
line 82 has the typo, while line 100 already uses the corrected F. The surrounding
sufficient-condition theorem remains valid.
-/

import Mathlib.CategoryTheory.Category.Preorder
import Mathlib.CategoryTheory.Category.Cat
import Mathlib.CategoryTheory.Products.Basic
import Mathlib.CategoryTheory.Types.Basic
import Mathlib.CategoryTheory.FintypeCat
import Mathlib.CategoryTheory.Functor.Const
import Mathlib.CategoryTheory.Whiskering
import Mathlib.Order.BoundedOrder.Basic
import Mathlib.Data.Bool.Basic

open CategoryTheory
namespace ProofWiki149536CodexExpansion
abbrev D := Discrete Unit

def X : Bool → FintypeCat
  | false => FintypeCat.of (Fin 1)
  | true => FintypeCat.of (Fin 3)

def mapFn (v : Fin 3) : ∀ {a b : Bool}, (a ⟶ b) → (X a → X b)
  | false, false, _ => id
  | false, true, _ => fun _ => v
  | true, true, _ => id
  | true, false, f => False.elim ((by decide : ¬ (true ≤ false)) (leOfHom f))

def diagram (v : Fin 3) : Bool ⥤ FintypeCat where
  obj := X
  map f := FintypeCat.homMk (mapFn v f)
  map_id a := by cases a <;> rfl
  map_comp {a b c} f g := by
    have hf := leOfHom f
    have hg := leOfHom g
    cases a <;> cases b <;> cases c
    all_goals first | exact False.elim ((by decide : ¬ (true ≤ false)) hf) | exact False.elim ((by decide : ¬ (true ≤ false)) hg) | rfl

def alphaFn : ∀ a : Bool, X a → X a
  | false => id
  | true => fun (x : Fin 3) => if x = 0 then (1 : Fin 3) else (2 : Fin 3)

def alphaBase : diagram 0 ⟶ diagram 1 where
  app a := FintypeCat.homMk (alphaFn a)
  naturality {a b} f := by
    have hf := leOfHom f
    cases a <;> cases b
    all_goals first | exact False.elim ((by decide : ¬ (true ≤ false)) hf) | rfl

def F : Bool × D ⥤ FintypeCat := CategoryTheory.Prod.fst Bool D ⋙ diagram 0
def G : Bool × D ⥤ FintypeCat := CategoryTheory.Prod.fst Bool D ⋙ diagram 1
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
  have hval := congrArg (fun k : FintypeCat.of (Fin 1) ⟶ FintypeCat.of (Fin 3) => k 0) h
  change (1 : Fin 3) = 2 at hval
  exact (by decide : (1 : Fin 3) ≠ 2) hval
end ProofWiki149536CodexExpansion
