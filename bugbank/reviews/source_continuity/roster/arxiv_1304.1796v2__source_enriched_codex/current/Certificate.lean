import Mathlib.Tactic
namespace Arxiv13041796v2SourceEnrichedCodex
/- The old p₀=1 violated the source definition. Keep a=3 and the same k-family,
using the required probability p₀=(1-1/k)^k. Strict failure holds for every k≥3. -/
noncomputable def p₀ (k : ℕ) : ℝ := (1-1/(k:ℝ))^k
theorem refutes_upper_bound_with_source_probability (k : ℕ) (hk : 3 ≤ k) :
    0 < p₀ k ∧
    p₀ k * (1+2/((k:ℝ)-1))^(3-1) >
      p₀ k * (1+2*(3-1)/((k:ℝ)-1)) := by
  have hkR : (3:ℝ) ≤ k := by exact_mod_cast hk
  have hp : 0 < p₀ k := by
    apply pow_pos
    have : 1/(k:ℝ) < 1 := (div_lt_one (by linarith)).mpr (by linarith)
    linarith
  refine ⟨hp,mul_lt_mul_of_pos_left ?_ hp⟩
  have hpos : 0 < 2/((k:ℝ)-1) := div_pos (by norm_num) (by linarith)
  have he : 2*(3-1)/((k:ℝ)-1) = 2*(2/((k:ℝ)-1)) := by ring
  rw [he]
  norm_num only [Nat.reduceSub]
  nlinarith [sq_pos_of_pos hpos]
end Arxiv13041796v2SourceEnrichedCodex
