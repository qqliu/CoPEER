import Mathlib.Algebra.Group.Pointwise.Set.Basic
import Mathlib.Data.Real.Basic
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.NormNum
set_option autoImplicit false
open scoped Pointwise
namespace ProofCerts.Alg48
/-- Real polyhedron A=[-1], b=0. -/
def P : Set ℝ := {x | -x ≤ 0}
/-- Its recession cone. -/
def C : Set ℝ := {d | -d ≤ 0}
theorem recession_cone : C = {d : ℝ | ∀ x ∈ P, ∀ t : ℝ, 0 ≤ t → x + t*d ∈ P} := by
  ext d
  constructor
  · intro hd x hx t ht
    dsimp [C] at hd
    dsimp [P] at hx ⊢
    have : 0 ≤ t*d := mul_nonneg ht (by linarith)
    linarith
  · intro h
    have := h 0 (by simp [P]) 1 (by norm_num)
    simpa [P,C] using this
/-- Mathlib pointwise subtraction is exactly the Minkowski difference. -/
theorem minkowski_difference_ne_halfspace : P - C ≠ P := by
  intro h
  have hz : (-1 : ℝ) ∈ P - C := by
    exact Set.mem_sub.mpr ⟨0, by simp [P], 1, by norm_num [C], by norm_num⟩
  rw [h] at hz
  norm_num [P] at hz
theorem original_witness_refutes_claim :
    P.Nonempty ∧
    C = {d : ℝ | ∀ x ∈ P, ∀ t : ℝ, 0 ≤ t → x + t*d ∈ P} ∧
    P - C ≠ P :=
  ⟨⟨0, by simp [P]⟩, recession_cone, minkowski_difference_ne_halfspace⟩
end ProofCerts.Alg48
#print axioms ProofCerts.Alg48.original_witness_refutes_claim
