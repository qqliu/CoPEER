import Mathlib
/-! Actual real-valued unconditional sums (nets over Finsets) and absolute
convergence replace the old eventual-constancy surrogate. The identity
enumeration includes zero, as explicitly specified in the source. -/
namespace ProofWiki117692CodexExpansion

def v (n : ℕ) : ℝ := if n = 0 then 1 else 0

theorem full_sum : HasSum v 1 := hasSum_ite_eq 0 1

theorem absolute_full_sum : HasSum (fun n => ‖v n‖) 1 := by
  have hv : (fun n => ‖v n‖) = v := by
    funext n
    simp only [v]
    split_ifs <;> norm_num
  rw [hv]
  exact full_sum

theorem tail_sum : HasSum (fun n => v (n + 1)) 0 := by
  simpa [v] using (hasSum_zero (α := ℝ) (β := ℕ))

theorem absolute_tail_sum : HasSum (fun n => ‖v (n + 1)‖) 0 := by
  simpa [v] using (hasSum_zero (α := ℝ) (β := ℕ))

theorem refutes_published_equivalence :
    Function.Bijective (id : ℕ → ℕ) ∧ Set.Infinite (Set.univ : Set ℕ) ∧
    0 < (1 : ℝ) ∧ HasSum v 1 ∧ HasSum (fun n => ‖v n‖) 1 ∧
    HasSum (fun n => v (n + 1)) 0 ∧
    HasSum (fun n => ‖v (n + 1)‖) 0 ∧
    ¬ HasSum (fun n => ‖v (n + 1)‖) 1 ∧
    ¬ (HasSum (fun n => ‖v n‖) 1 ↔ HasSum (fun n => ‖v (n + 1)‖) 1) := by
  have hn : ¬ HasSum (fun n => ‖v (n + 1)‖) 1 := by
    intro h
    have := absolute_tail_sum.unique h
    norm_num at this
  exact ⟨Function.bijective_id, Set.infinite_univ, by norm_num,
    full_sum, absolute_full_sum, tail_sum, absolute_tail_sum, hn,
    fun h => hn (h.mp absolute_full_sum)⟩

theorem negative_control_begin_at_zero : HasSum (fun n => ‖v n‖) 1 :=
  absolute_full_sum
end ProofWiki117692CodexExpansion
