"""If adding/coloring the remaining vertex u creates no cycle, then the resulting connected graph G is a tree and therefore 2-colorable."""

import json
from itertools import combinations

RECORD_ID = "reddit_askmath_pe1euu"
WITNESS_DESCRIPTION = (
    "Let H have vertices 0,1,2 and edges {0-1, 0-2, 1-2}. Add u=3 "
    "with the single edge 0-3. The resulting G is a triangle with a leaf."
)
REFUTATION_EXPLANATION = (
    "Adding u as a leaf creates no cycle containing u, and G is connected. "
    "Nevertheless, the pre-existing 3-cycle remains, so G is not a tree; "
    "that odd cycle also makes G not 2-colorable."
)
SEARCH_SPACE = (
    "All 1,098 labeled simple undirected augmentations obtained by taking "
    "n=1,2,3,4 base vertices, choosing every base-edge subset, and adjoining "
    "distinguished u with every possible neighbor subset (2+8+64+1,024 "
    "cases), in increasing n and bit-mask order."
)


def adjacency(vertex_count, edges):
    adj = [[] for _ in range(vertex_count)]
    for a, b in edges:
        adj[a].append(b)
        adj[b].append(a)
    return adj


def connected(vertex_count, edges):
    adj = adjacency(vertex_count, edges)
    seen = {0}
    stack = [0]
    while stack:
        vertex = stack.pop()
        for neighbor in adj[vertex]:
            if neighbor not in seen:
                seen.add(neighbor)
                stack.append(neighbor)
    return len(seen) == vertex_count


def has_cycle(vertex_count, edges):
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


def two_colorable(vertex_count, edges):
    adj = adjacency(vertex_count, edges)
    colors = [-1] * vertex_count
    for start in range(vertex_count):
        if colors[start] != -1:
            continue
        colors[start] = 0
        stack = [start]
        while stack:
            vertex = stack.pop()
            for neighbor in adj[vertex]:
                if colors[neighbor] == -1:
                    colors[neighbor] = 1 - colors[vertex]
                    stack.append(neighbor)
                elif colors[neighbor] == colors[vertex]:
                    return False
    return True


def path_exists(vertex_count, edges, start, goal):
    adj = adjacency(vertex_count, edges)
    seen = {start}
    stack = [start]
    while stack:
        vertex = stack.pop()
        if vertex == goal:
            return True
        for neighbor in adj[vertex]:
            if neighbor not in seen:
                seen.add(neighbor)
                stack.append(neighbor)
    return False


def adding_u_creates_cycle(base_count, base_edges, neighbor_mask):
    neighbors = [
        vertex for vertex in range(base_count)
        if neighbor_mask & (1 << vertex)
    ]
    for index, first in enumerate(neighbors):
        for second in neighbors[index + 1:]:
            if path_exists(base_count, base_edges, first, second):
                return True
    return False


def main():
    first_witness = None
    tested = 0

    for base_count in range(1, 5):
        possible_base_edges = list(combinations(range(base_count), 2))
        for base_mask in range(1 << len(possible_base_edges)):
            base_edges = [
                edge for bit, edge in enumerate(possible_base_edges)
                if base_mask & (1 << bit)
            ]
            for neighbor_mask in range(1 << base_count):
                tested += 1
                u = base_count
                added_edges = [
                    (vertex, u) for vertex in range(base_count)
                    if neighbor_mask & (1 << vertex)
                ]
                graph_edges = base_edges + added_edges

                if not connected(base_count + 1, graph_edges):
                    continue
                if adding_u_creates_cycle(base_count, base_edges, neighbor_mask):
                    continue

                is_tree = not has_cycle(base_count + 1, graph_edges)
                is_two_colorable = two_colorable(base_count + 1, graph_edges)
                if not is_tree or not is_two_colorable:
                    if first_witness is None:
                        first_witness = (base_count, base_mask, neighbor_mask)

    assert tested == 1098
    assert first_witness == (3, 7, 1)

    result = {
        "record_id": RECORD_ID,
        "outcome": "WITNESS_FOUND",
        "witness_description": WITNESS_DESCRIPTION,
        "refutation_explanation": REFUTATION_EXPLANATION,
        "search_space": SEARCH_SPACE,
    }
    print(json.dumps(result, separators=(",", ":")))


if __name__ == "__main__":
    main()
