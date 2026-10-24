import Mathlib
/-! Original three-element witness, with actual Setoid and finite cardinality.
This concerns the literal threshold inside the contrapositive proof. -/
namespace ProofWiki104646
abbrev S := Fin 3
def op (x y : S) : S := if x = 2 ∧ y = 2 then 1 else 0
def R : Setoid S where
  r x y := (x = 1 ↔ y = 1)
  iseqv := ⟨fun _ => Iff.rfl, fun h => h.symm, fun h h2 => h.trans h2⟩
instance (x y : S) : Decidable (R.r x y) := inferInstanceAs (Decidable (x = 1 ↔ y = 1))

theorem refutes_more_than_three :
    Fintype.card S = 3 ∧
    ¬ (∀ x y : S, op x y = x) ∧
    ¬ (∀ x y : S, op x y = y) ∧
    ¬ (∃ c : S, ∀ x y, op x y = c) ∧
    op 0 0 ≠ op 2 2 ∧
    ¬ (op 0 0 = 0 ∧ op 2 2 = 2) ∧
    ¬ (op 0 0 = 0 ∧ op 2 2 = 2) ∧
    R.r 0 2 ∧ R.r 0 2 ∧ ¬ R.r (op 0 0) (op 2 2) ∧
    ¬ (3 < Fintype.card S) := by
  decide
end ProofWiki104646
