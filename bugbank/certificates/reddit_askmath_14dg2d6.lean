import Mathlib.Analysis.SpecialFunctions.Trigonometric.Basic
import Mathlib.LinearAlgebra.Matrix.Notation
import Mathlib.Tactic.NormNum
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.Ring
import Mathlib.Tactic.FinCases
import Mathlib.Tactic.Tauto

/- Human-review repair, 2026-09-15.
The real matrices are right-handed 90-degree rotations about x,y,z. Their transposes are the corresponding negative rotations. Negating angles in the same composition order produces S with (SR)00=-1, so S is not the inverse.
Historical source and human verdicts are preserved in the review packet. -/
namespace RedditAskmath14dg2d6

open Matrix

def Rx : Matrix (Fin 3) (Fin 3) ℝ := !![1,0,0;0,0,-1;0,1,0]
def Ry : Matrix (Fin 3) (Fin 3) ℝ := !![0,0,1;0,1,0;-1,0,0]
def Rz : Matrix (Fin 3) (Fin 3) ℝ := !![0,-1,0;1,0,0;0,0,1]
def R := Rz*Ry*Rx
def S := Rz.transpose*Ry.transpose*Rx.transpose

theorem audited_counterexample :
    Real.cos (Real.pi/2) = 0 ∧ Real.sin (Real.pi/2) = 1 ∧
    Rx.transpose * Rx = 1 ∧ Ry.transpose * Ry = 1 ∧ Rz.transpose * Rz = 1 ∧
    (S*R) 0 0 = -1 ∧ S*R ≠ 1 := by
  have hv : (S*R) 0 0 = -1 := by
    norm_num [Rx,Ry,Rz,R,S,Matrix.mul_apply,Fin.sum_univ_succ]
  refine ⟨Real.cos_pi_div_two, Real.sin_pi_div_two, ?_, ?_, ?_, hv, ?_⟩
  · ext i j; fin_cases i <;> fin_cases j <;> norm_num [Rx,Matrix.mul_apply,Fin.sum_univ_succ,Matrix.one_apply]
  · ext i j; fin_cases i <;> fin_cases j <;> norm_num [Ry,Matrix.mul_apply,Fin.sum_univ_succ,Matrix.one_apply]
  · ext i j; fin_cases i <;> fin_cases j <;> norm_num [Rz,Matrix.mul_apply,Fin.sum_univ_succ,Matrix.one_apply]
  · intro h
    have hh := congrArg (fun M : Matrix (Fin 3) (Fin 3) ℝ => M 0 0) h
    change (S*R) 0 0 = (1 : Matrix (Fin 3) (Fin 3) ℝ) 0 0 at hh
    rw [hv] at hh
    norm_num at hh
end RedditAskmath14dg2d6
