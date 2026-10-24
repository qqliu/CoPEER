import Mathlib
namespace QEDReview28sol5
abbrev graph : SimpleGraph (Fin 4) := ⊤
def coloring : graph.Coloring (Fin 12) :=
  SimpleGraph.Coloring.mk (fun v => ⟨v.val, by omega⟩) (by
    intro u v h heq
    exact h (Fin.ext (congrArg (fun i : Fin 12 => i.val) heq)))
lemma not_three_colorable : ¬ graph.Colorable 3 := by
  rintro ⟨C⟩
  have hi : Function.Injective C := by
    intro u v h
    by_contra hn
    exact C.valid hn h
  have := Fintype.card_le_of_injective C hi
  norm_num at this
/-- The identity reduction sends the original K₄ to a 12-colorable graph that is not 3-colorable. -/
theorem refuted : graph.Colorable 12 ∧ ¬ graph.Colorable 3 :=
  ⟨⟨coloring⟩, not_three_colorable⟩
end QEDReview28sol5
