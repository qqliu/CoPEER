import Mathlib.Analysis.SpecialFunctions.Sqrt
import Mathlib.Tactic

/-! The parity assertion in the supplied frozen source fails at the prime 3.
The certificate uses Mathlib's actual real square root and integer floor.
It certifies this local arithmetic claim and makes no claim about other
source versions or the final prime-gap theorem. -/
namespace Arxiv11081466v3SourceEnrichedCodex
noncomputable def endpoint (p : ℕ) : ℤ := ⌊(p:ℝ) + 2*Real.sqrt p⌋ + 1

theorem endpoint_three : endpoint 3 = 7 := by
  have hs := Real.sq_sqrt (by norm_num : (0:ℝ) ≤ 3)
  have hp := Real.sqrt_nonneg (3:ℝ)
  have hlo : (6:ℝ) ≤ 3 + 2*Real.sqrt 3 := by nlinarith
  have hhi : (3:ℝ) + 2*Real.sqrt 3 < 7 := by nlinarith
  have hf : ⌊(3:ℝ) + 2*Real.sqrt 3⌋ = (6:ℤ) := Int.floor_eq_iff.mpr ⟨by norm_num; exact hlo, by norm_num; exact hhi⟩
  simpa [endpoint,hf]

theorem refutes_prime_endpoint_even :
    Nat.Prime 3 ∧ endpoint 3 = 7 ∧ ¬ Even (endpoint 3) ∧ Nat.Prime (endpoint 3).toNat := by
  rw [endpoint_three]
  norm_num
  decide
end Arxiv11081466v3SourceEnrichedCodex
