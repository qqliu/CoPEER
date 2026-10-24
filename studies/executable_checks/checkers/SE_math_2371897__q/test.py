"""Let $G$ be a triangle free graph. Then center of  $G$ has atmost two vertices."""

import itertools
import json

RECORD_ID = "SE_math_2371897__q"
OUTCOME = "WITNESS_FOUND"
WITNESS_DESCRIPTION = (
    "The graph with vertices {0,1,2,3} and edges "
    "{(0,2),(0,3),(1,2),(1,3)} is a 4-cycle."
)
REFUTATION_EXPLANATION = (
    "This graph is triangle-free. Every vertex has eccentricity 2, so its "
    "center is {0,1,2,3}, which has four vertices and therefore violates "
    "the claimed upper bound of two."
)
SEARCH_SPACE = (
    "All 64 labeled simple undirected graphs on vertex set {0,1,2,3} "
    "(all subsets of the 6 possible edges) were swept in increasing "
    "edge-mask order; connectedness, triangle-freeness, eccentricities, "
    "and centers were checked exactly."
)

VERTICES = tuple(range(4))
POSSIBLE_EDGES = tuple(itertools.combinations(VERTICES, 2))


def adjacency_from_mask(mask):
    adjacency = {vertex: set() for vertex in VERTICES}
    edges = []
    for bit, edge in enumerate(POSSIBLE_EDGES):
        if mask & (1 << bit):
            left, right = edge
            adjacency[left].add(right)
            adjacency[right].add(left)
            edges.append(edge)
    return adjacency, tuple(edges)


def distances_from(start, adjacency):
    distances = {start: 0}
    queue = [start]
    index = 0
    while index < len(queue):
        vertex = queue[index]
        index += 1
        for neighbor in sorted(adjacency[vertex]):
            if neighbor not in distances:
                distances[neighbor] = distances[vertex] + 1
                queue.append(neighbor)
    return distances


def is_connected(adjacency):
    return len(distances_from(0, adjacency)) == len(VERTICES)


def is_triangle_free(adjacency):
    for triple in itertools.combinations(VERTICES, 3):
        first, second, third = triple
        if (second in adjacency[first] and
                third in adjacency[first] and
                third in adjacency[second]):
            return False
    return True


def graph_center(adjacency):
    eccentricities = {}
    for vertex in VERTICES:
        distances = distances_from(vertex, adjacency)
        if len(distances) != len(VERTICES):
            return ()
        eccentricities[vertex] = max(distances.values())
    radius = min(eccentricities.values())
    return tuple(
        vertex for vertex in VERTICES
        if eccentricities[vertex] == radius
    )


def main():
    violations = []
    for mask in range(1 << len(POSSIBLE_EDGES)):
        adjacency, edges = adjacency_from_mask(mask)
        if is_connected(adjacency) and is_triangle_free(adjacency):
            center = graph_center(adjacency)
            if len(center) > 2:
                violations.append((mask, edges, center))

    expected_edges = ((0, 2), (0, 3), (1, 2), (1, 3))
    assert violations[0] == (30, expected_edges, (0, 1, 2, 3))

    result = {
        "record_id": RECORD_ID,
        "outcome": OUTCOME,
        "witness_description": WITNESS_DESCRIPTION,
        "refutation_explanation": REFUTATION_EXPLANATION,
        "search_space": SEARCH_SPACE,
    }
    print(json.dumps(result, separators=(",", ":")))


if __name__ == "__main__":
    main()
