"""Every chordal graph can be obtained via clique pasting from two chordal graphs whose vertex sets are both proper subsets of its vertex set."""

import json
from itertools import combinations, permutations

RECORD_ID = "arxiv_1311.5863v2__source_enriched_codex"
OUTCOME = "WITNESS_FOUND"
WITNESS_DESCRIPTION = "The complete graph K2 on V={0,1}, with edge set {{0,1}}."
REFUTATION_EXPLANATION = "K2 is chordal because it has no cycle of length at least 4. To cover V with two proper vertex subsets, the only ordered possibilities are ({0},{1}) and ({1},{0}); neither one-vertex graph contains the edge {0,1}. Clique pasting takes the union of the pasted graphs' edges, so it cannot produce K2."
SEARCH_SPACE = "All 2 labeled simple undirected graphs on V={0,1} (the 2 choices for edge {0,1}); for each graph, all 9 ordered pairs (A,B) of proper subsets of V, for 18 clique-pasting tests total."


def normalized_edge(u, v):
    return (u, v) if u < v else (v, u)


def induced_edges(vertex_subset, edges):
    return frozenset(
        edge for edge in edges
        if edge[0] in vertex_subset and edge[1] in vertex_subset
    )


def is_chordal(vertices, edges):
    vertex_tuple = tuple(sorted(vertices))
    for cycle_length in range(4, len(vertex_tuple) + 1):
        for chosen in combinations(vertex_tuple, cycle_length):
            for cycle in permutations(chosen):
                if cycle[0] != min(chosen):
                    continue
                consecutive = frozenset(
                    normalized_edge(cycle[index], cycle[(index + 1) % cycle_length])
                    for index in range(cycle_length)
                )
                if not consecutive.issubset(edges):
                    continue
                all_pairs = frozenset(
                    normalized_edge(u, v) for u, v in combinations(chosen, 2)
                )
                if edges.intersection(all_pairs) == consecutive:
                    return False
    return True


def is_clique(vertices, edges):
    return all(normalized_edge(u, v) in edges for u, v in combinations(sorted(vertices), 2))


def is_clique_pasting(vertices, edges, left_vertices, right_vertices):
    if left_vertices == vertices or right_vertices == vertices:
        return False
    if left_vertices.union(right_vertices) != vertices:
        return False
    overlap = left_vertices.intersection(right_vertices)
    if not is_clique(overlap, edges):
        return False
    left_edges = induced_edges(left_vertices, edges)
    right_edges = induced_edges(right_vertices, edges)
    if not is_chordal(left_vertices, left_edges):
        return False
    if not is_chordal(right_vertices, right_edges):
        return False
    return left_edges.union(right_edges) == edges


def main():
    vertices = frozenset((0, 1))
    possible_edges = ((0, 1),)
    proper_subsets = tuple(
        frozenset(v for v in sorted(vertices) if subset_mask & (1 << v))
        for subset_mask in range(1 << len(vertices))
        if subset_mask != (1 << len(vertices)) - 1
    )

    counterexamples = []
    tested_pairs = 0
    for edge_mask in range(1 << len(possible_edges)):
        edges = frozenset(
            possible_edges[index]
            for index in range(len(possible_edges))
            if edge_mask & (1 << index)
        )
        decompositions = []
        for left_vertices in proper_subsets:
            for right_vertices in proper_subsets:
                tested_pairs += 1
                if is_clique_pasting(vertices, edges, left_vertices, right_vertices):
                    decompositions.append((left_vertices, right_vertices))
        if is_chordal(vertices, edges) and not decompositions:
            counterexamples.append(edges)

    assert tested_pairs == 18
    assert frozenset(((0, 1),)) in counterexamples

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
