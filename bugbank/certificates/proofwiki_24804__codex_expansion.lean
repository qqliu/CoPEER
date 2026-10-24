import Mathlib
/-! The original three-point relation; the source explicitly uses R^0=R.
Mathlib's relation composition supplies the exact existential middle point. -/
namespace ProofWiki24804CodexExpansion
abbrev S := Fin 3
def R (x y : S) : Prop := (x = 0 ∧ y = 1) ∨ (x = 1 ∧ y = 2)
instance (x y : S) : Decidable (R x y) := inferInstanceAs (Decidable ((_ ∧ _) ∨ (_ ∧ _)))
def sourcePower : ℕ → S → S → Prop
  | 0 => R
  | n+1 => Relation.Comp (sourcePower n) R

theorem refutes_zero_power_addition :
    sourcePower 0 0 1 ∧ sourcePower 0 1 2 ∧
    Relation.Comp (sourcePower 0) (sourcePower 0) 0 2 ∧ ¬ sourcePower (0+0) 0 2 := by
  simp [sourcePower, R, Relation.Comp, Fin.exists_fin_succ]
end ProofWiki24804CodexExpansion
