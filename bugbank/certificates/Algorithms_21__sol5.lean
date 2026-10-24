/- Automated review revision: standard Lean library operations replace duplicate utilities. Source-specific graph algorithms retain their original executable definitions. -/
/-!
# Algorithms_21__sol5: source-exact base-case arithmetic correction

The selected release theorem is `base_case_refuted`. The source explicitly
writes `R(1) = 0 = 2^1 - 1`; its one-vertex graph has no edges, so zero
relaxations cannot equal one. This is an intermediate arithmetic slip, not
an asymptotic lower-bound refutation. The extracted later comparison is ambiguous (it may mean2^(n-1))
and is not selected as a counterexample.
-/

set_option maxRecDepth 100000
set_option maxHeartbeats 4000000

namespace Algorithms_21_sol5

/-! ## The graph family `G_n` -/

/-- Edge weight of every out-edge of `v_i`: `w(v_i, v_j) = -(2^i)`. -/
def wt (i : Nat) : Int := -((2 : Int) ^ i)

/-- Edge list of `G_n`: all arcs `(i, j, -(2^i))` with `i < j < n`. -/
def edgesG (n : Nat) : List (Nat × Nat × Int) :=
  (List.range n).foldr
    (fun i acc =>
      ((List.range n).filterMap (fun j => if i < j then some (i, j, wt i) else none)) ++ acc)
    []

/-! ## Distance vectors (`Option Int`, `none` = +∞) -/

/-- `dist[k]` (`none` when out of range — never hit: indices come from `List.range n`). -/
def getD (xs : List (Option Int)) (i : Nat) : Option Int := xs.getD i none

/-- Functional update `dist[k] := v` (no-op out of range). -/
def setD (xs : List (Option Int)) (i : Nat) (v : Option Int) : List (Option Int) := xs.set i v

/-- `a < b` with `none` = +∞ (so `some _ < none`, never `none < _`). -/
def oLt : Option Int → Option Int → Bool
  | none, _ => false
  | some _, none => true
  | some a, some b => decide (a < b)

/-- Min with `none` = +∞. -/
def oMin (a b : Option Int) : Option Int :=
  match oLt a b with | true => a | false => b

def memNat (x : Nat) (xs : List Nat) : Bool := xs.contains x

/-! ## Textbook Dijkstra (variant A: no re-insertion), deterministic -/

/-- Scan candidates in increasing index order, keeping the best-so-far and
replacing it only on a STRICTLY smaller label — so ties keep the lowest index.
Unvisited-only; `none` labels (+∞) are never selected. -/
def pickMinAux (dist : List (Option Int)) (vis : List Nat) :
    List Nat → Option Nat → Option Nat
  | [], best => best
  | v :: vs, best =>
      pickMinAux dist vis vs
        (match memNat v vis with
         | true => best
         | false =>
           match getD dist v with
           | none => best
           | some _ =>
             match best with
             | none => some v
             | some u => match oLt (getD dist v) (getD dist u) with
               | true => some v
               | false => best)

/-- Extract-Min over vertices `0 … n-1`. -/
def pickMin (n : Nat) (dist : List (Option Int)) (vis : List Nat) : Option Nat :=
  pickMinAux dist vis (List.range n) none

/-- Relax every out-edge of `u` (label `du`) exactly once.  Returns the updated
distance vector and the NUMBER OF RELAX INVOCATIONS (incremented for every
out-edge of `u`, whether or not the relaxation test succeeds). -/
def relaxOut (u : Nat) (du : Int) :
    List (Nat × Nat × Int) → List (Option Int) → List (Option Int) × Nat
  | [], dist => (dist, 0)
  | e :: es, dist =>
      match e.1 == u with
      | true =>
        match relaxOut u du es
                (setD dist e.2.1 (oMin (getD dist e.2.1) (some (du + e.2.2)))) with
        | (dist', c) => (dist', c + 1)
      | false => relaxOut u du es dist

/-- Main loop, fuel-bounded (fuel `n` suffices: at most `n` extractions). -/
def loop (edges : List (Nat × Nat × Int)) (n : Nat) :
    Nat → List (Option Int) → List Nat → Nat → List (Option Int) × Nat
  | 0, dist, _, cnt => (dist, cnt)
  | f + 1, dist, vis, cnt =>
      match pickMin n dist vis with
      | none => (dist, cnt)
      | some u =>
        match getD dist u with
        | none => (dist, cnt)   -- unreachable: pickMin only returns finite labels
        | some du =>
          match relaxOut u du edges dist with
          | (dist', c) => loop edges n f dist' (u :: vis) (cnt + c)

/-- Initial labels: `dist[0] = 0`, everything else +∞. -/
def initDist (n : Nat) : List (Option Int) :=
  (List.range n).map (fun v => match v == 0 with
    | true => some (0 : Int)
    | false => (none : Option Int))

/-- One full run of variant-A Dijkstra from `v_0` on `G_n`. -/
def dijkstraRun (n : Nat) : List (Option Int) × Nat :=
  loop (edgesG n) n n (initDist n) [] 0

/-- `R_A(n)`: total Relax invocations of the run. -/
def relaxCountA (n : Nat) : Nat := (dijkstraRun n).2

/-- Final label vector of the run (positive control only). -/
def finalDist (n : Nat) : List (Option Int) := (dijkstraRun n).1

/-- The record's claim at `n`: the run performs at least `2^n - 1` Relax
invocations. -/
def claimAt (n : Nat) : Bool := Nat.ble (2 ^ n - 1) (relaxCountA n)

/-!
## (a) Base case — variant-independent refutation at `n = 1`
-/

/-- The proof's base case writes `R(1) = 0 = 2^1 - 1`, i.e. `0 = 1`: false.
`G_1` has NO edges, so any edge-attached Relax semantics gives `R(1) = 0`,
and the simulation agrees; hence `R(1) ≥ 2^1 - 1` fails. -/
theorem base_case_refuted :
    (2 ^ 1 - 1 = 1)
  ∧ ¬ (0 = 2 ^ 1 - 1)
  ∧ (edgesG 1 = [])
  ∧ (relaxCountA 1 = 0)
  ∧ (claimAt 1 = false) := by decide

end Algorithms_21_sol5
