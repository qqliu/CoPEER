import Mathlib

/-!
Record SE_math_1291495__q (E07).

Source sentence under test (math.stackexchange question 1291495, line 12 of the quoted context):
  "G' is a tree with k-1 edges and k+1 vertices. G has k-1+m edges."
where G is a connected graph on k+1 vertices that contains a cycle, G' is what is left after
deleting m cycle edges, and G' is (correctly) asserted to be a tree.
The sentence is stated as `SourceSentence k` (through the template `SentenceWith k c`, with
`c` the printed edge count of G').  The theorem the source sets out to prove is `SourceTheorem`
(statement only): a connected graph on k+1 vertices with k edges is a tree.
The objects are Mathlib's `SimpleGraph`, `IsTree`, `Connected`, `IsAcyclic`, `edgeFinset`.
-/
set_option maxRecDepth 10000
set_option maxHeartbeats 4000000

namespace Census_SE_math_1291495__q

/-- A simple graph on `Fin n` from a list of edges. -/
def graph (n : ℕ) (es : List (ℕ × ℕ)) : SimpleGraph (Fin n) where
 Adj i j := i ≠ j ∧ ((i.val,j.val) ∈ es ∨ (j.val,i.val) ∈ es)
 symm := fun i j h => ⟨h.1.symm, h.2.symm⟩
 loopless := ⟨fun _ h => h.1 rfl⟩
instance (n : ℕ) (es : List (ℕ × ℕ)) : DecidableRel (graph n es).Adj := fun _ _ => inferInstanceAs (Decidable (_ ∧ _))

open SimpleGraph

/-- `m`, "the number of edges removed": the edges of `G` that are not edges of `G'`. -/
def removed {V : Type} [Fintype V] [DecidableEq V] (G G' : SimpleGraph V)
    [DecidableRel G.Adj] [DecidableRel G'.Adj] : ℕ :=
  (G.edgeFinset \ G'.edgeFinset).card

/-- The source sentence with the edge count of `G'` left as a parameter `c` (an integer, so that
`k - 1` is honest subtraction). The hypotheses are the source's: `G` is connected on `k+1` vertices
and contains a cycle; `G'` is a spanning tree of `G` (the outcome of the cycle-edge removal). -/
def SentenceWith (k : ℕ) (c : ℤ) : Prop :=
  ∀ (V : Type) [Fintype V] [DecidableEq V] (G G' : SimpleGraph V)
    [DecidableRel G.Adj] [DecidableRel G'.Adj],
    Fintype.card V = k + 1 → G.Connected → ¬ G.IsAcyclic → G' ≤ G → G'.IsTree →
      (G'.edgeFinset.card : ℤ) = c ∧ (G.edgeFinset.card : ℤ) = c + (removed G G' : ℤ)

/-- The source sentence as printed: `c = k - 1`. -/
def SourceSentence (k : ℕ) : Prop := SentenceWith k ((k : ℤ) - 1)

/-- The source sentence for every `k` (the located statement, read universally). -/
def UniversalSourceSentence : Prop := ∀ k : ℕ, SourceSentence k

/-- The theorem the source sets out to prove (statement only): a connected graph on `k+1`
vertices with `k` edges is a tree. -/
def SourceTheorem : Prop :=
  ∀ (V : Type) [Fintype V] [DecidableEq V] (k : ℕ) (G : SimpleGraph V) [DecidableRel G.Adj],
    Fintype.card V = k + 1 → G.Connected → G.edgeFinset.card = k → G.IsTree

end Census_SE_math_1291495__q
