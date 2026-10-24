/-!
Record: reddit_askmath_pe1euu
Public source: https://www.reddit.com/r/askmath/comments/pe1euu/could_someone_verify_my_graph_theory_proof/

Exact target scope: the quoted induction branch claims that, when adjoining the
remaining vertex `u` creates no new cycle, the resulting connected graph is a
tree and hence is two-colourable.  The concrete witness has vertices
`{a,b,c,u}` and exactly the undirected edges `a-b`, `b-c`, `c-a`, and `a-u`.
The predecessor induced on exactly `{a,b,c}` is the triangle, and the final
graph is obtained by adjoining `u` with sole neighbour `a`.  Thus no simple
cycle contains `u`, while the old closed sequence `a,b,c,a` remains a simple
cycle; both the predecessor and final graph are not two-colourable.

Material modelling judgments: adjacency is an exact Boolean relation and is
separately checked symmetric and irreflexive.  Walks and paths are lists of
adjacent vertices, with paths additionally having no repeated vertex.  A simple
cycle is a closed adjacent list with at least three edges whose vertices before
the repeated endpoint are distinct.  Since this type has exactly four
vertices, exhaustive closed lists with three or four distinct vertices are
exactly all possible simple cycles; `acyclic` is their absence.  Connectivity
exhausts all simple paths of at most four vertices, which is exact on this
finite type.  Proper two-colourability exhausts every function from the four
vertices to `Bool`.  “Creates no cycle” is interpreted, as in the full-source
semantic audit, as absence of a new simple cycle through the adjoined `u`, not
as the already-false assertion that the whole predecessor is acyclic.

Negative control: deleting exactly `c-a` leaves precisely `a-b`, `b-c`, and
`a-u`.  Exhaustive cycle checking proves this connected graph acyclic/a tree,
and the explicit colouring `a=c=false`, `b=u=true` is proper.  This detects a
vacuous or uniformly-false encoding and detects omission of the deleted edge.
-/

namespace RedditAskmathPe1euu

inductive Vertex where
  | a | b | c | u
  deriving DecidableEq, BEq

abbrev Adj := Vertex -> Vertex -> Bool

def allVertices (p : Vertex -> Bool) : Bool :=
  p .a && p .b && p .c && p .u

def anyVertex (p : Vertex -> Bool) : Bool :=
  p .a || p .b || p .c || p .u

def finalAdj : Adj
  | .a, .b | .b, .a => true
  | .b, .c | .c, .b => true
  | .c, .a | .a, .c => true
  | .a, .u | .u, .a => true
  | _, _ => false

def inPredecessor : Vertex -> Bool
  | .a | .b | .c => true
  | .u => false

def predecessorAdj (x y : Vertex) : Bool :=
  inPredecessor x && inPredecessor y && finalAdj x y

def leafEdge : Adj
  | .a, .u | .u, .a => true
  | _, _ => false

def controlAdj : Adj
  | .a, .b | .b, .a => true
  | .b, .c | .c, .b => true
  | .a, .u | .u, .a => true
  | _, _ => false

def sameAdj (r s : Adj) : Bool :=
  allVertices fun x => allVertices fun y => (r x y) == (s x y)

def simpleUndirected (adj : Adj) : Bool :=
  (allVertices fun x => !(adj x x)) &&
  (allVertices fun x => allVertices fun y =>
    (adj x y) == (adj y x))

def containsVertex (needle : Vertex) : List Vertex -> Bool
  | [] => false
  | x :: xs => (needle == x) || containsVertex needle xs

def noRepeatedVertices : List Vertex -> Bool
  | [] => true
  | x :: xs => !(containsVertex x xs) && noRepeatedVertices xs

def walk (adj : Adj) : List Vertex -> Bool
  | [] => false
  | [_] => true
  | x :: y :: rest => adj x y && walk adj (y :: rest)

def path (adj : Adj) (vertices : List Vertex) : Bool :=
  walk adj vertices && noRepeatedVertices vertices

def initVertices : List Vertex -> List Vertex
  | [] => []
  | [_] => []
  | x :: xs => x :: initVertices xs

def atLeastThreeEdges : List Vertex -> Bool
  | _ :: _ :: _ :: _ :: _ => true
  | _ => false

def startsAndEndsSame : List Vertex -> Bool
  | [] => false
  | first :: rest =>
      let rec lastEquals : List Vertex -> Bool
        | [] => true
        | [last] => last == first
        | _ :: xs => lastEquals xs
      lastEquals rest

def simpleCycle (adj : Adj) (vertices : List Vertex) : Bool :=
  atLeastThreeEdges vertices &&
  startsAndEndsSame vertices &&
  walk adj vertices &&
  noRepeatedVertices (initVertices vertices)

def hasSimpleCycle (adj : Adj) : Bool :=
  (anyVertex fun x => anyVertex fun y => anyVertex fun z =>
    simpleCycle adj [x, y, z, x]) ||
  (anyVertex fun w => anyVertex fun x => anyVertex fun y => anyVertex fun z =>
    simpleCycle adj [w, x, y, z, w])

def hasSimpleCycleThrough (adj : Adj) (marked : Vertex) : Bool :=
  (anyVertex fun x => anyVertex fun y => anyVertex fun z =>
    simpleCycle adj [x, y, z, x] &&
    containsVertex marked (initVertices [x, y, z, x])) ||
  (anyVertex fun w => anyVertex fun x => anyVertex fun y => anyVertex fun z =>
    simpleCycle adj [w, x, y, z, w] &&
    containsVertex marked (initVertices [w, x, y, z, w]))

def acyclic (adj : Adj) : Bool :=
  !(hasSimpleCycle adj)

def hasPath (adj : Adj) (source target : Vertex) : Bool :=
  ((source == target) && path adj [source]) ||
  path adj [source, target] ||
  (anyVertex fun x => path adj [source, x, target]) ||
  (anyVertex fun x => anyVertex fun y =>
    path adj [source, x, y, target])

def connected (adj : Adj) : Bool :=
  allVertices fun source => allVertices fun target =>
    hasPath adj source target

def tree (adj : Adj) : Bool :=
  connected adj && acyclic adj

def coloring (ca cb cc cu : Bool) : Vertex -> Bool
  | .a => ca
  | .b => cb
  | .c => cc
  | .u => cu

def properColoring (adj : Adj) (color : Vertex -> Bool) : Bool :=
  allVertices fun x => allVertices fun y =>
    !(adj x y) || !(color x == color y)

def anyBool (p : Bool -> Bool) : Bool :=
  p false || p true

def twoColorable (adj : Adj) : Bool :=
  anyBool fun ca => anyBool fun cb => anyBool fun cc => anyBool fun cu =>
    properColoring adj (coloring ca cb cc cu)

def predecessorIsInduced : Bool :=
  allVertices fun x => allVertices fun y =>
    predecessorAdj x y ==
      (inPredecessor x && inPredecessor y && finalAdj x y)

def predecessorHasExactlyABC : Bool :=
  inPredecessor .a && inPredecessor .b && inPredecessor .c &&
  !(inPredecessor .u)

def finalIsPredecessorWithLeafU : Bool :=
  sameAdj finalAdj (fun x y => predecessorAdj x y || leafEdge x y)

def uHasExactlyNeighborA : Bool :=
  allVertices fun x => finalAdj .u x == (x == .a)

def negativeControlSummary : Bool :=
  simpleUndirected controlAdj &&
  connected controlAdj &&
  acyclic controlAdj &&
  tree controlAdj &&
  properColoring controlAdj (coloring false true false true) &&
  twoColorable controlAdj

abbrev PublishedClaimAtWitness : Prop :=
  simpleUndirected finalAdj = true ->
  simpleUndirected predecessorAdj = true ->
  predecessorHasExactlyABC = true ->
  predecessorIsInduced = true ->
  finalIsPredecessorWithLeafU = true ->
  connected finalAdj = true ->
  uHasExactlyNeighborA = true ->
  hasSimpleCycleThrough finalAdj .u = false ->
  simpleCycle predecessorAdj [.a, .b, .c, .a] = true ->
  twoColorable predecessorAdj = false ->
  tree finalAdj = true /\ twoColorable finalAdj = true

/-- The exact sole-neighbour premise, together with simplicity, rules out every
exhaustively represented simple cycle through the newly adjoined vertex `u`. -/
theorem no_new_simple_cycle_through_u_from_unique_neighbor :
    simpleUndirected finalAdj = true ->
    uHasExactlyNeighborA = true ->
    hasSimpleCycleThrough finalAdj .u = false := by
  decide

/-- The triangle defeats every proposed Boolean colouring, stated for an
arbitrary colour function rather than only as a computed existential flag. -/
theorem final_triangle_defeats_every_coloring (color : Vertex -> Bool) :
    properColoring finalAdj color = false := by
  cases ha : color .a <;>
  cases hb : color .b <;>
  cases hc : color .c <;>
  simp [properColoring, allVertices, finalAdj, ha, hb, hc]

/-- The induction-stage predecessor is itself the odd triangle, so its
non-two-colourability is preserved rather than silently replaced by a stronger
induction hypothesis. -/
theorem predecessor_triangle_defeats_every_coloring
    (color : Vertex -> Bool) :
    properColoring predecessorAdj color = false := by
  cases ha : color .a <;>
  cases hb : color .b <;>
  cases hc : color .c <;>
  simp [properColoring, allVertices, predecessorAdj, inPredecessor,
    finalAdj, ha, hb, hc]

/-- Load-bearing refutation certificate.  All source-context premises hold:
the predecessor is the induced odd triangle, the final graph is its connected
simple extension by leaf `u`, and no new simple cycle goes through `u`.  The
old triangle nevertheless makes the final graph cyclic, not a tree, and not
two-colourable.  The derived negative-control summary is true as well. -/
theorem reddit_askmath_pe1euu_refutation :
    simpleUndirected finalAdj = true /\
    simpleUndirected predecessorAdj = true /\
    predecessorHasExactlyABC = true /\
    predecessorIsInduced = true /\
    finalIsPredecessorWithLeafU = true /\
    connected finalAdj = true /\
    uHasExactlyNeighborA = true /\
    hasSimpleCycleThrough finalAdj .u = false /\
    simpleCycle predecessorAdj [.a, .b, .c, .a] = true /\
    hasSimpleCycle predecessorAdj = true /\
    acyclic predecessorAdj = false /\
    twoColorable predecessorAdj = false /\
    simpleCycle finalAdj [.a, .b, .c, .a] = true /\
    hasSimpleCycle finalAdj = true /\
    acyclic finalAdj = false /\
    tree finalAdj = false /\
    twoColorable finalAdj = false /\
    negativeControlSummary = true /\
    Not PublishedClaimAtWitness := by
  decide

/-- Meaningful edge-deletion negative control.  Exactly `c-a` is absent while
all three retained undirected edges are present; the result is connected,
acyclic, a tree, and accepts the independently verified proper colouring. -/
theorem reddit_askmath_pe1euu_negative_control :
    controlAdj .c .a = false /\
    controlAdj .a .c = false /\
    controlAdj .a .b = true /\ controlAdj .b .a = true /\
    controlAdj .b .c = true /\ controlAdj .c .b = true /\
    controlAdj .a .u = true /\ controlAdj .u .a = true /\
    simpleUndirected controlAdj = true /\
    connected controlAdj = true /\
    hasSimpleCycle controlAdj = false /\
    acyclic controlAdj = true /\
    tree controlAdj = true /\
    properColoring controlAdj (coloring false true false true) = true /\
    twoColorable controlAdj = true := by
  decide

end RedditAskmathPe1euu

#print axioms RedditAskmathPe1euu.no_new_simple_cycle_through_u_from_unique_neighbor
#print axioms RedditAskmathPe1euu.final_triangle_defeats_every_coloring
#print axioms RedditAskmathPe1euu.predecessor_triangle_defeats_every_coloring
#print axioms RedditAskmathPe1euu.reddit_askmath_pe1euu_refutation
#print axioms RedditAskmathPe1euu.reddit_askmath_pe1euu_negative_control
