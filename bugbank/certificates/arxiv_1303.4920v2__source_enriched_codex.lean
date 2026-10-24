import Mathlib.Data.ZMod.Basic
import Mathlib.LinearAlgebra.Matrix.ToLin
import Mathlib.LinearAlgebra.BilinearForm.Orthogonal
import Mathlib.Tactic

/- The original diagonal length-two Z₄ code. All rings, codes, vector spaces,
   dot products, images and orthogonal complements are Mathlib objects. -/
namespace Arxiv13034920Mathlib
abbrev Q := Fin 2 → ZMod 4
abbrev BVec := Fin 2 × Fin 2 → ZMod 2

def C : Submodule (ZMod 4) Q where
  carrier := {x | x 0 = x 1}
  zero_mem' := rfl
  add_mem' {x} {y} hx hy := by change x 0 + y 0 = x 1 + y 1; rw [hx,hy]
  smul_mem' a x hx := by change a * _ = a * _; rw [hx]

def B : Submodule (ZMod 2) BVec where
  carrier := {x | ∀ j, x (0,j) = x (1,j)}
  zero_mem' := by intro j; rfl
  add_mem' {x} {y} hx hy := by intro j; change x (0,j) + y (0,j) = x (1,j) + y (1,j); rw [hx j,hy j]
  smul_mem' a x hx := by intro j; change a * _ = a * _; rw [hx j]

/-- The usual Gray table 0 ↦ 00, 1 ↦ 01, 2 ↦ 11, 3 ↦ 10. -/
def grayBit (a : ZMod 4) (j : Fin 2) : ZMod 2 :=
  if j = 0 then if a = 2 ∨ a = 3 then 1 else 0
  else if a = 1 ∨ a = 2 then 1 else 0

def gray (x : Q) : BVec := fun ij => grayBit (x ij.1) ij.2

theorem gray_image_exact : gray '' (C : Set Q) = (B : Set BVec) := by
  have h : ∀ y : BVec, (∃ x : Q, x 0 = x 1 ∧ gray x = y) ↔
      ∀ j, y (0,j) = y (1,j) := by decide
  exact Set.ext h

theorem binary_self_dual :
    B.orthogonalBilin (dotProductBilin (ZMod 2) (ZMod 2)) = B := by
  ext x
  change (∀ y : BVec, (∀ j, y (0,j) = y (1,j)) → dotProduct y x = 0) ↔
    (∀ j, x (0,j) = x (1,j))
  exact (by decide : ∀ x : BVec,
    (∀ y : BVec, (∀ j, y (0,j) = y (1,j)) → dotProduct y x = 0) ↔
    (∀ j, x (0,j) = x (1,j))) x

theorem quaternary_not_self_dual :
    C.orthogonalBilin (dotProductBilin (ZMod 4) (ZMod 4)) ≠ C := by
  intro h
  have hx : (fun _ : Fin 2 => (1 : ZMod 4)) ∈ C := rfl
  have ho : (fun _ : Fin 2 => (1 : ZMod 4)) ∈
      C.orthogonalBilin (dotProductBilin (ZMod 4) (ZMod 4)) := by rw [h]; exact hx
  have hz := ho (fun _ : Fin 2 => (1 : ZMod 4)) hx
  exact (by decide : ¬ dotProduct (fun _ : Fin 2 => (1 : ZMod 4))
    (fun _ : Fin 2 => (1 : ZMod 4)) = 0) hz

/-- A binary-linear self-dual Gray image, while the original Z₄-linear code
    is not self-dual: the literal source converse fails at length two. -/
theorem original_witness_refutes :
    gray '' (C : Set Q) = (B : Set BVec) ∧
    B.orthogonalBilin (dotProductBilin (ZMod 2) (ZMod 2)) = B ∧
    C.orthogonalBilin (dotProductBilin (ZMod 4) (ZMod 4)) ≠ C :=
  ⟨gray_image_exact, binary_self_dual, quaternary_not_self_dual⟩
end Arxiv13034920Mathlib
#print axioms Arxiv13034920Mathlib.original_witness_refutes
