import Mathlib.LinearAlgebra.Matrix.ToLin
import Mathlib.LinearAlgebra.FiniteDimensional.Basic
import Mathlib.Data.ZMod.Basic
import Mathlib.Tactic.LinearCombination
import Mathlib.Tactic.NormNum
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.Ring
import Mathlib.Tactic.FinCases

/- Human-guided audit: The unchanged 4-cycle has boundary matrix columns corresponding exactly to edges12,23,34,41 over ZMod2. Its actual linear kernel is linearly equivalent to ZMod2, hence dimension1≠4−2. Replaces bespoke Boolean span/basis notions.
   Original witness action: KEPT. -/
namespace Audit_reddit_math_2mw3v2
open scoped BigOperators
abbrev F := ZMod 2
-- Column j is the boundary of edge (j,j+1 mod4), in source edge order.
def boundary : Matrix (Fin 4) (Fin 4) F := !![1,0,0,1;1,1,0,0;0,1,1,0;0,0,1,1]
def cycles : Submodule F (Fin 4 → F) := LinearMap.ker boundary.mulVecLin
lemma classify (x : Fin 4 → F) : x ∈ cycles ↔ ∀ i, x i = x 0 := by
  have h : ∀ x : Fin 4 → F, boundary.mulVec x = 0 ↔ ∀ i, x i = x 0 := by decide
  exact h x
noncomputable def coeff : cycles ≃ₗ[F] F where
  toFun x := x.val 0
  invFun t := ⟨fun _ => t, (classify _).2 (by simp)⟩
  left_inv x := by apply Subtype.ext; funext i; exact ((classify _).1 x.property i).symm
  right_inv t := rfl
  map_add' x y := rfl
  map_smul' t x := rfl
theorem dimension_certificate : Module.finrank F cycles = 1 ∧ Module.finrank F cycles ≠ 4-2 := by
  have h := coeff.finrank_eq
  norm_num at h
  exact ⟨h, by omega⟩
theorem certificate :
    (∀ v e : Fin 4, boundary v e = if v = e ∨ v = e+1 then 1 else 0) ∧
    Module.finrank F cycles = 1 ∧ Module.finrank F cycles ≠ 4-2 :=
  ⟨by decide, dimension_certificate⟩
end Audit_reddit_math_2mw3v2
