/-!
Record: `reddit_learnmath_egpgy9`

Public source:
https://www.reddit.com/r/learnmath/comments/egpgy9/vector_geometry_problem_leading_to_two/

Exact source claim: “a quadrilateral with all four sides equal must be a
square.”  `SourceClaim` states this universally over ordered, simple, strictly
convex counterclockwise quadrilaterals.  Refuting the claim inside this
well-behaved subclass also refutes the unrestricted source assertion.

Verified witness: the ordered vertices are `A = (0,0)`, `B = (5,0)`,
`C = (8,4)`, and `D = (3,4)`.  All six pairs of vertices are distinct.  For
each directed boundary edge, both nonincident vertices lie strictly to its
left; all eight determinants are 20.  Thus the certificate checks simplicity,
strict convexity, and counterclockwise orientation rather than relying only on
the four local turns.  The four squared side lengths are positive and equal to
25, while the first adjacent-edge dot product is 15 rather than zero.  Hence
this is an equal-sided rhombus, not a square.

Material modelling judgments: coordinates and every geometric computation use
`Int`.  Vector subtraction, squared Euclidean length, dot product, and
determinant have their standard polynomial definitions.  `intEq` is the exact
constructor equality test on the unbounded `Int` type; it is used because the
zero-import prelude does not install all of the proposition-level `Decidable`
instances needed by one large `decide`.  `pointEq` is consequently exact
coordinate equality.  `PairwiseDistinct` contains all six exact inequality
tests.  `StrictConvexCCW` contains the eight strict left-of-directed-edge
tests, which for four ordered vertices exactly enforce a simple strictly
convex CCW quadrilateral.  `EqualSides` includes positivity of the first
squared length and equality of all four boundary lengths, excluding a
collapsed zero-length case.  `RightAngles` checks all four successive dot
products.  `Square` retains the quadrilateral and equal-side hypotheses and
adds all four right angles; no geometric implication is assumed.

`positiveInt` is the exact constructor characterization of strict positivity:
precisely the positive `Int.ofNat` successors produce `true`; zero and every
negative integer produce `false`.  Neither it nor `intEq` introduces a finite
bound or an approximation.

Negative control: `A = (0,0)`, `B = (5,0)`, `C = (5,5)`, `D = (0,5)` has all
eight left-side determinants and all four squared side lengths equal to 25,
and all four successive dot products equal to zero.  It satisfies the same
domain and equal-side tests and is a square, detecting an encoding that made
`Square` uniformly false or confused equal sides with failure.

Route review: this remains `SELF_CONTAINED_LEAN`.  Integer-coordinate Euclidean
geometry makes every witness and control obligation exactly kernel-computable.
The file is prelude-only.  Concrete reductions are proved with `rfl`, and the
two compound certificates are assembled from small explicit lemmas; no
trust-extending declarations, external tactics, or large `decide` search is
used.
-/

namespace RedditLearnmathEgpgy9

structure Point where
  x : Int
  y : Int

def sub (p q : Point) : Point :=
  { x := p.x - q.x, y := p.y - q.y }

def sqLen (v : Point) : Int :=
  v.x * v.x + v.y * v.y

def dot (u v : Point) : Int :=
  u.x * v.x + u.y * v.y

def det (u v : Point) : Int :=
  u.x * v.y - u.y * v.x

/- Exact, unbounded equality on integers, exposed as a Boolean so concrete
facts remain kernel-reducible in a zero-import file. -/
def intEq : Int -> Int -> Bool
  | .ofNat m, .ofNat n => m == n
  | .negSucc m, .negSucc n => m == n
  | _, _ => false

def positiveInt : Int -> Bool
  | .ofNat 0 => false
  | .ofNat (Nat.succ _) => true
  | .negSucc _ => false

def pointEq (p q : Point) : Bool :=
  intEq p.x q.x && intEq p.y q.y

structure Quad where
  a : Point
  b : Point
  c : Point
  d : Point

def edgeAB (q : Quad) : Point := sub q.b q.a
def edgeBC (q : Quad) : Point := sub q.c q.b
def edgeCD (q : Quad) : Point := sub q.d q.c
def edgeDA (q : Quad) : Point := sub q.a q.d

def PairwiseDistinct (q : Quad) : Prop :=
  pointEq q.a q.b = false /\
  pointEq q.a q.c = false /\
  pointEq q.a q.d = false /\
  pointEq q.b q.c = false /\
  pointEq q.b q.d = false /\
  pointEq q.c q.d = false

def StrictConvexCCW (q : Quad) : Prop :=
  positiveInt (det (edgeAB q) (sub q.c q.a)) = true /\
  positiveInt (det (edgeAB q) (sub q.d q.a)) = true /\
  positiveInt (det (edgeBC q) (sub q.d q.b)) = true /\
  positiveInt (det (edgeBC q) (sub q.a q.b)) = true /\
  positiveInt (det (edgeCD q) (sub q.a q.c)) = true /\
  positiveInt (det (edgeCD q) (sub q.b q.c)) = true /\
  positiveInt (det (edgeDA q) (sub q.b q.d)) = true /\
  positiveInt (det (edgeDA q) (sub q.c q.d)) = true

def Quadrilateral (q : Quad) : Prop :=
  PairwiseDistinct q /\ StrictConvexCCW q

def EqualSides (q : Quad) : Prop :=
  positiveInt (sqLen (edgeAB q)) = true /\
  intEq (sqLen (edgeAB q)) (sqLen (edgeBC q)) = true /\
  intEq (sqLen (edgeBC q)) (sqLen (edgeCD q)) = true /\
  intEq (sqLen (edgeCD q)) (sqLen (edgeDA q)) = true

def RightAngles (q : Quad) : Prop :=
  intEq (dot (edgeAB q) (edgeBC q)) 0 = true /\
  intEq (dot (edgeBC q) (edgeCD q)) 0 = true /\
  intEq (dot (edgeCD q) (edgeDA q)) 0 = true /\
  intEq (dot (edgeDA q) (edgeAB q)) 0 = true

def Square (q : Quad) : Prop :=
  Quadrilateral q /\ EqualSides q /\ RightAngles q

def rhombusWitness : Quad :=
  { a := { x := 0, y := 0 }
    b := { x := 5, y := 0 }
    c := { x := 8, y := 4 }
    d := { x := 3, y := 4 } }

def squareControl : Quad :=
  { a := { x := 0, y := 0 }
    b := { x := 5, y := 0 }
    c := { x := 5, y := 5 }
    d := { x := 0, y := 5 } }

abbrev SourceClaim : Prop :=
  forall q, Quadrilateral q -> EqualSides q -> Square q

/- Small, structurally bounded proofs replace the failed deeply nested
`decide` synthesis.  Each leaf below closes by kernel reduction. -/

theorem rhombusWitness_pairwise : PairwiseDistinct rhombusWitness := by
  constructor
  · rfl
  constructor
  · rfl
  constructor
  · rfl
  constructor
  · rfl
  constructor
  · rfl
  · rfl

theorem rhombusWitness_strictConvexCCW :
    StrictConvexCCW rhombusWitness := by
  constructor
  · rfl
  constructor
  · rfl
  constructor
  · rfl
  constructor
  · rfl
  constructor
  · rfl
  constructor
  · rfl
  constructor
  · rfl
  · rfl

theorem rhombusWitness_quadrilateral : Quadrilateral rhombusWitness := by
  exact And.intro rhombusWitness_pairwise rhombusWitness_strictConvexCCW

theorem rhombusWitness_equalSides : EqualSides rhombusWitness := by
  constructor
  · rfl
  constructor
  · rfl
  constructor
  · rfl
  · rfl

theorem rhombusWitness_notRightAngles :
    Not (RightAngles rhombusWitness) := by
  intro right
  have impossible : false = true := right.1
  cases impossible

theorem rhombusWitness_notSquare : Not (Square rhombusWitness) := by
  intro alleged
  exact rhombusWitness_notRightAngles alleged.2.2

/- The following audited proposition exposes every concrete calculation:
all six distinctions, all eight determinants (each exactly 20), all four
squared side lengths (each exactly 25), the failing adjacent dot product
(exactly 15), and every resulting geometric predicate. -/
theorem rhombusWitness_certificate :
    pointEq rhombusWitness.a rhombusWitness.b = false /\
    pointEq rhombusWitness.a rhombusWitness.c = false /\
    pointEq rhombusWitness.a rhombusWitness.d = false /\
    pointEq rhombusWitness.b rhombusWitness.c = false /\
    pointEq rhombusWitness.b rhombusWitness.d = false /\
    pointEq rhombusWitness.c rhombusWitness.d = false /\
    intEq (det (edgeAB rhombusWitness)
      (sub rhombusWitness.c rhombusWitness.a)) 20 = true /\
    intEq (det (edgeAB rhombusWitness)
      (sub rhombusWitness.d rhombusWitness.a)) 20 = true /\
    intEq (det (edgeBC rhombusWitness)
      (sub rhombusWitness.d rhombusWitness.b)) 20 = true /\
    intEq (det (edgeBC rhombusWitness)
      (sub rhombusWitness.a rhombusWitness.b)) 20 = true /\
    intEq (det (edgeCD rhombusWitness)
      (sub rhombusWitness.a rhombusWitness.c)) 20 = true /\
    intEq (det (edgeCD rhombusWitness)
      (sub rhombusWitness.b rhombusWitness.c)) 20 = true /\
    intEq (det (edgeDA rhombusWitness)
      (sub rhombusWitness.b rhombusWitness.d)) 20 = true /\
    intEq (det (edgeDA rhombusWitness)
      (sub rhombusWitness.c rhombusWitness.d)) 20 = true /\
    positiveInt (det (edgeAB rhombusWitness)
      (sub rhombusWitness.c rhombusWitness.a)) = true /\
    positiveInt (det (edgeAB rhombusWitness)
      (sub rhombusWitness.d rhombusWitness.a)) = true /\
    positiveInt (det (edgeBC rhombusWitness)
      (sub rhombusWitness.d rhombusWitness.b)) = true /\
    positiveInt (det (edgeBC rhombusWitness)
      (sub rhombusWitness.a rhombusWitness.b)) = true /\
    positiveInt (det (edgeCD rhombusWitness)
      (sub rhombusWitness.a rhombusWitness.c)) = true /\
    positiveInt (det (edgeCD rhombusWitness)
      (sub rhombusWitness.b rhombusWitness.c)) = true /\
    positiveInt (det (edgeDA rhombusWitness)
      (sub rhombusWitness.b rhombusWitness.d)) = true /\
    positiveInt (det (edgeDA rhombusWitness)
      (sub rhombusWitness.c rhombusWitness.d)) = true /\
    intEq (sqLen (edgeAB rhombusWitness)) 25 = true /\
    intEq (sqLen (edgeBC rhombusWitness)) 25 = true /\
    intEq (sqLen (edgeCD rhombusWitness)) 25 = true /\
    intEq (sqLen (edgeDA rhombusWitness)) 25 = true /\
    positiveInt (sqLen (edgeAB rhombusWitness)) = true /\
    intEq (dot (edgeAB rhombusWitness) (edgeBC rhombusWitness)) 15 = true /\
    PairwiseDistinct rhombusWitness /\
    StrictConvexCCW rhombusWitness /\
    Quadrilateral rhombusWitness /\
    EqualSides rhombusWitness /\
    Not (RightAngles rhombusWitness) /\
    Not (Square rhombusWitness) := by
  constructor
  · rfl
  constructor
  · rfl
  constructor
  · rfl
  constructor
  · rfl
  constructor
  · rfl
  constructor
  · rfl
  constructor
  · rfl
  constructor
  · rfl
  constructor
  · rfl
  constructor
  · rfl
  constructor
  · rfl
  constructor
  · rfl
  constructor
  · rfl
  constructor
  · rfl
  constructor
  · rfl
  constructor
  · rfl
  constructor
  · rfl
  constructor
  · rfl
  constructor
  · rfl
  constructor
  · rfl
  constructor
  · rfl
  constructor
  · rfl
  constructor
  · rfl
  constructor
  · rfl
  constructor
  · rfl
  constructor
  · rfl
  constructor
  · rfl
  constructor
  · rfl
  constructor
  · exact rhombusWitness_pairwise
  constructor
  · exact rhombusWitness_strictConvexCCW
  constructor
  · exact rhombusWitness_quadrilateral
  constructor
  · exact rhombusWitness_equalSides
  constructor
  · exact rhombusWitness_notRightAngles
  · exact rhombusWitness_notSquare

/-- Load-bearing, source-shaped refutation: even an ordered simple strictly
convex CCW quadrilateral with positive equal sides need not be a square. -/
theorem refutes_equal_sides_imply_square : Not SourceClaim := by
  intro claimed
  have allegedSquare : Square rhombusWitness :=
    claimed rhombusWitness rhombusWitness_quadrilateral
      rhombusWitness_equalSides
  exact rhombusWitness_notSquare allegedSquare

theorem squareControl_pairwise : PairwiseDistinct squareControl := by
  constructor
  · rfl
  constructor
  · rfl
  constructor
  · rfl
  constructor
  · rfl
  constructor
  · rfl
  · rfl

theorem squareControl_strictConvexCCW : StrictConvexCCW squareControl := by
  constructor
  · rfl
  constructor
  · rfl
  constructor
  · rfl
  constructor
  · rfl
  constructor
  · rfl
  constructor
  · rfl
  constructor
  · rfl
  · rfl

theorem squareControl_quadrilateral : Quadrilateral squareControl := by
  exact And.intro squareControl_pairwise squareControl_strictConvexCCW

theorem squareControl_equalSides : EqualSides squareControl := by
  constructor
  · rfl
  constructor
  · rfl
  constructor
  · rfl
  · rfl

theorem squareControl_rightAngles : RightAngles squareControl := by
  constructor
  · rfl
  constructor
  · rfl
  constructor
  · rfl
  · rfl

theorem squareControl_square : Square squareControl := by
  exact And.intro squareControl_quadrilateral
    (And.intro squareControl_equalSides squareControl_rightAngles)

/-- Meaningful negative control: the axis-aligned control satisfies all six
distinctions, all eight strict left-side tests (each determinant exactly 25),
all positive equal-side tests (each squared length exactly 25), and every
encoded right angle (each dot product exactly zero), so it is genuinely a
square. -/
theorem negative_control_axis_aligned_square :
    pointEq squareControl.a squareControl.b = false /\
    pointEq squareControl.a squareControl.c = false /\
    pointEq squareControl.a squareControl.d = false /\
    pointEq squareControl.b squareControl.c = false /\
    pointEq squareControl.b squareControl.d = false /\
    pointEq squareControl.c squareControl.d = false /\
    intEq (det (edgeAB squareControl)
      (sub squareControl.c squareControl.a)) 25 = true /\
    intEq (det (edgeAB squareControl)
      (sub squareControl.d squareControl.a)) 25 = true /\
    intEq (det (edgeBC squareControl)
      (sub squareControl.d squareControl.b)) 25 = true /\
    intEq (det (edgeBC squareControl)
      (sub squareControl.a squareControl.b)) 25 = true /\
    intEq (det (edgeCD squareControl)
      (sub squareControl.a squareControl.c)) 25 = true /\
    intEq (det (edgeCD squareControl)
      (sub squareControl.b squareControl.c)) 25 = true /\
    intEq (det (edgeDA squareControl)
      (sub squareControl.b squareControl.d)) 25 = true /\
    intEq (det (edgeDA squareControl)
      (sub squareControl.c squareControl.d)) 25 = true /\
    positiveInt (det (edgeAB squareControl)
      (sub squareControl.c squareControl.a)) = true /\
    positiveInt (det (edgeAB squareControl)
      (sub squareControl.d squareControl.a)) = true /\
    positiveInt (det (edgeBC squareControl)
      (sub squareControl.d squareControl.b)) = true /\
    positiveInt (det (edgeBC squareControl)
      (sub squareControl.a squareControl.b)) = true /\
    positiveInt (det (edgeCD squareControl)
      (sub squareControl.a squareControl.c)) = true /\
    positiveInt (det (edgeCD squareControl)
      (sub squareControl.b squareControl.c)) = true /\
    positiveInt (det (edgeDA squareControl)
      (sub squareControl.b squareControl.d)) = true /\
    positiveInt (det (edgeDA squareControl)
      (sub squareControl.c squareControl.d)) = true /\
    intEq (sqLen (edgeAB squareControl)) 25 = true /\
    intEq (sqLen (edgeBC squareControl)) 25 = true /\
    intEq (sqLen (edgeCD squareControl)) 25 = true /\
    intEq (sqLen (edgeDA squareControl)) 25 = true /\
    positiveInt (sqLen (edgeAB squareControl)) = true /\
    intEq (dot (edgeAB squareControl) (edgeBC squareControl)) 0 = true /\
    intEq (dot (edgeBC squareControl) (edgeCD squareControl)) 0 = true /\
    intEq (dot (edgeCD squareControl) (edgeDA squareControl)) 0 = true /\
    intEq (dot (edgeDA squareControl) (edgeAB squareControl)) 0 = true /\
    PairwiseDistinct squareControl /\
    StrictConvexCCW squareControl /\
    Quadrilateral squareControl /\
    EqualSides squareControl /\
    RightAngles squareControl /\
    Square squareControl := by
  constructor
  · rfl
  constructor
  · rfl
  constructor
  · rfl
  constructor
  · rfl
  constructor
  · rfl
  constructor
  · rfl
  constructor
  · rfl
  constructor
  · rfl
  constructor
  · rfl
  constructor
  · rfl
  constructor
  · rfl
  constructor
  · rfl
  constructor
  · rfl
  constructor
  · rfl
  constructor
  · rfl
  constructor
  · rfl
  constructor
  · rfl
  constructor
  · rfl
  constructor
  · rfl
  constructor
  · rfl
  constructor
  · rfl
  constructor
  · rfl
  constructor
  · rfl
  constructor
  · rfl
  constructor
  · rfl
  constructor
  · rfl
  constructor
  · rfl
  constructor
  · rfl
  constructor
  · rfl
  constructor
  · rfl
  constructor
  · rfl
  constructor
  · exact squareControl_pairwise
  constructor
  · exact squareControl_strictConvexCCW
  constructor
  · exact squareControl_quadrilateral
  constructor
  · exact squareControl_equalSides
  constructor
  · exact squareControl_rightAngles
  · exact squareControl_square

end RedditLearnmathEgpgy9
