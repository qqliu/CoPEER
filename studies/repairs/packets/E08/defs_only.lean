import Mathlib

/- Record SE_math_1868681__q (E08).
Source sentence: "the greatest number of edges on a bipartite graph on p [vertices] is p^2/4".
Bipartite means 2-colourable (Mathlib `IsBipartite`); colour classes may be empty; the
printed formula p^2/4 is read in ℚ (no floor), and "greatest" means an attained maximum
(`IsGreatest`).  The located statement is `SourceClaim p`, read for every p as
`UniversalSourceClaim`. -/
set_option maxRecDepth 10000
set_option maxHeartbeats 4000000

namespace Census_SE_math_1868681__q

/-- A simple graph on `Fin n` from a list of edges. -/
def graph (n : ℕ) (es : List (ℕ × ℕ)) : SimpleGraph (Fin n) where
 Adj i j := i ≠ j ∧ ((i.val,j.val) ∈ es ∨ (j.val,i.val) ∈ es)
 symm := fun i j h => ⟨h.1.symm, h.2.symm⟩
 loopless := ⟨fun _ h => h.1 rfl⟩
instance (n : ℕ) (es : List (ℕ × ℕ)) : DecidableRel (graph n es).Adj := fun _ _ => inferInstanceAs (Decidable (_ ∧ _))

open SimpleGraph

/-- Number of edges of a simple graph, free of decidability instances. -/
noncomputable def edges {V : Type*} (G : SimpleGraph V) : ℕ := G.edgeSet.ncard

/-- The edge counts of the bipartite (2-colourable, Mathlib `IsBipartite`) simple graphs on
`p` labelled vertices.  Colour classes may be empty. -/
def BipCounts (p : ℕ) : Set ℕ :=
  {m | ∃ G : SimpleGraph (Fin p), G.IsBipartite ∧ edges G = m}

/-- The source sentence at `p`: "the greatest number of edges on a bipartite graph on p
[vertices] is p^2/4", as a precise statement in the rationals (no floor). -/
def SourceClaim (p : ℕ) : Prop :=
  IsGreatest ((fun m : ℕ => (m : ℚ)) '' BipCounts p) ((p : ℚ) ^ 2 / 4)

/-- The source sentence for every `p`. -/
def UniversalSourceClaim : Prop := ∀ p : ℕ, SourceClaim p

end Census_SE_math_1868681__q
