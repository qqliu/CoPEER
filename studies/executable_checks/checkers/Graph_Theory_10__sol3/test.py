"""A planar graph is outerplanar if and only if its dual is a forest. Since G is not outerplanar, Gcontains a cycle C."""

import json
from itertools import combinations

REPORT = {
    "record_id": "Graph Theory_10__sol3",
    "outcome": "WITNESS_FOUND",
    "witness_description": "Witness: V={0,1,2,3}, E={01,12,23,30,02}, embedded as a square with diagonal 02. Every vertex is on the outer face, so the graph is outerplanar. Its dual has the outer face O and triangular faces A=012, B=023; dual edges include O-A, A-B, and B-O, a 3-cycle, so the dual is not a forest.",
    "refutation_explanation": "The claimed forward implication from outerplanarity to having a forest dual fails on the witness. This does not rely on treating parallel dual edges as cycles: after parallel dual edges are collapsed, O, A, and B still form a triangle. Hence the stated biconditional is false.",
    "search_space": "Exactly two candidates were swept in fixed order: the plane 4-cycle with edges 01,12,23,30 in the integer-coordinate square embedding, first without a diagonal and then with diagonal 02. The first has no cycle in its simplified dual; the second is the reported witness. For each candidate, every disjoint edge pair and every edge-to-face incidence was checked exactly."
}

VERTICES = (0, 1, 2, 3)
POSITIONS = ((0, 0), (2, 0), (2, 2), (0, 2))
BOUNDARY = frozenset(((0, 1), (1, 2), (2, 3), (0, 3)))
DIAGONAL = (0, 2)
CANDIDATE_MASKS = (0, 1)


def orient(a, b, c):
    return ((b[0] - a[0]) * (c[1] - a[1])
            - (b[1] - a[1]) * (c[0] - a[0]))


def properly_cross(edge_a, edge_b):
    if set(edge_a) & set(edge_b):
        return False
    a, b = (POSITIONS[edge_a[0]], POSITIONS[edge_a[1]])
    c, d = (POSITIONS[edge_b[0]], POSITIONS[edge_b[1]])
    return (orient(a, b, c) * orient(a, b, d) < 0
            and orient(c, d, a) * orient(c, d, b) < 0)


def faces_for(mask):
    outer = BOUNDARY
    if mask == 0:
        return (outer, BOUNDARY)
    assert mask == 1
    triangle_012 = frozenset(((0, 1), (1, 2), (0, 2)))
    triangle_023 = frozenset(((0, 2), (2, 3), (0, 3)))
    return (outer, triangle_012, triangle_023)


def dual_simple_edges(edges, faces):
    result = set()
    for primal_edge in sorted(edges):
        incident = tuple(
            face_index
            for face_index, face_edges in enumerate(faces)
            if primal_edge in face_edges
        )
        assert len(incident) == 2
        assert incident[0] != incident[1]
        result.add(incident)
    return tuple(sorted(result))


def contains_cycle(vertex_count, edges):
    parent = list(range(vertex_count))

    def find(vertex):
        while parent[vertex] != vertex:
            parent[vertex] = parent[parent[vertex]]
            vertex = parent[vertex]
        return vertex

    for a, b in edges:
        root_a = find(a)
        root_b = find(b)
        if root_a == root_b:
            return True
        parent[root_b] = root_a
    return False


checked_masks = []
found = None
for diagonal_mask in CANDIDATE_MASKS:
    checked_masks.append(diagonal_mask)
    edges = set(BOUNDARY)
    if diagonal_mask == 1:
        edges.add(DIAGONAL)

    for edge_a, edge_b in combinations(sorted(edges), 2):
        assert not properly_cross(edge_a, edge_b)

    faces = faces_for(diagonal_mask)
    outer_vertices = set()
    for a, b in faces[0]:
        outer_vertices.add(a)
        outer_vertices.add(b)
    assert outer_vertices == set(VERTICES)
    assert len(faces) == 2 - len(VERTICES) + len(edges)

    dual_edges = dual_simple_edges(edges, faces)
    if contains_cycle(len(faces), dual_edges):
        found = (
            diagonal_mask,
            tuple(sorted(edges)),
            dual_edges,
            faces,
        )
        break

assert tuple(checked_masks) == CANDIDATE_MASKS
assert found is not None
assert found[0] == 1
assert found[1] == ((0, 1), (0, 2), (0, 3), (1, 2), (2, 3))
assert found[2] == ((0, 1), (0, 2), (1, 2))
assert found[3][0] == BOUNDARY
assert found[3][1] == frozenset(((0, 1), (1, 2), (0, 2)))
assert found[3][2] == frozenset(((0, 2), (2, 3), (0, 3)))
assert REPORT["record_id"] == "Graph Theory_10__sol3"
assert REPORT["outcome"] == "WITNESS_FOUND"

print(json.dumps(REPORT, sort_keys=False, separators=(",", ":")))
