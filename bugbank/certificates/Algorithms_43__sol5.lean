import Mathlib

open scoped BigOperators

set_option linter.style.nameCheck false

namespace QEDReview43sol5

/- Real, universal polar membership rather than an integer encoding. -/
abbrev Vec := ℝ × ℝ

def dot (y x : Vec) : ℝ := dotProduct ![y.1,y.2] ![x.1,x.2]

/-- The source uses a one-sided polar. Mathlib LinearMap.polar uses an absolute
value bound, so substituting that definition would change this problem. -/
def polar (S : Set Vec) : Set Vec := {y | ∀ x ∈ S, dot y x ≤ 1}

def Sbox : Set Vec := {x | x.1 ≤ 1 ∧ x.2 ≤ 1}

def Sprime : Set Vec := {x | 2 * x.1 ≤ 1}

theorem Algorithms_43__sol5_refuted :
    (0, 1) ∈ polar Sbox ∧
    dot (1, 0) (0, 3) ≤ 1 ∧
    dot (0, 1) (0, 3) > dot (0, 1) (1, 0) / 1 ∧
    dot (1, 1) (1, 0) ≤ 1 ∧ dot (1, 1) (0, 1) ≤ 1 ∧
    (1, 1) ∉ polar Sbox ∧
    (1, 0) ∈ polar Sprime ∧
    dot (1, 0) (2, 0) > 1 := by
  refine ⟨?_, by norm_num [dot, dotProduct, Fin.sum_univ_two], by norm_num [dot, dotProduct, Fin.sum_univ_two], by norm_num [dot, dotProduct, Fin.sum_univ_two],
    by norm_num [dot, dotProduct, Fin.sum_univ_two], ?_, ?_, by norm_num [dot, dotProduct, Fin.sum_univ_two]⟩
  · intro x hx
    simpa [dot, dotProduct, Fin.sum_univ_two] using hx.2
  · intro h
    have bad := h (1, 1) (by norm_num [Sbox])
    norm_num [dot, dotProduct, Fin.sum_univ_two] at bad
  · intro x hx
    change 2 * x.1 ≤ 1 at hx
    simpa [dot, dotProduct, Fin.sum_univ_two] using (show x.1 ≤ 1 by linarith)


end QEDReview43sol5
