import Mathlib.MeasureTheory.MeasurableSpace.Defs

/-!
Source: https://math.stackexchange.com/a/1646288 (line 0052).
The source claims that a generating family must contain the whole space.
The generator {{true}} on Bool omits the whole space; its generated measurable
space contains it, by the sigma-algebra axioms. The witness uses Mathlib's actual
MeasurableSpace.generateFrom, replacing a bounded Boolean closure simulation.
-/
namespace mse_1645967__ans1646288

def generator : Set (Set Bool) := {{true}}
abbrev generated : MeasurableSpace Bool := MeasurableSpace.generateFrom generator

theorem generator_need_not_contain_Omega :
    MeasurableSpace.generateFrom generator = generated ∧
    @MeasurableSet Bool generated Set.univ ∧
    Set.univ ∉ generator := by
  refine ⟨rfl, MeasurableSet.univ, ?_⟩
  intro h
  have hEq : (Set.univ : Set Bool) = {true} := h
  have hf : false ∈ ({true} : Set Bool) := hEq ▸ Set.mem_univ false
  cases hf

theorem generator_really_generates_singleton :
    @MeasurableSet Bool generated {true} :=
  MeasurableSpace.measurableSet_generateFrom (by exact Set.mem_singleton _)

end mse_1645967__ans1646288

namespace mse_1645967__ans1646288
/-- This is the originally stored full-powerset witness on the two-point space. -/
theorem generated_is_full_powerset : generated = ⊤ := by
  letI : MeasurableSpace Bool := generated
  apply le_antisymm le_top
  intro s _
  have ht := generator_really_generates_singleton
  have hf : @MeasurableSet Bool generated {false} := by
    have heq : ({true} : Set Bool)ᶜ = {false} := by
      ext b
      cases b <;> simp
    rw [← heq]
    exact ht.compl
  by_cases hT : true ∈ s <;> by_cases hF : false ∈ s
  · have heq : s = Set.univ := by ext b; cases b <;> simp_all
    rw [heq]
    exact MeasurableSet.univ
  · have heq : s = {true} := by ext b; cases b <;> simp_all
    rw [heq]
    exact ht
  · have heq : s = {false} := by ext b; cases b <;> simp_all
    rw [heq]
    exact hf
  · have heq : s = ∅ := by ext b; cases b <;> simp_all
    rw [heq]
    exact MeasurableSet.empty

/-- Final certificate for the exact stored witness G={{true}}, A=the powerset. -/
theorem original_generator_counterexample :
    MeasurableSpace.generateFrom generator = (⊤ : MeasurableSpace Bool) ∧
    Set.univ ∉ generator :=
  ⟨generated_is_full_powerset, generator_need_not_contain_Omega.2.2⟩
end mse_1645967__ans1646288
