import Mathlib.Data.Set.Lattice
import Mathlib.Tactic.NormNum
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.Ring
import Mathlib.Tactic.FinCases
import Mathlib.Tactic.Tauto

/- Human-review repair, 2026-09-15.
Full contextual families are included: F={{1,2},{1}}, G={{2}}, H={{1,2}}. Every required union lies in H and x=2 is in its intersection, but membership in the chosen A does not imply membership in every member of F.
Historical source and human verdicts are preserved in the review packet. -/
namespace RedditLearnmath12d6y5z

def A : Set ℕ := {1,2}
def B : Set ℕ := {2}
def C : Set ℕ := {1}
def F : Set (Set ℕ) := {A,C}
def G : Set (Set ℕ) := {B}
def H : Set (Set ℕ) := {A}

theorem audited_counterexample :
    (∀ S ∈ F, ∀ T ∈ G, S ∪ T ∈ H) ∧
    2 ∈ ⋂₀ H ∧ A ∈ F ∧ 2 ∈ A ∧ 2 ∉ ⋂₀ F := by
  constructor
  · intro S hS T hT
    simp only [F, Set.mem_insert_iff, Set.mem_singleton_iff] at hS
    simp only [G, Set.mem_singleton_iff] at hT
    subst T
    rcases hS with rfl | rfl <;> simp [H, A, B, C, Set.ext_iff,or_comm]
  · simp [H, F, A, B, C]
end RedditLearnmath12d6y5z
