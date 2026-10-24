/-
Record SE_math_782216__q (E09, Stack Exchange, question arm).
Source: "Is my induction proof of the handshake lemma correct? (Graph Theory)".
Quoted claim (base case of the induction on the number of edges):
  "Since there aren't any edge the number of vertices must be equal to 1 or 0."
The located statement is `BaseClaim` at a finite simple graph, read universally as
`UniversalBaseClaim`.  The theorem the source is proving is the handshake lemma,
`SourceGoal` (statement only).
-/
import Mathlib

namespace SE_math_782216_q_Census
open SimpleGraph Finset

/-- The source's base-case sentence at a finite simple graph `G`:
"since there aren't any edges the number of vertices must be 1 or 0". -/
def BaseClaim {V : Type*} [Fintype V] (G : SimpleGraph V) [Fintype G.edgeSet] : Prop :=
  G.edgeFinset.card = 0 → Fintype.card V ≤ 1

/-- The quoted claim, read as the universal statement the source needs. -/
def UniversalBaseClaim : Prop :=
  ∀ (V : Type) [Fintype V] (G : SimpleGraph V) [Fintype G.edgeSet], BaseClaim G

/-- The handshake lemma, the theorem the source is proving (statement only). -/
def SourceGoal : Prop :=
  ∀ (V : Type) [Fintype V] (G : SimpleGraph V) [DecidableRel G.Adj],
    ∑ v, G.degree v = 2 * G.edgeFinset.card

end SE_math_782216_q_Census
