import Mathlib.LinearAlgebra.Matrix.Determinant.Basic
import Mathlib.Tactic

/-! The standalone multilinearity proposition gives a signed permutation sum
for arbitrary independently decomposed columns. The two nonzero selected
components below give I₂, while the asserted sum is -1. All matrices and
determinants use Mathlib rather than an arithmetic determinant surrogate. -/
namespace Arxiv12077033v2SourceEnrichedCodex
open Matrix
abbrev V := Fin 2 → ℤ
def c11 : V := ![0,0]
def c12 : V := ![1,0]
def c21 : V := ![0,1]
def c22 : V := ![0,0]
def fromCols (u v : V) : Matrix (Fin 2) (Fin 2) ℤ :=
  ![u,v]ᵀ
def M := fromCols (0 • c11 + 1 • c12) (1 • c21 + 0 • c22)
def assertedPermutationSum : ℤ :=
  (0*0) * (fromCols c11 c22).det - (1*1) * (fromCols c12 c21).det

theorem refutes_signed_permutation_multilinearity :
    M = (1 : Matrix (Fin 2) (Fin 2) ℤ) ∧ M.det = 1 ∧
    assertedPermutationSum = -1 ∧ M.det ≠ assertedPermutationSum := by
  norm_num [M, fromCols, c11,c12,c21,c22,assertedPermutationSum,Matrix.det_fin_two]
  decide
end Arxiv12077033v2SourceEnrichedCodex
