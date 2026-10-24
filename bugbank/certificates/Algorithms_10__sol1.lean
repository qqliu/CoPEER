import Mathlib

/-!
# Algorithms 10, solution 1: expansion does not force positive minimum degree

The witness is `K₅` together with an isolated vertex, on `Fin 6`, with `α=1/3`.
The expansion premise quantifies over every `Finset (Fin 6)` of cardinality three.
Adjacency, degree and minimum degree use Mathlib's `SimpleGraph` definitions;
the open neighborhood is the union of its neighbor finsets.
-/
namespace ProofCerts.Alg10

def graph : SimpleGraph (Fin 6) where
  Adj x y := x ≠ y ∧ x ≠ 0 ∧ y ≠ 0
  symm := by intro x y h; exact ⟨h.1.symm, h.2.2, h.2.1⟩
  loopless := ⟨fun x h => h.1 rfl⟩

instance : DecidableRel graph.Adj := fun _ _ => inferInstanceAs (Decidable (_ ∧ _ ∧ _))

def neighborhood (S : Finset (Fin 6)) : Finset (Fin 6) :=
  S.biUnion (fun v => graph.neighborFinset v)

/-- Every size-three subset satisfies the source's open-neighborhood premise. -/
theorem expansion_premise :
    ∀ S : Finset (Fin 6), S.card = 3 → (neighborhood S).card = 5 := by
  decide

theorem degree_zero : graph.degree 0 = 0 := by decide

theorem min_degree_zero : graph.minDegree = 0 := by
  have h := graph.minDegree_le_degree 0
  rw [degree_zero] at h
  omega

noncomputable def alpha : ℝ := 1 / 3

theorem alpha_positive : 0 < alpha := by norm_num [alpha]

/-- The full expansion hypothesis holds, yet its alleged minimum-degree consequence fails. -/
theorem expansion_not_imply_min_degree :
    0 < alpha ∧
    (∀ S : Finset (Fin 6), S.card = 3 →
      (3 : ℝ) + alpha * 6 ≤ (neighborhood S).card) ∧
    ¬ ((graph.minDegree : ℝ) > alpha * 6) := by
  refine ⟨alpha_positive, ?_, ?_⟩
  · intro S hS
    rw [expansion_premise S hS]
    norm_num [alpha]
  · rw [min_degree_zero]
    norm_num [alpha]

end ProofCerts.Alg10
