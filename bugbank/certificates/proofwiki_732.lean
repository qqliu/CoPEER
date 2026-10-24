import Mathlib
/-! Keep original witness3: S={0,1,2},T={0,1}, rows {0},{1},{0,1}.
Mathlib relation images certify surjectivity on the entire powerset, while
row2 violates single-valuedness. Thus this witness meets the source's full
surjective-direct-image hypothesis, unlike its smaller witness1. -/
namespace ProofWiki732
abbrev S := Fin 3
abbrev T := Fin 2
def R : SetRel S T := {p | (p.1 = 0 ∧ p.2 = 0) ∨ (p.1 = 1 ∧ p.2 = 1) ∨ p.1 = 2}

instance (p : S × T) : Decidable (p ∈ R) := inferInstanceAs (Decidable ((_ ∧ _) ∨ (_ ∧ _) ∨ _))

theorem image_surjective : Function.Surjective (SetRel.image R) := by
  intro t
  refine ⟨{x | (x = 0 ∧ (0 : T) ∈ t) ∨ (x = 1 ∧ (1 : T) ∈ t)}, ?_⟩
  ext y
  fin_cases y <;> simp [SetRel.image, R, Fin.exists_fin_succ]

theorem refutes_singleton_exclusion_under_full_context :
    Function.Surjective (SetRel.image R) ∧
    (2,0) ∈ R ∧ (2,1) ∈ R ∧ (0 : T) ≠ 1 ∧
    ({0} : Set T) ∈ Set.range (SetRel.image R) ∧
    ({1} : Set T) ∈ Set.range (SetRel.image R) ∧
    ¬ (∀ x : S, ∀ y z : T, (x,y) ∈ R → (x,z) ∈ R → y=z) := by
  refine ⟨image_surjective, by decide, by decide, by decide,
    image_surjective {0}, image_surjective {1}, ?_⟩
  intro h
  exact (by decide : (0 : T) ≠ 1) (h 2 0 1 (by decide) (by decide))
end ProofWiki732
