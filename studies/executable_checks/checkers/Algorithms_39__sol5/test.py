"""If we remove any set of < k edges, the graph remains connected because each vertex still has
at least one remaining edge. This is because: - For any vertex v, if we remove < k edges, at
least one edge incident to v remains (since deg(v) ≥k). - Thus, no vertex becomes isolated,
and the graph remains connected."""

import json
from itertools import combinations, product


RECORD_ID = "Algorithms_39__sol5"
OUTCOME = "WITNESS_FOUND"
WITNESS_DESCRIPTION = (
    "k = 2; vertices {0,1,2,3,4,5}; edges "
    "{(0,1),(0,2),(1,2),(3,4),(3,5),(4,5),(0,3)}; remove {(0,3)}."
)
REFUTATION_EXPLANATION = (
    "Every vertex initially has degree at least 2 (degrees 3,2,2,3,2,2). "
    "Removing 1 < 2 edges leaves degrees 2,2,2,2,2,2, so no vertex is "
    "isolated, but it separates {0,1,2} from {3,4,5}; therefore the "
    "remaining graph is disconnected."
)
SEARCH_SPACE = (
    "All 9 labeled simple undirected graphs formed by triangles on {0,1,2} "
    "and {3,4,5} plus one edge between the triangles, with k=2; for each "
    "graph, all 8 edge-removal sets of size 0 or 1 were checked (72 "
    "graph/removal pairs total)."
)


def degrees(vertices, edges):
    result = {vertex: 0 for vertex in vertices}
    for left, right in edges:
        result[left] += 1
        result[right] += 1
    return tuple(result[vertex] for vertex in vertices)


def is_connected(vertices, edges):
    adjacency = {vertex: [] for vertex in vertices}
    for left, right in edges:
        adjacency[left].append(right)
        adjacency[right].append(left)
    visited = {vertices[0]}
    stack = [vertices[0]]
    while stack:
        current = stack.pop()
        for neighbor in reversed(adjacency[current]):
            if neighbor not in visited:
                visited.add(neighbor)
                stack.append(neighbor)
    return len(visited) == len(vertices)


def main():
    vertices = (0, 1, 2, 3, 4, 5)
    left_triangle = ((0, 1), (0, 2), (1, 2))
    right_triangle = ((3, 4), (3, 5), (4, 5))
    base_edges = left_triangle + right_triangle
    k = 2
    checked = 0
    witness = None

    for cross_edge in product((0, 1, 2), (3, 4, 5)):
        edges = tuple(sorted(base_edges + (cross_edge,)))
        assert is_connected(vertices, edges)
        assert min(degrees(vertices, edges)) >= k

        for removed_count in range(k):
            for removed in combinations(edges, removed_count):
                checked += 1
                remaining = tuple(edge for edge in edges if edge not in removed)
                remaining_degrees = degrees(vertices, remaining)
                if (
                    witness is None
                    and all(degree >= 1 for degree in remaining_degrees)
                    and not is_connected(vertices, remaining)
                ):
                    witness = (cross_edge, edges, removed)

    expected_edges = (
        (0, 1), (0, 2), (0, 3), (1, 2), (3, 4), (3, 5), (4, 5)
    )
    assert checked == 72
    assert witness == ((0, 3), expected_edges, ((0, 3),))

    result = {
        "record_id": RECORD_ID,
        "outcome": OUTCOME,
        "witness_description": WITNESS_DESCRIPTION,
        "refutation_explanation": REFUTATION_EXPLANATION,
        "search_space": SEARCH_SPACE,
    }
    print(json.dumps(result, ensure_ascii=False, separators=(",", ":")))


if __name__ == "__main__":
    main()
