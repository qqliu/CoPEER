import Mathlib

/-!
# Graph Theory_15 (sol2) — an endpoint neighbor `z ≠ u` need NOT be an internal vertex `v_i` with `2 < i < n-1`

The candidate solution asserts, in the *rotation case* of a Hamilton-path argument:

> "any endpoint neighbor `z` (`≠ u`) must be an internal vertex `v_i` of the Hamilton
>  path `P` with `2 < i < n-1`."

This is false. The non-path neighbor of an endpoint can sit at position `i = 2`,
which is *internal* but does **not** satisfy the strict band `2 < i < n-1`. In fact for
small `n` that band can be empty: at `n = 4` it reads `2 < i < 3`, which no integer
satisfies, so the claim is vacuously refutable as soon as an endpoint has a non-path
neighbor `≠ u` at all.

**Concrete witness — `K₄` with a fixed edge.**
`G = K₄` on vertices `{u, v, a, w}` (`u = 0`, `v = 1`, `a = 2`, `w = 3`) with the fixed
edge `e = uv`. Take the Hamilton path

```
P = (u, v, a, w),   n = 4,   positions  pos(u)=1, pos(v)=2, pos(a)=3, pos(w)=4.
```

The endpoints of `P` are `u` (position `1`) and `w` (position `4`). In `K₄` the endpoint
`w` is adjacent to `u`, `v`, and `a`. The path edge incident to `w` is `a–w`, so the
**non-path** neighbors of `w` are `u` (position `1`) and `v` (position `2`).

Choose `z = v`. Then:

* `z` is a neighbor of the endpoint `w` in `G` (`K₄` adjacency), and `z ≠ u` — so `z`
  satisfies the hypothesis of the rotation case;
* `pos(z) = 2`, which does **not** satisfy `2 < i < n - 1 = 2 < i < 3`.

Hence the asserted index condition fails on a genuine endpoint neighbor `z ≠ u`,
refuting the claim.

## Modeling choices
* Vertices are `Fin 4` with `u = 0`, `v = 1`, `a = 2`, `w = 3`; mirrors `GT7`/`GT20`/`GT1`.
* `Adj : Fin 4 → Fin 4 → Bool` is the symmetric, loop-free `K₄` adjacency
  (`Adj x y := x ≠ y`), and `degree` is Mathlib `SimpleGraph.degree`; `hamiltonPath` is an actual
  Mathlib walk with `IsHamiltonian` proved.
* The Hamilton path `P = (u,v,a,w)` is recorded two ways: its 1-indexed position map
  `pos : Fin 4 → Nat`, and its edge-membership predicate `PathEdge : Fin 4 → Fin 4 → Bool`
  (the consecutive pairs `u–v`, `v–a`, `a–w`). Both are explicit and decidable.
* `n := 4` and the endpoints are `u` (`pos = 1`) and `w` (`pos = 4`). A *non-path neighbor*
  of `w` is a vertex `y` with `Adj w y` and `¬ PathEdge w y`.
* The claim's index band is the decidable predicate `IndexOK i := 2 < i ∧ i < n - 1`.
  The full refutation exhibits `z = v` satisfying the rotation-case hypothesis
  (`Adj w z`, `z ≠ u`, non-path neighbor) while `IndexOK (pos z)` is false.

**Decidability discipline.** Every statement quantifies only over `Fin 4` / `Bool` /
`Nat`, never over a function type, so each goal reduces in the kernel via plain `decide`
(no `native_decide`, no custom `inductive`/`induction`, library finite cardinalities). The
lone exception is `band_empty`, an unbounded `∀ i : Nat`, which is closed by `omega`.
-/

namespace ProofCerts.GT15

/-- Number of vertices of the witness `K₄` / length of the Hamilton path `P`. -/
def n : Nat := 4

/-- Symmetric, loop-free adjacency of the complete graph `K₄` on `Fin 4`
(`u = 0`, `v = 1`, `a = 2`, `w = 3`): distinct vertices are adjacent. -/
def graph : SimpleGraph (Fin 4) := ⊤

instance : DecidableRel graph.Adj := fun x y =>
  inferInstanceAs (Decidable (x ≠ y))

def Adj (x y : Fin 4) : Bool := decide (graph.Adj x y)

/-- Number of neighbours of `x` (the `GT1` style: an explicit `Nat` sum of
`(Adj x ·).toNat` over the four vertices, no `Finset.card`). -/
def degree (x : Fin 4) : Nat :=
  graph.degree x

/-- 1-indexed position of each vertex along the Hamilton path `P = (u, v, a, w)`:
`pos u = 1`, `pos v = 2`, `pos a = 3`, `pos w = 4`. -/
def pos : Fin 4 → Nat
  | 0 => 1   -- u
  | 1 => 2   -- v
  | 2 => 3   -- a
  | 3 => 4   -- w

/-- Edge-membership of the Hamilton path `P = (u, v, a, w)`: the consecutive pairs
`u–v`, `v–a`, `a–w` (in either orientation). -/
def PathEdge (x y : Fin 4) : Bool :=
  ((x == 0) && (y == 1)) || ((x == 1) && (y == 0)) ||   -- u–v
  ((x == 1) && (y == 2)) || ((x == 2) && (y == 1)) ||   -- v–a
  ((x == 2) && (y == 3)) || ((x == 3) && (y == 2))      -- a–w

/-- The fixed endpoint `u = 0` (first vertex of `P`, position `1`). -/
def u : Fin 4 := 0

/-- The other endpoint `w = 3` (last vertex of `P`, position `4`). -/
def w : Fin 4 := 3

/-- The chosen counterexample neighbor `z = v = 1` (position `2`). -/
def z : Fin 4 := 1

/-- `y` is a *non-path neighbor* of the endpoint `w`: adjacent to `w` in `G` but the
edge `w–y` is not on the Hamilton path. -/
def NonPathNeighborOfW (y : Fin 4) : Bool := Adj w y && !(PathEdge w y)

/-- The claim's index band for an "internal vertex `v_i`": `2 < i ∧ i < n - 1`. -/
def IndexOK (i : Nat) : Prop := 2 < i ∧ i < n - 1

instance (i : Nat) : Decidable (IndexOK i) := by unfold IndexOK; infer_instance

/-- The witness graph has no self-loops. -/
theorem adj_irrefl : ∀ x : Fin 4, Adj x x = false := by decide

/-- The witness graph is undirected: its adjacency is symmetric. -/
theorem adj_symm : ∀ x y : Fin 4, Adj x y = Adj y x := by decide

/-- **`G = K₄`**: every vertex has degree `3 = n - 1`, the complete graph on four
vertices. -/
theorem is_K4 : ∀ x : Fin 4, degree x = 3 := by decide

/-- The path-edge relation is symmetric (the path is undirected). -/
theorem pathEdge_symm : ∀ x y : Fin 4, PathEdge x y = PathEdge y x := by decide

/-- Every path edge is a real edge of `G = K₄`: `P` is a subgraph of `G`. -/
theorem path_subgraph : ∀ x y : Fin 4, PathEdge x y = true → Adj x y = true := by decide

/-- The endpoints of `P` are `u` (position `1`) and `w` (position `n = 4`). -/
theorem endpoints_positions : pos u = 1 ∧ pos w = 4 := by decide

/-- `z = v` is adjacent to the endpoint `w` in `G = K₄`. -/
theorem z_adj_w : Adj w z = true := by decide

/-- `z = v` differs from the fixed endpoint `u`. -/
theorem z_ne_u : z ≠ u := by decide

/-- `z = v` is a *non-path* neighbor of the endpoint `w` (the edge `w–v` is not on `P`). -/
theorem z_nonpath_neighbor : NonPathNeighborOfW z = true := by decide

/-- The position of `z = v` along `P` is `2`. -/
theorem z_pos : pos z = 2 := by decide

/-- The claim's band is **empty** at `n = 4`: no natural number `i` satisfies
`2 < i < n - 1 = 2 < i < 3`. (Unbounded `∀ i : Nat`, so closed by `omega` after
unfolding the band, rather than by `decide`.) -/
theorem band_empty : ∀ i : Nat, ¬ IndexOK i := by
  intro i hi
  unfold IndexOK n at hi
  omega

/-- The position of `z = v` does **not** satisfy the claim's index condition
`2 < pos z < n - 1`. -/
theorem z_index_bad : ¬ IndexOK (pos z) := by decide

/--
**Refutation.** In the rotation case the candidate claim says: every endpoint neighbor
`z ≠ u` must be an internal vertex `v_i` of `P` with `2 < i < n - 1`. On the witness
`K₄`/`P = (u,v,a,w)` this fails:

* `z = v` is a genuine endpoint neighbor (`Adj w z`, a non-path neighbor of the endpoint
  `w`) with `z ≠ u` — so it satisfies the rotation-case hypothesis; yet
* its position `pos z = 2` does **not** satisfy `2 < i < n - 1`.

We package exactly such a `z`: all of the hypothesis conjuncts hold while the index
conclusion `IndexOK (pos z)` is refuted. (`band_empty` records the stronger fact that
the band is altogether empty at `n = 4`.)
-/
theorem claim_fails :
    ∃ y : Fin 4,
      Adj w y = true ∧ y ≠ u ∧ NonPathNeighborOfW y = true ∧ ¬ IndexOK (pos y) :=
  ⟨z, z_adj_w, z_ne_u, z_nonpath_neighbor, z_index_bad⟩

/-- The concrete path is a Mathlib graph walk, not just position labels. -/
def hamiltonPath : graph.Walk (0 : Fin 4) 3 :=
  .cons (by decide : graph.Adj 0 1) (.cons (by decide : graph.Adj 1 2) (.cons (by decide : graph.Adj 2 3) .nil))

theorem hamiltonPath_isHamiltonian : hamiltonPath.IsHamiltonian := by
  change ∀ v : Fin 4, ([0,1,2,3] : List (Fin 4)).count v = 1
  decide

/-- Source graph degree, Hamilton path, and the excluded endpoint neighbor. -/
theorem certificate :
    (∀ v : Fin 4, graph.degree v = 3) ∧ hamiltonPath.IsHamiltonian ∧
    graph.Adj w z ∧ z ≠ u ∧ NonPathNeighborOfW z = true ∧ ¬ IndexOK (pos z) := by
  exact ⟨is_K4, hamiltonPath_isHamiltonian, by decide, z_ne_u,
    z_nonpath_neighbor, z_index_bad⟩

end ProofCerts.GT15
