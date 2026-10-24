import Mathlib

namespace QEDReview10sol5
/-- The frozen witness K₂ on {0,5} and K₄ on {1,2,3,4}. -/
def graph : SimpleGraph (Fin 6) where
  Adj u v := u ≠ v ∧ ((u = 0 ∨ u = 5) ↔ (v = 0 ∨ v = 5))
  symm := by intro u v h; exact ⟨h.1.symm, h.2.symm⟩
  loopless := ⟨fun u h => h.1 rfl⟩
instance : DecidableRel graph.Adj := fun _ _ => inferInstanceAs (Decidable (_ ∧ _))
def neighborhood (S : Finset (Fin 6)) := S.biUnion (fun v => graph.neighborFinset v)
lemma expansion : ∀ S : Finset (Fin 6), S.card = 3 → 4 ≤ (neighborhood S).card := by decide
/-- The singleton does not inherit the expansion assumption for half-sized sets. -/
theorem refuted :
    (0 : ℝ) < 1 / 6 ∧
    (∀ S : Finset (Fin 6), S.card = 3 →
      (3 : ℝ) + (1 / 6) * 6 ≤ (neighborhood S).card) ∧
    (neighborhood {0}).card = 1 ∧
    ¬ ((3 : ℝ) + (1 / 6) * 6 ≤ (neighborhood {0}).card) := by
  refine ⟨by norm_num, ?_, by decide, ?_⟩
  · intro S hS
    have := expansion S hS
    norm_num
    exact_mod_cast this
  · have h : (neighborhood {0}).card = 1 := by decide
    rw [h]
    norm_num
end QEDReview10sol5
