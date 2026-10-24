import Mathlib
/-! Preserve S={a,b}, C={{b}}, X={a}, y=a. Source-specific theta and t
are implemented from their printed definitions on Mathlib finite sets/lists.
The source assumptions are circuit axioms, so they are checked explicitly. -/
namespace ProofWiki113792
abbrev S := Fin 2
def circuits : Finset (Finset S) := {{1}}
def theta (x : S) (seen : Finset S) : ℤ :=
  if ∃ C ∈ circuits, x ∈ C ∧ C ⊆ seen then 0 else 1
def t (xs : List S) : ℤ :=
  ((List.range xs.length).map (fun i => theta xs[i]! (xs.take (i+1)).toFinset)).sum

theorem circuit_axioms :
    circuits.Nonempty ∧ (∅ : Finset S) ∉ circuits ∧
    (∀ C₁ ∈ circuits, ∀ C₂ ∈ circuits, C₁ ≠ C₂ → ¬ C₁ ⊆ C₂) ∧
    (∀ C₁ ∈ circuits, ∀ C₂ ∈ circuits, ∀ z w : S,
      C₁ ≠ C₂ → z ∈ C₁ ∩ C₂ → w ∈ C₁ \ C₂ →
      ∃ C₃ ∈ circuits, w ∈ C₃ ∧ C₃ ⊆ (C₁ ∪ C₂).erase z) := by
  simp [circuits]

theorem refutes_literal_equality_chain_with_y_in_X :
    ({0} : Finset S) ∪ {0} = {0} ∧
    t [0] = 1 ∧ t [0,0] = 2 ∧ theta 0 {0} = 1 ∧
    t [0] - t [0] ≠ t [0,0] - t [0] := by
  decide

/-- Any set function rho takes the same value before/after adjoining y∈X.
This avoids assuming an arbitrary finite rank surrogate equals the source's
rho. Its distinct listing [a] has t=1, as computed above. -/
theorem refutation_for_any_set_rank (rho : Finset S → ℤ) :
    rho ({0} ∪ {0}) - rho {0} ≠ t [0,0] - t [0] := by
  have h1 : t [0] = 1 := by decide
  have h2 : t [0,0] = 2 := by decide
  rw [Finset.union_self, sub_self, h1, h2]
  norm_num
end ProofWiki113792
