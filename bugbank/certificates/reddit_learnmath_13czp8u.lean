import Mathlib.Data.Real.Basic
import Mathlib.LinearAlgebra.Matrix.Notation
import Mathlib.LinearAlgebra.Matrix.ToLin
import Mathlib.Tactic.NormNum
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.Ring
import Mathlib.Tactic.FinCases
import Mathlib.Tactic.Tauto

/- Human-review repair, 2026-09-15.
Real Mathlib matrix and vector operations certify column stochasticity and a nonzero eigenvector with eigenvalue -1, including both positive entries of A+I and its nontrivial kernel.
Historical source and human verdicts are preserved in the review packet. -/
namespace RedditLearnmath13czp8u

open Matrix

def A : Matrix (Fin 2) (Fin 2) ℝ := !![0,1;1,0]
def v : Fin 2 → ℝ := ![1,-1]

theorem audited_counterexample :
    (∀ i j, 0 ≤ A i j) ∧ (∀ j, ∑ i, A i j = 1) ∧
    v ≠ 0 ∧ A.mulVec v = (-1 : ℝ) • v ∧
    (∀ i j, 0 < (A+1) i j) ∧ (A+1).mulVec v = 0 := by
  refine ⟨?_, ?_, ?_, ?_, ?_, ?_⟩
  · intro i j; fin_cases i <;> fin_cases j <;> norm_num [A]
  · intro j; fin_cases j <;> norm_num [A, Fin.sum_univ_two]
  · intro h
    have := congrFun h 0
    norm_num [v] at this
  · ext i; fin_cases i <;> norm_num [A, v, mulVec, dotProduct, Fin.sum_univ_two]
  · intro i j; fin_cases i <;> fin_cases j <;> norm_num [A, Matrix.one_apply]
  · ext i; fin_cases i <;> norm_num [A, v, mulVec, dotProduct, Fin.sum_univ_two]

end RedditLearnmath13czp8u
