"""In a circuit-free graph, every walk between two vertices is a path."""

import json

record_id = "reddit_askmath_1tgrwlt"
notes = (
    "Exact recomputation confirms the witness: the one-edge simple graph is "
    "circuit-free, while (0,1,0,1) is a walk with distinct endpoints that "
    "repeats vertices and its sole edge, so it is not a path. The refuted "
    "statement is substantive, not plainly a typo; it confuses an arbitrary "
    "walk with a path."
)

vertices = frozenset((0, 1))
edges = frozenset((frozenset((0, 1)),))
walk = (0, 1, 0, 1)

assert len(vertices) == 2
assert len(edges) == 1
assert all(len(edge) == 2 and edge <= vertices for edge in edges)

parent = {vertex: vertex for vertex in vertices}


def root(vertex):
    while parent[vertex] != vertex:
        vertex = parent[vertex]
    return vertex


has_circuit = False
for edge in edges:
    a, b = tuple(edge)
    a_root = root(a)
    b_root = root(b)
    if a_root == b_root:
        has_circuit = True
        break
    parent[a_root] = b_root

assert not has_circuit
assert walk[0] != walk[-1]
assert all(
    frozenset((walk[index], walk[index + 1])) in edges
    for index in range(len(walk) - 1)
)
traversed = tuple(
    frozenset((walk[index], walk[index + 1]))
    for index in range(len(walk) - 1)
)
assert len(frozenset(walk)) < len(walk)
assert len(frozenset(traversed)) < len(traversed)

result = {
    "record_id": record_id,
    "verdict": "CONFIRMED",
    "notes": notes,
}
print(json.dumps(result, separators=(",", ":")))
