import Mathlib.GroupTheory.Perm.Centralizer
import Mathlib.GroupTheory.Subgroup.Center
import Mathlib.Combinatorics.SimpleGraph.Clique
/-!
Original witness retained: S₃, m = 1. The source's displayed subtraction gives
three maximal independent singleton sets versus zero subgroups of order zero.
This targets only the local sign error, not a different group-theoretic theorem.
All group operations are Mathlib permutations; the center, graph independence,
inclusion maximality, subgroups, commutativity, and cardinalities use Mathlib.
The finite decision procedure is proved equivalent to the library predicate.
-/
namespace Arxiv170607142v2SourceEnrichedCodex
abbrev G := Equiv.Perm (Fin 3)
abbrev V := {g : G // g ∉ Subgroup.center G}
def graph : SimpleGraph V where
 Adj x y := x.1 * y.1 ≠ y.1 * x.1
 symm := by intro x y h; exact Ne.symm h
 loopless := ⟨by intro x; simp⟩
instance : DecidableRel graph.Adj := fun _ _ => inferInstanceAs (Decidable (_ ≠ _))
/-- Convert the library's inclusion-maximal set predicate to finite quantification,
solely to supply a computable decision procedure. -/
lemma maximal_iff_finite (s : Finset V) :
    Maximal graph.IsIndepSet (s : Set V) ↔
      graph.IsIndepSet s ∧
        ∀ t : Finset V, graph.IsIndepSet t → s ⊆ t → t ⊆ s := by
  classical
  rw [SimpleGraph.isMaximalIndepSet_iff]
  constructor
  · rintro ⟨hs,hm⟩
    exact ⟨hs,fun t ht hst => by simpa using hm (t : Set V) ht (by simpa using hst)⟩
  · rintro ⟨hs,hm⟩
    refine ⟨hs,?_⟩
    intro t ht hst
    have h := hm t.toFinset (by simpa using ht) (by simpa using hst)
    simpa using h

instance (s : Finset V) : Decidable (Maximal graph.IsIndepSet (s : Set V)) :=
  decidable_of_iff _ (maximal_iff_finite s).symm

/-- Number of inclusion-maximal independent sets of the requested cardinality. -/
def mis (n : ℕ) : ℕ :=
  (Finset.univ.filter fun s : Finset V =>
    Maximal graph.IsIndepSet (s : Set V) ∧ s.card = n).card

/-- Number of inclusion-maximal abelian Mathlib subgroups of the requested order. -/
noncomputable def mas (n : ℕ) : ℕ :=
  Set.ncard {H : Subgroup G |
    Maximal (fun K : Subgroup G => IsMulCommutative K) H ∧ Nat.card H = n}

lemma mas_zero : mas 0 = 0 := by
  classical
  have h : {H : Subgroup G |
      Maximal (fun K : Subgroup G => IsMulCommutative K) H ∧ Nat.card H = 0} = ∅ := by
    ext H
    simp only [Set.mem_setOf_eq,Set.mem_empty_iff_false,iff_false,not_and]
    intro _
    exact Nat.card_pos.ne'
  rw [mas,h,Set.ncard_empty]

set_option maxRecDepth 100000 in
set_option maxHeartbeats 0 in
theorem refutes_published_mis_mas_negative_shift :
 Fintype.card G = 6 ∧
 (∃ x y : G, x*y≠y*x) ∧
 Fintype.card (Subgroup.center G) = 1 ∧
 Fintype.card (Subgroup.center G) ≤ 1 ∧
 mis 1 = 3 ∧ mis 2 = 1 ∧ mas (1-Fintype.card (Subgroup.center G)) = 0 ∧
 mis 1 ≠ mas (1-Fintype.card (Subgroup.center G)) := by
 have hcenter : Fintype.card (Subgroup.center G) = 1 := by decide
 have hmis : mis 1 = 3 := by decide
 refine ⟨by decide,by decide,hcenter,hcenter.le,hmis,by decide,?_,?_⟩
 · rw [hcenter]; exact mas_zero
 · rw [hcenter,Nat.sub_self,mas_zero,hmis]; decide
end Arxiv170607142v2SourceEnrichedCodex
