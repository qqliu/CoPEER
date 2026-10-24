"""Every pair of distinct vertices in a bridgeless graph has two internally disjoint paths between them.

Exhaustively check every vertex pair in one explicitly specified finite graph.
"""

import json
from itertools import combinations

RECORD_ID = "arxiv_1201.5203v4__source_enriched_codex"
OUTCOME = "WITNESS_FOUND"
WITNESS_DESCRIPTION = (
    "The connected graph with vertices {0,1,2,3,4} and edges "
    "{0-1,1-2,0-2,0-3,3-4,0-4}, with the distinct vertices 1 and 3."
)
REFUTATION_EXPLANATION = (
    "Every edge lies on one of the triangles 0-1-2-0 or 0-3-4-0, so deleting "
    "any edge does not increase the number of connected components; hence no edge "
    "is a bridge. Removing vertex 0 separates 1 from 3, so every path from 1 to 3 "
    "contains 0 as an internal vertex. Consequently, no two such paths are "
    "internally disjoint."
)
SEARCH_SPACE = (
    "The single labeled loopless simple undirected graph V={0,1,2,3,4}, "
    "E={{0,1},{1,2},{0,2},{0,3},{3,4},{0,4}}, with all 10 unordered pairs "
    "of distinct vertices checked in lexicographic order; every simple path for "
    "each pair was enumerated."
)

VERTICES = tuple(range(5))
EDGES = (
    (0, 1),
    (0, 2),
    (0, 3),
    (0, 4),
    (1, 2),
    (3, 4),
)


def adjacency(edges):
    neighbors = [[] for _ in VERTICES]
    for left, right in edges:
        neighbors[left].append(right)
        neighbors[right].append(left)
    return tuple(tuple(sorted(items)) for items in neighbors)


def component_count(edges):
    neighbors = adjacency(edges)
    unseen = set(VERTICES)
    count = 0
    while unseen:
        count += 1
        start = min(unseen)
        unseen.remove(start)
        stack = [start]
        while stack:
            current = stack.pop()
            for neighbor in neighbors[current]:
                if neighbor in unseen:
                    unseen.remove(neighbor)
                    stack.append(neighbor)
    return count


def is_bridgeless(edges):
    baseline = component_count(edges)
    for edge in edges:
        reduced = tuple(candidate for candidate in edges if candidate != edge)
        if component_count(reduced) > baseline:
            return False
    return True


def all_simple_paths(edges, start, goal):
    neighbors = adjacency(edges)
    paths = []

    def visit(current, path, used):
        if current == goal:
            paths.append(tuple(path))
            return
        for neighbor in neighbors[current]:
            if neighbor not in used:
                used.add(neighbor)
                path.append(neighbor)
                visit(neighbor, path, used)
                path.pop()
                used.remove(neighbor)

    visit(start, [start], {start})
    return tuple(paths)


def has_two_internally_disjoint_paths(edges, start, goal):
    paths = all_simple_paths(edges, start, goal)
    for first, second in combinations(paths, 2):
        if set(first[1:-1]).isdisjoint(second[1:-1]):
            return True
    return False


def main():
    assert component_count(EDGES) == 1
    assert is_bridgeless(EDGES)

    violating_pairs = []
    checked_pairs = 0
    for start, goal in combinations(VERTICES, 2):
        checked_pairs += 1
        if not has_two_internally_disjoint_paths(EDGES, start, goal):
            violating_pairs.append((start, goal))

    assert checked_pairs == 10
    assert violating_pairs == [(1, 3), (1, 4), (2, 3), (2, 4)]

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
