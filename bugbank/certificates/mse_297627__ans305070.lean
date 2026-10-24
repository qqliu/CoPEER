import Mathlib.Combinatorics.SimpleGraph.Clique
import Mathlib.Data.Finset.Lattice.Fold
import Mathlib.Tactic.Tauto

/-! The original six-vertex witness, original distinguished clique and original
move order 2,3 are retained. Mathlib SimpleGraph.IsClique, Finset.powerset,
Finset.sup and Finset.card replace custom graph, powerset, set and counting
routines. The source's s(S) is exactly the maximum clique cardinality below. -/
namespace MSE297627

def graph : SimpleGraph (Fin 6) where
  Adj x y := x ≠ y ∧ (x < 2 ∨ y < 2 ∨ (x=2 ∧ y=3) ∨ (x=3 ∧ y=2))
  symm := by intro x y h; tauto
  loopless := ⟨by simp⟩
instance : DecidableRel graph.Adj := fun x y => inferInstanceAs (Decidable
  (x ≠ y ∧ (x < 2 ∨ y < 2 ∨ (x=2 ∧ y=3) ∨ (x=3 ∧ y=2))))

def s (S : Finset (Fin 6)) : ℕ :=
  (S.powerset.filter (fun A : Finset (Fin 6) => graph.IsClique (A : Set (Fin 6)))).sup Finset.card

def G : Finset (Fin 6) := {0,1,2,3}
def Y : Finset (Fin 6) := {0,1,4,5}
def Z : Finset (Fin 6) := {2,3}
def H₁ : Finset (Fin 6) := {0,1,4}
def H₂ : Finset (Fin 6) := {0,1,5}

theorem original_process :
    graph.IsClique (G : Set (Fin 6)) ∧ G.card = 4 ∧ s Finset.univ = 4 ∧
    (∀ v ∈ G, s (Finset.univ.erase v) = 3) ∧
    s (Finset.univ.erase 2) = 3 ∧ s ((Finset.univ.erase 2).erase 3) = 3 ∧
    ((Finset.univ.erase 2).erase 3) = Y ∧ s ({2} : Finset (Fin 6)) = 1 ∧
    s Z = 2 := by decide

theorem certificate :
    Y ∪ Z = Finset.univ ∧ Disjoint Y Z ∧ s Y = 3 ∧ s Z = 2 ∧
    (G ∩ Y).Nonempty ∧
    (∀ v ∈ G ∩ Y, s (Y.erase v) = s Y - 1 ∧ s (insert v Z) = s Z + 1) ∧
    H₁ ⊆ Y ∧ H₂ ⊆ Y ∧ H₁ ≠ H₂ ∧
    graph.IsClique (H₁ : Set (Fin 6)) ∧ graph.IsClique (H₂ : Set (Fin 6)) ∧
    H₁.card = s Y ∧ H₂.card = s Y ∧
    5 ∈ H₂ ∧ s (Y.erase 5) = s Y ∧ s (Y.erase 5) ≠ s Y - 1 := by decide
end MSE297627
