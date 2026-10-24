import Mathlib

/-! The actual process reproduces first, then the original parent may die;
a newborn cannot die the same day. At population one the death probability
p*(1-1/N) is zero. Consequently the next size is one or two according to a
Bernoulli birth. This uses an actual Mathlib probability mass function and
removes the unrelated catastrophe / nearest-neighbour surrogate processes. -/
open scoped NNReal
namespace MSE3410112

noncomputable def deathProbability (p : ℝ) (N : ℕ) : ℝ := p * (1 - 1 / (N : ℝ))

theorem parent_cannot_die_at_one (p : ℝ) : deathProbability p 1 = 0 := by
  simp [deathProbability]

def nextSize (born : Bool) : ℕ := if born then 2 else 1

noncomputable def transitionFromOne (p : ℝ≥0) (h : p ≤ 1) : PMF ℕ :=
  (PMF.bernoulli p h).map nextSize

theorem extinction_probability_zero (p : ℝ≥0) (h : p ≤ 1) :
    transitionFromOne p h 0 = 0 := by
  rw [transitionFromOne, PMF.map_apply]
  simp [tsum_fintype, nextSize]

theorem certificate :
    deathProbability (1/3) 1 = 0 ∧
    transitionFromOne (1/3) (by exact (div_le_one (by norm_num)).2 (by norm_num)) 0 = 0 ∧
    ¬ 0 < transitionFromOne (1/3) (by exact (div_le_one (by norm_num)).2 (by norm_num)) 0 := by
  simp [parent_cannot_die_at_one, extinction_probability_zero]

theorem geometric_bound_no_decay (p : ℝ≥0) (h : p ≤ 1) (n : ℕ) :
    (1 - (transitionFromOne p h 0).toReal) ^ n = 1 := by
  simp [extinction_probability_zero]
end MSE3410112
