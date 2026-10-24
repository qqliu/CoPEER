/- Record SE_cstheory_2312__a2318 (E06, cstheory.stackexchange reply a2318 to question 2312).
Core Lean only (no imports, no Mathlib).

Weighted edge lists over vertices 0 .. n-1.  From a graph G with designated vertices u ≠ v
the source builds G* = G plus, for every other vertex k, the two edges (u,k) and (v,k) of
weight -d, plus the edge (u,v) of weight a.  Notation of the source: T = wsum G,
f = a - (n-2) d, written inline as `a - ((n : Int) - 2) * d`.  The source stipulates
T > 0 and -0.99 T ≤ f ≤ -0.49 T (the "window").
`build`/`tsum` merge parallel edges (additively when `addMode = true`, by overwrite otherwise).
The located statement `LocalClaim` is the source's identity "the new total is T + f" together
with the positivity of the new total, under the source's hypotheses.
`PositivityUnderWindow` is the positivity half alone. -/

set_option maxRecDepth 10000

namespace SE_cstheory_2312_a2318_Census

abbrev WEdge := Nat × Nat × Int

def wsum (es : List WEdge) : Int := (es.map (fun e => e.2.2)).sum

def penaltiesBelow (u v : Nat) (d : Int) : Nat → List WEdge
  | 0 => []
  | k + 1 =>
      (if k = u ∨ k = v then [] else [(u, k, -d), (v, k, -d)]) ++ penaltiesBelow u v d k

def gstar (n u v : Nat) (d a : Int) (G : List WEdge) : List WEdge :=
  G ++ penaltiesBelow u v d n ++ [(u, v, a)]

def norm (i j : Nat) : Nat × Nat := if i ≤ j then (i, j) else (j, i)

def applyEdge (addMode : Bool) : List ((Nat × Nat) × Int) → WEdge → List ((Nat × Nat) × Int)
  | [], (i, j, w) => [(norm i j, w)]
  | (p, x) :: rest, (i, j, w) =>
      if p = norm i j then (p, if addMode then x + w else w) :: rest
      else (p, x) :: applyEdge addMode rest (i, j, w)

def build (addMode : Bool) : List WEdge → List ((Nat × Nat) × Int) → List ((Nat × Nat) × Int)
  | [], m => m
  | e :: es, m => build addMode es (applyEdge addMode m e)

def tsum (es : List ((Nat × Nat) × Int)) : Int := (es.map (fun e => e.2)).sum

/-- The located claim: under the source's hypotheses, the new total equals `T + f` and is
positive. -/
def LocalClaim : Prop :=
  ∀ (n u v : Nat) (d a : Int) (G : List WEdge),
    u ≠ v → u < n → v < n → 0 < wsum G →
    (-99 : Int) * wsum G ≤ 100 * (a - ((n : Int) - 2) * d) →
    100 * (a - ((n : Int) - 2) * d) ≤ (-49 : Int) * wsum G →
    wsum (gstar n u v d a G) = wsum G + (a - ((n : Int) - 2) * d)
      ∧ 0 < wsum (gstar n u v d a G)

/-- The positivity half of the located claim, alone. -/
def PositivityUnderWindow : Prop :=
  ∀ (n u v : Nat) (d a : Int) (G : List WEdge),
    u ≠ v → u < n → v < n → 0 < wsum G →
    (-99 : Int) * wsum G ≤ 100 * (a - ((n : Int) - 2) * d) →
    100 * (a - ((n : Int) - 2) * d) ≤ (-49 : Int) * wsum G →
    0 < wsum (gstar n u v d a G)

end SE_cstheory_2312_a2318_Census
