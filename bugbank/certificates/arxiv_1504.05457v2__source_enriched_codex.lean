/-!
Record: `arxiv_1504.05457v2__source_enriched_codex`

This certificate addresses the exact frozen source supplied in review input
`R076.json`, lines 128–133 and 170–173. The record identifier is retained for
traceability; it does not independently establish which public source version
contains that text. No inherited reviewer approval is asserted here.

The displayed definition calls the common graphs `G` satisfying
`forall common Gstar, not (G <= Gstar)` the maximal common subgraphs.
Its non-strict exclusion includes `Gstar = G`. The source's dominance relation
requires a bijection between the **full** vertex types, preserving edges and
respecting vertex- and edge-label compatibility. Accordingly, `Embedding`
below requires both injectivity and surjectivity onto `large.Vertex`.
It is not merely a bijection onto an image subset.

The unchanged witness has `G1 = G2 = H`: one vertex, no edges or loops, and
vertex label `a`. The identity bijection witnesses all three needed instances
of dominance. `H` is maximal among graphs common to `H,H`: any alleged strict
common supergraph is already dominated by `H`, contradicting strictness.
Nevertheless, taking `Gstar = H` refutes the displayed non-strict prohibition.
The selected theorem proves this disagreement for the literal full-domain
bijective relation.

A labeled graph is represented by its vertex type, symmetric edge predicate
(loops permitted), vertex labels, and labels for applicable edges. This uses
single-valued labels, which suffice for the concrete witness. Vertex and edge
label types are distinct, and their compatibility relations are explicit and
reflexive. `Subgraph` is retained as the internal name for existence of the
source dominance data; it does not denote arbitrary vertex-subset containment.
`Common`, `Displayed`, `Strict`, and `ActualMaximal` all use this same relation.
The strict repair is a separately labeled local definition, not an attribution
of corrected text to the source.

The negative control uses the same two-vertex type for `K2` and `H2`, with
identical vertex labels. `K2` is edgeless; `H2` has one undirected edge. The
identity **bijection** takes `K2` into `H2`, while no edge-preserving map can
take `H2` into `K2`. Thus `K2` is common but nonmaximal for `H2,H2`, and the
strict repair rejects it while accepting maximal `H`.

This source file has zero imports and uses Lean core definitions and explicit
proofs. Compilation validates those formal statements; source correspondence
still requires the separate semantic review recorded with this proposal.
-/

namespace Arxiv150405457v2SourceEnrichedCodex

structure LabelCompatibility (VertexLabel EdgeLabel : Type) where
  vertex : VertexLabel -> VertexLabel -> Prop
  edge : EdgeLabel -> EdgeLabel -> Prop
  vertex_refl : forall label, vertex label label
  edge_refl : forall label, edge label label

structure LabeledGraph (VertexLabel EdgeLabel : Type) where
  Vertex : Type
  edge : Vertex -> Vertex -> Prop
  edge_symmetric : forall {u v}, edge u v -> edge v u
  vertexLabel : Vertex -> VertexLabel
  edgeLabel : forall {u v}, edge u v -> EdgeLabel

/- Concrete source-dominance data live in `Type`. The vertex map is bijective
between the full vertex types, not just injective into a selected image.
`Subgraph` wraps existence of these data in `Nonempty`. -/
structure Embedding {VertexLabel EdgeLabel : Type}
    (compatibility : LabelCompatibility VertexLabel EdgeLabel)
    (small large : LabeledGraph VertexLabel EdgeLabel) where
  toFun : small.Vertex -> large.Vertex
  injective : forall {u v}, toFun u = toFun v -> u = v
  surjective : forall v : large.Vertex, Exists fun u : small.Vertex => toFun u = v
  preservesEdge : forall {u v}, small.edge u v ->
    large.edge (toFun u) (toFun v)
  preservesVertexLabel : forall u,
    compatibility.vertex (small.vertexLabel u) (large.vertexLabel (toFun u))
  preservesEdgeLabel : forall {u v} (h : small.edge u v),
    compatibility.edge (small.edgeLabel h)
      (large.edgeLabel (preservesEdge h))

def Subgraph {VertexLabel EdgeLabel : Type}
    (compatibility : LabelCompatibility VertexLabel EdgeLabel)
    (small large : LabeledGraph VertexLabel EdgeLabel) : Prop :=
  Nonempty (Embedding compatibility small large)

def identityEmbedding {VertexLabel EdgeLabel : Type}
    (compatibility : LabelCompatibility VertexLabel EdgeLabel)
    (G : LabeledGraph VertexLabel EdgeLabel) :
    Embedding compatibility G G where
  toFun := fun v => v
  injective := fun h => h
  surjective := fun v => Exists.intro v rfl
  preservesEdge := fun h => h
  preservesVertexLabel := fun v => compatibility.vertex_refl (G.vertexLabel v)
  preservesEdgeLabel := fun h => compatibility.edge_refl (G.edgeLabel h)

theorem subgraph_reflexive {VertexLabel EdgeLabel : Type}
    (compatibility : LabelCompatibility VertexLabel EdgeLabel)
    (G : LabeledGraph VertexLabel EdgeLabel) :
    Subgraph compatibility G G :=
  Nonempty.intro (identityEmbedding compatibility G)

def Common {VertexLabel EdgeLabel : Type}
    (compatibility : LabelCompatibility VertexLabel EdgeLabel)
    (G G1 G2 : LabeledGraph VertexLabel EdgeLabel) : Prop :=
  Subgraph compatibility G G1 /\ Subgraph compatibility G G2

/- This is the source's displayed non-strict condition: `Gstar not≥ G` is
represented by `not (G ≤ Gstar)`, while `Gstar` ranges over every common
subgraph, including `G` itself. -/
def Displayed {VertexLabel EdgeLabel : Type}
    (compatibility : LabelCompatibility VertexLabel EdgeLabel)
    (G G1 G2 : LabeledGraph VertexLabel EdgeLabel) : Prop :=
  Common compatibility G G1 G2 /\
  forall Gstar, Common compatibility Gstar G1 G2 ->
    Not (Subgraph compatibility G Gstar)

def Strict {VertexLabel EdgeLabel : Type}
    (compatibility : LabelCompatibility VertexLabel EdgeLabel)
    (G Gstar : LabeledGraph VertexLabel EdgeLabel) : Prop :=
  Subgraph compatibility G Gstar /\
  Not (Subgraph compatibility Gstar G)

def ActualMaximal {VertexLabel EdgeLabel : Type}
    (compatibility : LabelCompatibility VertexLabel EdgeLabel)
    (G G1 G2 : LabeledGraph VertexLabel EdgeLabel) : Prop :=
  Common compatibility G G1 G2 /\
  Not (Exists fun Gstar =>
    Common compatibility Gstar G1 G2 /\
    Strict compatibility G Gstar)

def Repaired {VertexLabel EdgeLabel : Type}
    (compatibility : LabelCompatibility VertexLabel EdgeLabel)
    (G G1 G2 : LabeledGraph VertexLabel EdgeLabel) : Prop :=
  Common compatibility G G1 G2 /\
  forall Gstar, Common compatibility Gstar G1 G2 ->
    Not (Strict compatibility G Gstar)

def ClaimedIntersectionCorrect {VertexLabel EdgeLabel : Type}
    (compatibility : LabelCompatibility VertexLabel EdgeLabel)
    (G1 G2 : LabeledGraph VertexLabel EdgeLabel) : Prop :=
  forall G, Displayed compatibility G G1 G2 <->
    ActualMaximal compatibility G G1 G2

/- Self-instantiation refutes the literal universal condition under the
full-domain bijective dominance relation defined above. -/
theorem displayed_rejects_every_common {VertexLabel EdgeLabel : Type}
    (compatibility : LabelCompatibility VertexLabel EdgeLabel)
    (G G1 G2 : LabeledGraph VertexLabel EdgeLabel)
    (common : Common compatibility G G1 G2) :
    Not (Displayed compatibility G G1 G2) := by
  intro displayed
  exact displayed.2 G common (subgraph_reflexive compatibility G)

inductive VertexLabel where
  | a
  deriving DecidableEq, BEq

inductive EdgeLabel where
  | link
  deriving DecidableEq, BEq

def vertexLabelCompatible (x y : VertexLabel) : Prop := x = y
def edgeLabelCompatible (x y : EdgeLabel) : Prop := x = y

def labelCompatibility : LabelCompatibility VertexLabel EdgeLabel where
  vertex := vertexLabelCompatible
  edge := edgeLabelCompatible
  vertex_refl := fun _ => rfl
  edge_refl := fun _ => rfl

inductive OneVertex where
  | v
  deriving DecidableEq, BEq

def H : LabeledGraph VertexLabel EdgeLabel where
  Vertex := OneVertex
  edge := fun _ _ => False
  edge_symmetric := fun h => False.elim h
  vertexLabel := fun _ => .a
  edgeLabel := fun h => False.elim h

def H_le_H : Subgraph labelCompatibility H H :=
  Nonempty.intro (identityEmbedding labelCompatibility H)

def H_common : Common labelCompatibility H H H :=
  And.intro H_le_H H_le_H

theorem H_actual_maximal : ActualMaximal labelCompatibility H H H := by
  refine And.intro H_common ?_
  intro larger
  exact Exists.elim larger (fun _ facts => facts.2.2 facts.1.1)

theorem H_repaired : Repaired labelCompatibility H H H := by
  refine And.intro H_common ?_
  intro Gstar common strict
  exact strict.2 common.1

theorem H_not_displayed : Not (Displayed labelCompatibility H H H) :=
  displayed_rejects_every_common labelCompatibility H H H H_common

/- Load-bearing refutation: all concrete graph, label, containment,
reflexivity, commonness, maximality, literal-predicate failure, repaired
behavior, and extensional disagreement facts occur in the conclusion. -/
theorem refutes_displayed_graph_intersection :
    Not (H.edge .v .v) /\
    H.vertexLabel .v = .a /\
    vertexLabelCompatible .a .a /\
    Subgraph labelCompatibility H H /\
    Common labelCompatibility H H H /\
    ActualMaximal labelCompatibility H H H /\
    Not (Displayed labelCompatibility H H H) /\
    Repaired labelCompatibility H H H /\
    (Exists fun G =>
      ActualMaximal labelCompatibility G H H /\
      Not (Displayed labelCompatibility G H H)) /\
    Not (ClaimedIntersectionCorrect labelCompatibility H H) := by
  constructor
  · intro edge
    exact edge
  constructor
  · rfl
  constructor
  · rfl
  constructor
  · exact H_le_H
  constructor
  · exact H_common
  constructor
  · exact H_actual_maximal
  constructor
  · exact H_not_displayed
  constructor
  · exact H_repaired
  constructor
  · exact Exists.intro H (And.intro H_actual_maximal H_not_displayed)
  · intro claimed
    exact H_not_displayed ((claimed H).mpr H_actual_maximal)

inductive TwoVertex where
  | left | right
  deriving DecidableEq, BEq

def H2Edge : TwoVertex -> TwoVertex -> Prop
  | .left, .right => True
  | .right, .left => True
  | _, _ => False

def H2Edge_symmetric {u v : TwoVertex} : H2Edge u v -> H2Edge v u := by
  cases u <;> cases v <;> intro edge
  · exact False.elim edge
  · exact True.intro
  · exact True.intro
  · exact False.elim edge

def H2 : LabeledGraph VertexLabel EdgeLabel where
  Vertex := TwoVertex
  edge := H2Edge
  edge_symmetric := H2Edge_symmetric
  vertexLabel := fun _ => .a
  edgeLabel := fun _ => .link

def K2 : LabeledGraph VertexLabel EdgeLabel where
  Vertex := TwoVertex
  edge := fun _ _ => False
  edge_symmetric := fun h => False.elim h
  vertexLabel := fun _ => .a
  edgeLabel := fun h => False.elim h

def K2_embedding_H2 : Embedding labelCompatibility K2 H2 where
  toFun := fun v => v
  injective := fun h => h
  surjective := fun v => Exists.intro v rfl
  preservesEdge := fun h => False.elim h
  preservesVertexLabel := fun _ => rfl
  preservesEdgeLabel := fun h => False.elim h

def K2_le_H2 : Subgraph labelCompatibility K2 H2 :=
  Nonempty.intro K2_embedding_H2

theorem H2_not_le_K2 : Not (Subgraph labelCompatibility H2 K2) := by
  intro containment
  apply Nonempty.elim containment
  intro embedding
  have sourceEdge : H2.edge .left .right := True.intro
  exact embedding.preservesEdge sourceEdge

def H2_common : Common labelCompatibility H2 H2 H2 :=
  And.intro (subgraph_reflexive labelCompatibility H2)
    (subgraph_reflexive labelCompatibility H2)

def K2_common : Common labelCompatibility K2 H2 H2 :=
  And.intro K2_le_H2 K2_le_H2

def K2_strict_H2 : Strict labelCompatibility K2 H2 :=
  And.intro K2_le_H2 H2_not_le_K2

theorem K2_not_actual_maximal :
    Not (ActualMaximal labelCompatibility K2 H2 H2) := by
  intro maximal
  apply maximal.2
  exact Exists.intro H2 (And.intro H2_common K2_strict_H2)

theorem K2_not_displayed_via_H2 :
    Not (Displayed labelCompatibility K2 H2 H2) := by
  intro displayed
  exact displayed.2 H2 H2_common K2_le_H2

theorem K2_not_repaired : Not (Repaired labelCompatibility K2 H2 H2) := by
  intro repaired
  exact repaired.2 H2 H2_common K2_strict_H2

/- Meaningful changed-feature negative control: adding precisely the one
undirected edge changes `K2` into its strict common supergraph `H2`.  Thus the
edgeless candidate is genuinely nonmaximal; both the literal predicate and
the strict repaired predicate reject it, for the intended structural reason. -/
theorem negative_control_edge_deletion_is_nonmaximal_and_repair_rejects :
    Not (K2.edge .left .right) /\
    H2.edge .left .right /\
    H2.edge .right .left /\
    Not (H2.edge .left .left) /\
    Not (H2.edge .right .right) /\
    K2.vertexLabel .left = H2.vertexLabel .left /\
    K2.vertexLabel .right = H2.vertexLabel .right /\
    Subgraph labelCompatibility K2 H2 /\
    Not (Subgraph labelCompatibility H2 K2) /\
    Strict labelCompatibility K2 H2 /\
    Common labelCompatibility K2 H2 H2 /\
    Not (ActualMaximal labelCompatibility K2 H2 H2) /\
    Not (Displayed labelCompatibility K2 H2 H2) /\
    Not (Repaired labelCompatibility K2 H2 H2) /\
    Repaired labelCompatibility H H H := by
  constructor
  · intro edge
    exact edge
  constructor
  · exact True.intro
  constructor
  · exact True.intro
  constructor
  · intro edge
    exact edge
  constructor
  · intro edge
    exact edge
  constructor
  · rfl
  constructor
  · rfl
  constructor
  · exact K2_le_H2
  constructor
  · exact H2_not_le_K2
  constructor
  · exact K2_strict_H2
  constructor
  · exact K2_common
  constructor
  · exact K2_not_actual_maximal
  constructor
  · exact K2_not_displayed_via_H2
  constructor
  · exact K2_not_repaired
  · exact H_repaired

end Arxiv150405457v2SourceEnrichedCodex
