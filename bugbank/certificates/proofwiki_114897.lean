import Mathlib
/-! Actual order filters on Mathlib Boolean algebras, including the original
atom-generated maximal proper filter on Bool x Bool. -/
namespace ProofWiki114897
open Order

def F : PFilter Bool := PFilter.principal true
def U : PFilter (Bool × Bool) := PFilter.principal (true, false)

theorem bottom_not_mem : (⊥ : Bool) ∉ F := by simp [F]

theorem U_maximal_proper :
    (⊥ : Bool × Bool) ∉ U ∧
    ∀ G : PFilter (Bool × Bool), (⊥ : Bool × Bool) ∉ G → U ≤ G → G ≤ U := by
  refine ⟨by change ¬ ((true, false) ≤ (false, false)); decide, ?_⟩
  intro G hproper hUG x hx
  have ha : (true, false) ∈ G := hUG (by simp [U])
  have hmeet := PFilter.inf_mem hx ha
  rcases x with ⟨b,c⟩
  cases b <;> cases c
  · exact False.elim (hproper hmeet)
  · exact False.elim (hproper hmeet)
  · simp [U]
  · simp [U]

theorem refutes_published_filter_claims :
    (⊥ : Bool) ∉ F ∧
    ¬ (∀ G : PFilter Bool, (⊥ : Bool) ∈ G) ∧
    (true, false) ∈ U ∧ (⊥ : Bool × Bool) ∉ U ∧
    (∀ G : PFilter (Bool × Bool), (⊥ : Bool × Bool) ∉ G → U ≤ G → G ≤ U) := by
  exact ⟨bottom_not_mem, fun h => bottom_not_mem (h F), by simp [U],
    U_maximal_proper.1, U_maximal_proper.2⟩

theorem negative_control_top_is_in_every_filter (G : PFilter Bool) : (⊤ : Bool) ∈ G :=
  PFilter.top_mem
end ProofWiki114897
