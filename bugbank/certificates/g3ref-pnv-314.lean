import Mathlib
open Set MeasureTheory
/-! Original witness preserved; standard Mathlib mathematical objects. Local proof-step counterexample. -/
namespace G3refPnv314
abbrev X := Bool × Bool
local instance : TopologicalSpace Bool := ⊥
local instance : DiscreteTopology Bool := ⟨rfl⟩
def U : Set X := {(false,false), (true,true)}
def V : Set X := {(true,false)}
theorem refutes_disjoint_projections :
    T2Space X ∧ IsOpen U ∧ IsOpen V ∧ Disjoint U V ∧
    (false,false) ∈ U ∧ (true,false) ∈ V ∧
    ¬ Disjoint (Prod.fst '' U) (Prod.fst '' V) := by
  refine ⟨inferInstance, isOpen_discrete _, isOpen_discrete _, ?_, by simp [U], by simp [V], ?_⟩
  · simp [U,V, Set.disjoint_left]
  · intro h
    have hu : true ∈ Prod.fst '' U := ⟨(true,true), by simp [U], rfl⟩
    have hv : true ∈ Prod.fst '' V := ⟨(true,false), by simp [V], rfl⟩
    exact (Set.disjoint_left.mp h) hu hv

end G3refPnv314
