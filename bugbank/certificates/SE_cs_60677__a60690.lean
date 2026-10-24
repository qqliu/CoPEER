/- Human-review certificate. Original witness preserved; historical certificate remains in the frozen packet. -/
import Mathlib
namespace SE_cs_60677_a60690
def W : List ℕ :=
 [1,17,23,29,31,37,41,43,47,53,59,61,67,71,73,79,81,83,88,89,91,95,97]
def Sclaim : List ℕ :=
 [1,17,29,31,37,41,43,47,53,59,61,67,71,73,79,83,89,91,92,95,97,99]
def Feasible (s : List ℕ) : Prop := s.Nodup ∧ (∀ x ∈ s, 0 < x ∧ x ≤ 100) ∧ s.Pairwise Nat.Coprime
theorem asserted_optimum_is_not_optimal :
 Feasible W ∧ Feasible Sclaim ∧ W.sum = 1356 ∧ Sclaim.sum = 1355 ∧ Sclaim.sum < W.sum := by
 unfold Feasible
 decide
end SE_cs_60677_a60690
