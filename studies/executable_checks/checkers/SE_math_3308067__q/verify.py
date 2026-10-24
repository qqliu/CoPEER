r"""**Base case**: Let $V(G)=\{v_1,v_2\}$, then the most edges the graph can have is $\frac{2(2-1)}{2}=1$, so this means $E(G)=\{v_1 v_2\}$, and $deg.v_1 = deg.v_2=1$"""

import json

record_id = "SE_math_3308067__q"
notes = (
    "Exact recomputation confirms that the empty simple undirected graph on the "
    "two vertices has no edges and both degrees equal to 0, contradicting the "
    "claimed conclusion. The refuted statement is a substantive logical error, "
    "not a typo."
)

vertices = ("v1", "v2")
vertex_set = frozenset(vertices)
possible_edges = frozenset(
    frozenset((vertices[left], vertices[right]))
    for left in range(len(vertices))
    for right in range(left + 1, len(vertices))
)
witness_edges = frozenset()

def is_simple_graph(edge_set):
    return all(
        len(edge) == 2 and edge <= vertex_set
        for edge in edge_set
    )

degrees = {
    vertex: sum(1 for edge in witness_edges if vertex in edge)
    for vertex in vertices
}
maximum_edge_count = len(vertices) * (len(vertices) - 1) // 2
maximum_is_one = len(possible_edges) == maximum_edge_count and maximum_edge_count == 1
witness_is_valid = is_simple_graph(witness_edges) and witness_edges <= possible_edges
claimed_conclusion = (
    witness_edges == possible_edges
    and degrees["v1"] == 1
    and degrees["v2"] == 1
)
refutes_claim = (
    maximum_is_one
    and witness_is_valid
    and len(witness_edges) <= maximum_edge_count
    and degrees["v1"] == 0
    and degrees["v2"] == 0
    and not claimed_conclusion
)

if not refutes_claim:
    raise AssertionError("independent exact recomputation did not validate the witness")

print(json.dumps({
    "record_id": record_id,
    "verdict": "CONFIRMED",
    "notes": notes,
}, separators=(",", ":")))
