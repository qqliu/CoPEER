import Mathlib.Combinatorics.SimpleGraph.Clique
import Mathlib.Data.Matrix.Mul
import Mathlib.Tactic

/-! Standard Mathlib SimpleGraph, independence and Matrix powers replace the
previous hand-written nine-entry multiplication table. The ordered path 0-1-2
has maximum independent-set size two, but its upper adjacency square is nonzero. -/
namespace Arxiv07092689v3SourceEnrichedCodex

def G : SimpleGraph (Fin 3) where
  Adj i j := (i=0 ∧ j=1) ∨ (i=1 ∧ j=0) ∨ (i=1 ∧ j=2) ∨ (i=2 ∧ j=1)
  symm := by intro i j h; aesop
  loopless := ⟨by intro i h; rcases h with h|h|h|h <;> omega⟩
instance : DecidableRel G.Adj := by intro i j; unfold G; infer_instance

def upper : Matrix (Fin 3) (Fin 3) ℕ :=
  fun i j => if i < j ∧ G.Adj i j then 1 else 0

theorem independent_two : G.IsIndepSet (({0,2} : Finset (Fin 3)) : Set (Fin 3)) := by
  decide

theorem independent_at_most_two :
    ∀ s : Finset (Fin 3), G.IsIndepSet (s : Set (Fin 3)) → s.card ≤ 2 := by
  decide

theorem upper_square_entry : (upper ^ 2) 0 2 = 1 := by
  norm_num [pow_two,Matrix.mul_apply,Fin.sum_univ_succ,upper,G] <;> decide

theorem refutes_claim1_forward_implication_on_ordered_path :
    G.IsIndepSet (({0,2} : Finset (Fin 3)) : Set (Fin 3)) ∧
    ({0,2} : Finset (Fin 3)).card = 2 ∧
    (∀ s : Finset (Fin 3), G.IsIndepSet (s : Set (Fin 3)) → s.card ≤ 2) ∧
    upper ^ (3-2+1) ≠ 0 := by
  refine ⟨independent_two,by decide,independent_at_most_two,?_⟩
  intro h
  have he := congrArg (fun M : Matrix (Fin 3) (Fin 3) ℕ => M 0 2) h
  norm_num [upper_square_entry] at he
end Arxiv07092689v3SourceEnrichedCodex
