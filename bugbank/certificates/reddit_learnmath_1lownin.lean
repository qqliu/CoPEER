import Mathlib.LinearAlgebra.LinearIndependent.Basic
import Mathlib.Data.Real.Basic
import Mathlib.LinearAlgebra.Matrix.Determinant.Basic
import Mathlib.LinearAlgebra.LinearIndependent.Defs
import Mathlib.Tactic.NormNum
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.Ring
import Mathlib.Tactic.FieldSimp
import Mathlib.Tactic.FinCases
import Mathlib.Tactic.Tauto
import Mathlib.Tactic.IntervalCases

/- Human-guided audit: m=n=2,r=1, A=(1,0)ᵀ and B=(1,0) satisfy actual LinearIndependent hypotheses but AB has determinant zero. Uses Mathlib matrix multiplication and invertibility.
   Original witness action: KEPT. -/
namespace Audit_reddit_learnmath_1lownin
def A : Matrix (Fin 2) (Fin 1) ℝ := fun i _ => if i = 0 then 1 else 0
def B : Matrix (Fin 1) (Fin 2) ℝ := fun _ j => if j = 0 then 1 else 0
theorem certificate : LinearIndependent ℝ (fun j : Fin 1 => fun i : Fin 2 => A i j) ∧
    LinearIndependent ℝ (fun i => B i) ∧ ¬ IsUnit (A * B) := by
  have hn : (fun i : Fin 2 => if i = 0 then (1 : ℝ) else 0) ≠ 0 := by
    intro h; have := congrFun h 0; norm_num at this
  refine ⟨?_, ?_, ?_⟩
  · exact linearIndependent_unique_iff.mpr hn
  · exact linearIndependent_unique_iff.mpr hn
  · intro h
    have hd := h.map (Matrix.detMonoidHom : Matrix (Fin 2) (Fin 2) ℝ →* ℝ)
    have hz : (A*B).det = 0 := by norm_num [Matrix.det_fin_two, Matrix.mul_apply, A, B, Fin.sum_univ_one]
    simpa [hz] using hd
end Audit_reddit_learnmath_1lownin
