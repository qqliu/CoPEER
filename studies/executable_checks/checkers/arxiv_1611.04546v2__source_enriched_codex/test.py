"""Every triangle-free planar graph of n vertices contains an induced forest of size at least 5n/9 + 20/27."""

import json
from fractions import Fraction
from itertools import combinations

RECORD_ID = "arxiv_1611.04546v2__source_enriched_codex"
WITNESS_DESCRIPTION = (
    "The one-vertex edgeless graph. It is triangle-free and planar, and its "
    "largest induced forest has size 1."
)
REFUTATION_EXPLANATION = (
    "For n = 1, the claimed lower bound is 5/9 + 20/27 = 35/27. Every "
    "induced forest has size at most 1, and 1 < 35/27, so this graph has no "
    "induced forest meeting the claimed bound."
)
SEARCH_SPACE = (
    "All labeled simple undirected graphs on the vertex set {0}: exactly 1 "
    "graph (the edgeless graph), together with all 2 vertex subsets used to "
    "compute its maximum induced-forest size."
)


def is_triangle_free(vertices, edges):
    edge_set = set(edges)
    for a, b, c in combinations(vertices, 3):
        if ((a, b) in edge_set and (a, c) in edge_set
                and (b, c) in edge_set):
            return False
    return True


def is_planar_in_search_space(vertices, edges):
    # The bounded space has one vertex and no possible edges; its sole graph
    # has an immediate plane drawing consisting of one point.
    return vertices == (0,) and not edges


def induced_subgraph_is_forest(subset, edges):
    chosen = set(subset)
    parent = {vertex: vertex for vertex in subset}

    def find(vertex):
        while parent[vertex] != vertex:
            parent[vertex] = parent[parent[vertex]]
            vertex = parent[vertex]
        return vertex

    for left, right in edges:
        if left not in chosen or right not in chosen:
            continue
        left_root = find(left)
        right_root = find(right)
        if left_root == right_root:
            return False
        parent[left_root] = right_root
    return True


def maximum_induced_forest_size(vertices, edges):
    maximum = 0
    for subset_size in range(len(vertices) + 1):
        for subset in combinations(vertices, subset_size):
            if induced_subgraph_is_forest(subset, edges):
                maximum = max(maximum, subset_size)
    return maximum


def main():
    vertices = (0,)
    possible_edges = tuple(combinations(vertices, 2))
    witness = None

    for edge_mask in range(1 << len(possible_edges)):
        edges = tuple(
            edge for index, edge in enumerate(possible_edges)
            if edge_mask & (1 << index)
        )
        if not is_triangle_free(vertices, edges):
            continue
        if not is_planar_in_search_space(vertices, edges):
            continue
        forest_size = maximum_induced_forest_size(vertices, edges)
        lower_bound = Fraction(5 * len(vertices), 9) + Fraction(20, 27)
        if Fraction(forest_size, 1) < lower_bound:
            witness = (vertices, edges, forest_size, lower_bound)
            break

    if witness is None:
        raise AssertionError("The exhaustive bounded search found no witness")

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
