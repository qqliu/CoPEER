import Mathlib

/-! The equality-only-at-one assertion fails at the permitted endpoint n=1.
Use actual complex powers, finite sums and the complex norm. The original
root-free polynomial theorem remains true. -/
namespace G3refPnv146
noncomputable def powerSum (z : ℂ) (n : ℕ) : ℂ := ∑ k ∈ Finset.range n, z ^ (k + 1)

theorem refutes_equality_only_at_one :
    0 < (1 : ℕ) ∧ ‖(-1 : ℂ)‖ ≤ 1 ∧
    ‖powerSum (-1) 1‖ = 1 ∧ (-1 : ℂ) ≠ 1 := by
  norm_num [powerSum]

theorem negative_control_n_two_breaks_equality :
    powerSum (-1) 2 = 0 ∧ ‖powerSum (-1) 2‖ < 2 := by
  norm_num [powerSum, Finset.sum_range_succ]
end G3refPnv146
