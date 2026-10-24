import Mathlib.Tactic
namespace Arxiv09100923v4SourceEnrichedCodex
noncomputable def lambdaBound (n : ℕ) : ℤ := ⌈((n:ℝ)-1)/2⌉
theorem refutes_largest_even_assertion :
    lambdaBound 3 = 1 ∧ 2 * lambdaBound 3 = 2 ∧
    (4:ℤ) ∈ Finset.Icc 1 (3+1) ∧ Even (4:ℤ) ∧ 2*lambdaBound 3 < 4 := by
  have h : lambdaBound 3 = 1 := by norm_num [lambdaBound]
  rw [h]
  norm_num
/-- The original packet also documents all odd n=2k+1; retain that existing family. -/
theorem original_odd_family (k : ℕ) (hk : 1 ≤ k) :
    lambdaBound (2*k+1) = (k : ℤ) ∧
    (2*(k : ℤ)+2) ∈ Finset.Icc 1 (((2*k+1 : ℕ) : ℤ)+1) ∧
    Even (2*(k : ℤ)+2) ∧ 2*lambdaBound (2*k+1) < 2*(k : ℤ)+2 := by
  have hr : (((2*k+1 : ℕ) : ℝ)-1)/2 = (k : ℝ) := by push_cast; ring
  have hl : lambdaBound (2*k+1) = (k : ℤ) := by unfold lambdaBound; rw [hr]; simp
  refine ⟨hl, ?_, ?_, ?_⟩
  · simp only [Finset.mem_Icc]; constructor <;> omega
  · exact ⟨(k : ℤ)+1, by ring⟩
  · rw [hl]; omega
end Arxiv09100923v4SourceEnrichedCodex
