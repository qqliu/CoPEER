/-
Record SE_math_994847__q (E10).

Source: A is the adjacency matrix of a finite simple graph on n vertices.  Located claim:
  "If any A^{n-1}_{i,j} would be 0, that would mean that there would not be any path
   connecting those vertices.  Thus, the graph would be disconnected."
`LocalClaimEntrywise G` is the entrywise reading, `LocalClaim G` the graph-level conclusion;
both are read over every finite simple graph (`UniversalLocalClaim`,
`UniversalLocalClaimEntrywise`).  Matrices are over ℕ (entries count walks).
-/

import Mathlib

namespace SE_math_994847_q
open Matrix

section General

variable {V : Type*} [Fintype V] [DecidableEq V] (G : SimpleGraph V) [DecidableRel G.Adj]

/-- `A^(n-1)` has a zero entry, where `n` is the number of vertices. -/
def HasZeroEntry : Prop :=
  ∃ i j : V, (G.adjMatrix ℕ ^ (Fintype.card V - 1)) i j = 0

/-- The source's local claim, entrywise reading: "If any `A^{n-1}_{i,j}` would be 0, that would
mean that there would not be any path connecting those vertices." -/
def LocalClaimEntrywise : Prop :=
  ∀ i j : V, (G.adjMatrix ℕ ^ (Fintype.card V - 1)) i j = 0 → ¬ G.Reachable i j

/-- The source's local claim, graph-level conclusion: "Thus, the graph would be disconnected." -/
def LocalClaim : Prop := HasZeroEntry G → ¬ G.Connected

end General

/-- The graph-level claim over every finite simple graph. -/
def UniversalLocalClaim : Prop :=
  ∀ (V : Type) [Fintype V] [DecidableEq V] (G : SimpleGraph V) [DecidableRel G.Adj], LocalClaim G

/-- The entrywise claim over every finite simple graph. -/
def UniversalLocalClaimEntrywise : Prop :=
  ∀ (V : Type) [Fintype V] [DecidableEq V] (G : SimpleGraph V) [DecidableRel G.Adj],
    LocalClaimEntrywise G

end SE_math_994847_q
