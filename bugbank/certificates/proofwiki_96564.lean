import Mathlib
/-! The source's complex-style product is Mathlib's quadratic algebra over
ZMod 5 with generator square -1. Its nonzero zero divisors obstruct inverses. -/
namespace ProofWiki96564
abbrev F := ZMod 5
abbrev E := QuadraticAlgebra F (-1) 0

def witness : E := ⟨1, 2⟩
def annihilator : E := ⟨1, 3⟩

theorem witness_nonzero : witness ≠ 0 := by
  intro h
  have := congrArg QuadraticAlgebra.re h
  exact (by decide : (1 : F) ≠ 0) this

theorem annihilator_nonzero : annihilator ≠ 0 := by
  intro h
  have := congrArg QuadraticAlgebra.re h
  exact (by decide : (1 : F) ≠ 0) this

theorem product_zero : witness * annihilator = 0 := by
  ext <;> norm_num [witness, annihilator] <;> decide

theorem refutes_unrestricted_direct_product_field_claim :
    witness ≠ 0 ∧ annihilator ≠ 0 ∧ witness * annihilator = 0 ∧
    witness.re ^ 2 + witness.im ^ 2 = 0 ∧
    ¬ (∃ y : E, witness * y = 1) := by
  refine ⟨witness_nonzero, annihilator_nonzero, product_zero, ?_, ?_⟩
  · decide
  · rintro ⟨y, hy⟩
    apply annihilator_nonzero
    calc
      annihilator = 1 * annihilator := (one_mul _).symm
      _ = (witness * y) * annihilator := by rw [hy]
      _ = y * (witness * annihilator) := by ring
      _ = 0 := by rw [product_zero, mul_zero]

theorem negative_control_unity_has_inverse : ∃ y : E, 1 * y = 1 := ⟨1, one_mul 1⟩
end ProofWiki96564
