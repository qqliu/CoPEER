"""If we remove any set of < k edges, the graph remains connected because each vertex still has
at least one remaining edge. This is because: - For any vertex v, if we remove < k edges, at
least one edge incident to v remains (since deg(v) ≥k). - Thus, no vertex becomes isolated,
and the graph remains connected."""

import json

RECORD_ID = "Algorithms_39__sol5"
CONFIRMED_NOTES = (
    "Exact recomputation confirms the witness: the original simple graph is "
    "connected and has minimum degree 2; removing the single edge (0,3), with "
    "1 < 2, leaves every vertex at degree 2 but produces two disconnected "
    "components. The refuted statement is substantive, not a typo: having no "
    "isolated vertices does not imply connectivity."
)


def component(start, vertices, edges):
    reached = {start}
    frontier = [start]
    while frontier:
        vertex = frontier.pop()
        for edge in edges:
            if edge[0] == vertex:
                neighbor = edge[1]
            elif edge[1] == vertex:
                neighbor = edge[0]
            else:
                continue
            if neighbor in vertices and neighbor not in reached:
                reached.add(neighbor)
                frontier.append(neighbor)
    return reached


def degree(vertex, edges):
    return sum(1 for edge in edges if vertex in edge)


def main():
    k = 2
    vertices = frozenset({0, 1, 2, 3, 4, 5})
    edges = frozenset({
        (0, 1), (0, 2), (1, 2),
        (3, 4), (3, 5), (4, 5),
        (0, 3),
    })
    removed = frozenset({(0, 3)})
    remaining = edges - removed

    simple_graph = all(
        left in vertices and right in vertices and left != right
        for left, right in edges
    )
    original_connected = component(0, vertices, edges) == vertices
    minimum_degree_condition = all(degree(v, edges) >= k for v in vertices)
    removal_bound = len(removed) < k and removed <= edges
    nobody_isolated = all(degree(v, remaining) >= 1 for v in vertices)
    remaining_degrees = tuple(degree(v, remaining) for v in sorted(vertices))
    left_component = component(0, vertices, remaining)
    remaining_disconnected = left_component != vertices
    exact_separation = left_component == {0, 1, 2}

    established = all((
        simple_graph,
        original_connected,
        minimum_degree_condition,
        removal_bound,
        nobody_isolated,
        remaining_degrees == (2, 2, 2, 2, 2, 2),
        remaining_disconnected,
        exact_separation,
    ))
    if not established:
        raise AssertionError("independent exact verification failed")

    print(json.dumps({
        "record_id": RECORD_ID,
        "verdict": "CONFIRMED",
        "notes": CONFIRMED_NOTES,
    }, separators=(",", ":")))


if __name__ == "__main__":
    main()
