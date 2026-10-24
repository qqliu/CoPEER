import Mathlib

/-!
# Algorithms 17: a cyclic unique minimum and failure of cycle-edge deletion

This certificate is shared by records `Algorithms_17__sol1` through
`Algorithms_17__sol5`. The selected theorem for solutions 1–4 is
`unique_transRed_not_acyclic`: the directed two-cycle has a unique
minimum-edge transitive reduction and is cyclic. For solution 4, substituting
two vertices in the source's two cyclic orders gives the same two cross
edges, not two distinct reductions. The selected theorem for solution 5 is
`cycle_edge_deletion_loses_reachability`: deleting edge `0 → 1` leaves one
edge but loses reachability from `0` to `1`.

`Relation.TransGen` expresses positive-length reachability. A transitive
reduction minimizes edge count over all digraphs on these two vertices with
the same reachability relation; self-loops are allowed among competitors.
The certificate concerns this two-vertex example, not a larger enumeration
or a graph-count claim. Source correspondence is assessed separately from
kernel verification of these declarations.
-/
namespace ProofCerts.Alg17

abbrev Digraph := Fin 2 → Fin 2 → Bool

def Adj (a b : Fin 2) : Bool := decide (a ≠ b)

abbrev Reach (H : Digraph) := Relation.TransGen (fun a b => H a b = true)

def SameReach (G H : Digraph) : Prop := ∀ a b, Reach G a b ↔ Reach H a b

def edgeSet (H : Digraph) : Finset (Fin 2 × Fin 2) :=
  Finset.univ.filter (fun p => H p.1 p.2 = true)

def edgeCount (H : Digraph) : ℕ := (edgeSet H).card

def IsTransRed (G H : Digraph) : Prop :=
  SameReach G H ∧ ∀ K, SameReach G K → edgeCount H ≤ edgeCount K

def Acyclic (H : Digraph) : Prop := ∀ a, ¬ Reach H a a

lemma cross_edge_of_path (H : Digraph) {a b : Fin 2} (h : Reach H a b) :
    a ≠ b → H a b = true := by
  induction h using Relation.TransGen.trans_induction_on with
  | single h => exact fun _ => h
  | @trans a b c hab hbc ihab ihbc =>
    intro hac
    by_cases heq : a = b
    · subst b; exact ihbc hac
    · by_cases heq' : b = c
      · subst c; exact ihab hac
      · have hsame : a = c := by
          fin_cases a <;> fin_cases b <;> fin_cases c <;> simp_all
        exact (hac hsame).elim

lemma witness_reaches (a b : Fin 2) : Reach Adj a b := by
  fin_cases a <;> fin_cases b
  · exact (show Reach Adj 0 1 from .single (by decide)).trans
      (.single (show Adj 1 0 = true by decide))
  · exact .single (by decide)
  · exact .single (by decide)
  · exact (show Reach Adj 1 0 from .single (by decide)).trans
      (.single (show Adj 0 1 = true by decide))

lemma witness_edges_required (H : Digraph) (h : SameReach Adj H) :
    edgeSet Adj ⊆ edgeSet H := by
  intro p hp
  have hp' : Adj p.1 p.2 = true := (Finset.mem_filter.mp hp).2
  have hne : p.1 ≠ p.2 := of_decide_eq_true hp'
  exact Finset.mem_filter.mpr ⟨Finset.mem_univ _,
    cross_edge_of_path H ((h _ _).mp (witness_reaches _ _)) hne⟩

theorem G_is_transRed : IsTransRed Adj Adj := by
  refine ⟨fun _ _ => Iff.rfl, fun H hH => ?_⟩
  exact Finset.card_le_card (witness_edges_required H hH)

theorem transRed_unique (H : Digraph) (hH : IsTransRed Adj H) : H = Adj := by
  have hsub := witness_edges_required H hH.1
  have hcard : (edgeSet H).card ≤ (edgeSet Adj).card :=
    hH.2 Adj (fun _ _ => Iff.rfl)
  have hsets : edgeSet Adj = edgeSet H := Finset.eq_of_subset_of_card_le hsub hcard
  funext a b
  have heq : (H a b = true) ↔ Adj a b = true := by
    have := congrArg (fun S : Finset (Fin 2 × Fin 2) => (a, b) ∈ S) hsets
    simpa [edgeSet] using (Iff.of_eq this).symm
  exact Bool.eq_iff_iff.mpr heq

theorem G_not_acyclic : ¬ Acyclic Adj := fun h => h 0 (witness_reaches 0 0)

/-- A cyclic digraph has a unique minimum-edge transitive reduction. -/
theorem unique_transRed_not_acyclic :
    (∃! H : Digraph, IsTransRed Adj H) ∧ ¬ Acyclic Adj :=
  ⟨⟨Adj, G_is_transRed, transRed_unique⟩, G_not_acyclic⟩

/-- The solution-5 witness deletes edge `0 → 1` and leaves only `1 → 0`. -/
def deletedCycleEdge : Digraph := fun a b => decide (a = 1 ∧ b = 0)
theorem cycle_edge_deletion_loses_reachability :
    edgeCount Adj = 2 ∧ edgeCount deletedCycleEdge = 1 ∧
    ¬ SameReach Adj deletedCycleEdge := by
  refine ⟨by decide, by decide, ?_⟩
  intro h
  have hpath := (h 0 1).mp (witness_reaches 0 1)
  have hedge := cross_edge_of_path deletedCycleEdge hpath (by decide)
  norm_num [deletedCycleEdge] at hedge

end ProofCerts.Alg17
