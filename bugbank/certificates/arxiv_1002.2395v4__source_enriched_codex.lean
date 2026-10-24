import Mathlib.Tactic

/-! The source permits real-valued F, not only nonnegative F, and defines
normalized cardinality-layer averages. The values (1,1,-1,-1) satisfy all
Hadamard-Fischer inequalities but give averages (1,0,-1). -/
namespace Arxiv10022395v4SourceEnrichedCodex
open Finset
noncomputable def F (s : Finset (Fin 2)) : ℝ := if 1 ∈ s then -1 else 1
noncomputable def layerAverage (k : ℕ) : ℝ :=
  (∑ s ∈ (Finset.univ : Finset (Finset (Fin 2))).filter (fun s => s.card = k), F s) /
    Nat.choose 2 k

theorem hadamard_fischer (s t : Finset (Fin 2)) :
    F (s ∩ t) * F (s ∪ t) ≤ F s * F t := by
  by_cases hs : 1 ∈ s <;> by_cases ht : 1 ∈ t <;> simp [F,hs,ht]

theorem refutes_hadamard_fischer_absolute_newton :
    F ∅ = 1 ∧
    (∀ s t, F (s ∩ t) * F (s ∪ t) ≤ F s * F t) ∧
    layerAverage 0 = 1 ∧ layerAverage 1 = 0 ∧ layerAverage 2 = -1 ∧
    ¬ layerAverage 1 ^ 2 ≥ |layerAverage 0 * layerAverage 2| := by
  have hs0 : (Finset.univ : Finset (Finset (Fin 2))).filter (fun s => s.card = 0) = {∅} := by decide
  have hs1 : (Finset.univ : Finset (Finset (Fin 2))).filter (fun s => s.card = 1) = {{0},{1}} := by decide
  have hs2 : (Finset.univ : Finset (Finset (Fin 2))).filter (fun s => s.card = 2) = {{0,1}} := by decide
  have h0 : layerAverage 0 = 1 := by unfold layerAverage; rw [hs0]; norm_num [F]
  have h1 : layerAverage 1 = 0 := by unfold layerAverage; rw [hs1]; norm_num [F]
  have h2 : layerAverage 2 = -1 := by unfold layerAverage; rw [hs2]; norm_num [F]
  refine ⟨by simp [F],hadamard_fischer,h0,h1,h2,?_⟩
  rw [h0,h1,h2]
  norm_num
end Arxiv10022395v4SourceEnrichedCodex
