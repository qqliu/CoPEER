import Mathlib
namespace QEDReview11sol5
abbrev graph : SimpleGraph (Fin 3) := ⊤
/-- A trip respects the source's passenger capacity, departs from its stated bank,
and leaves an independent unattended bank. Charon travels with the load. -/
def Trip (departure load unattended : Finset (Fin 3)) : Prop :=
  load ⊆ departure ∧ load.card ≤ 2 ∧
  unattended = departure \ load ∧ graph.IsIndepSet (↑unattended)
lemma not_two_colorable : ¬ graph.Colorable 2 := by
  rintro ⟨C⟩
  have hi : Function.Injective C := by
    intro u v h
    by_contra hn
    exact C.valid hn h
  have := Fintype.card_le_of_injective C hi
  norm_num at this
/-- Original three trips on K₃, with two passenger seats and one pilot seat. -/
theorem refuted :
    Trip {0,1,2} {1,2} {0} ∧
    Trip {1,2} {2} {1} ∧
    Trip {0,2} {0,2} ∅ ∧
    ({1} ∪ ({0,2} : Finset (Fin 3))) = Finset.univ ∧
    ¬ graph.Colorable 2 := by
  refine ⟨?_, ?_, ?_, by decide, not_two_colorable⟩ <;> (unfold Trip; decide)
end QEDReview11sol5
