import Mathlib.Tactic
namespace Arxiv240216847v2SourceEnrichedCodex
abbrev Load := ℕ × ℕ
def step (S : Finset Load) (p d : ℕ) : Finset Load :=
  S ∪ (S.filter (fun x => x.1 ≤ d-p ∧ x.2 ≤ d-p)).biUnion
    (fun x => {x,(x.1+p,x.2),(x.1,x.2+p)})
def S₀ : Finset Load := {(0,0)}
def S₁ := step S₀ 5 5
def S₂ := step S₁ 1 5
def processing : Fin 2 → ℕ := ![5,1]
def deadline : Fin 2 → ℕ := ![5,5]
def assignment : Fin 2 → Fin 2 := id
def completion (j : Fin 2) : ℕ :=
  ∑ i ∈ (Finset.univ : Finset (Fin 2)).filter (fun i => i ≤ j ∧ assignment i = assignment j), processing i
def load (m : Fin 2) : ℕ :=
  ∑ i ∈ (Finset.univ : Finset (Fin 2)).filter (fun i => assignment i = m), processing i
theorem refutes_refined_multi_machine_feasibility_recurrence :
    (∀ j : Fin 2, 0 < processing j ∧ completion j ≤ deadline j) ∧
    Monotone deadline ∧
    (load 0,load 1) = (5,1) ∧
    S₁ = {(0,0),(5,0),(0,5)} ∧
    S₂ = {(0,0),(5,0),(0,5),(1,0),(0,1)} ∧
    (load 0,load 1) ∉ S₂ := by
  decide
end Arxiv240216847v2SourceEnrichedCodex
