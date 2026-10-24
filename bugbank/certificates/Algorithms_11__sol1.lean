import Mathlib.Combinatorics.SimpleGraph.VertexCover
import Mathlib.Tactic.NormNum
set_option autoImplicit false

/- The original K₁,₃ and K₂ witnesses, with Mathlib vertex covers,
independent sets, finite cardinality and unbounded finite-schedule reachability.
Only the source-specific ferry transition is defined here. A state stores the
pilot in bit 0 and passenger i in bit i+1. -/
namespace QEDMissingAlg11

set_option maxRecDepth 4096
set_option maxHeartbeats 1000000

def star : SimpleGraph (Fin 4) :=
  SimpleGraph.fromEdgeSet ({s(0,1), s(0,2), s(0,3)} : Set (Sym2 (Fin 4)))
instance : DecidableRel star.Adj := by unfold star; infer_instance
def cover : Finset (Fin 4) := {0}
def pilot (s : Fin 32) : Bool := s.val % 2 == 1
def passenger (s : Fin 32) (i : Fin 4) : Bool :=
  (s.val >>> (i.val + 1)) % 2 == 1
def safe (s : Fin 32) : Prop :=
  star.IsIndepSet {i | passenger s i ≠ pilot s}
instance (s : Fin 32) : Decidable (safe s) := by
  unfold safe SimpleGraph.IsIndepSet Set.Pairwise
  infer_instance
def moved (p s : Fin 32) : Finset (Fin 4) :=
  Finset.univ.filter (fun i => passenger p i ≠ passenger s i)
def step (p s : Fin 32) : Prop :=
  pilot s = !pilot p ∧ (moved p s).card ≤ 1 ∧
  (∀ i ∈ moved p s, passenger p i = pilot p) ∧ safe s
instance (p s : Fin 32) : Decidable (step p s) := by unfold step; infer_instance
def invariant : Finset (Fin 32) := {0,2,3,4,7,8,11,16,19}
theorem invariant_closed : ∀ p s : Fin 32,
    p ∈ invariant → step p s → s ∈ invariant := by decide
theorem no_schedule : ¬ Relation.ReflTransGen step (0 : Fin 32) 31 := by
  intro h
  have trapped : ∀ s, Relation.ReflTransGen step (0 : Fin 32) s → s ∈ invariant := by
    intro s hs
    induction hs with
    | refl => decide
    | @tail b c hab hbc ih => exact invariant_closed b c ih hbc
  have ht := trapped 31 h
  exact (show (31 : Fin 32) ∉ invariant by decide) ht
theorem sol1_refutation :
    star.IsVertexCover (cover : Set (Fin 4)) ∧ cover.card = 1 ∧
    safe 0 ∧ safe 31 ∧ ¬ Relation.ReflTransGen step (0 : Fin 32) 31 := by
  refine ⟨?_, by decide, by decide, by decide, no_schedule⟩
  unfold SimpleGraph.IsVertexCover star cover
  decide

def edgeGraph : SimpleGraph (Fin 2) := ⊤
instance : DecidableRel edgeGraph.Adj := by unfold edgeGraph; infer_instance
def coverH : Finset (Fin 2) := {1}
def pilotH (s : Fin 8) : Bool := s.val % 2 == 1
def passengerH (s : Fin 8) (i : Fin 2) : Bool :=
  (s.val >>> (i.val + 1)) % 2 == 1
def stepH (p s : Fin 8) : Prop :=
  pilotH s = !pilotH p ∧
  (Finset.univ.filter (fun i => passengerH p i ≠ passengerH s i)).card ≤ 1 ∧
  (∀ i : Fin 2, passengerH p i ≠ passengerH s i → passengerH p i = pilotH p) ∧
  edgeGraph.IsIndepSet {i | passengerH s i ≠ pilotH s}
theorem sol2_refutation :
    edgeGraph.IsVertexCover (coverH : Set (Fin 2)) ∧ coverH.card = 1 ∧
    ¬ stepH 0 7 := by
  unfold SimpleGraph.IsVertexCover edgeGraph coverH stepH SimpleGraph.IsIndepSet Set.Pairwise
  decide
end QEDMissingAlg11
#print axioms QEDMissingAlg11.sol1_refutation
#print axioms QEDMissingAlg11.sol2_refutation
