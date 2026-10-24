"""A bijection between the edge sets of two graphs with equally sized vertex sets implies that the graphs are isomorphic."""

import itertools
import json

RECORD_ID = "reddit_learnmath_o65dcu"
OUTCOME = "WITNESS_FOUND"
WITNESS_DESCRIPTION = "On the common vertex set {0,1,2,3}, let G have edges {(0,1),(0,2)} and H have edges {(0,3),(1,2)}. A bijection sends (0,1) to (0,3) and (0,2) to (1,2)."
REFUTATION_EXPLANATION = "The edge-set bijection satisfies the claim's premise, but G and H are not isomorphic: their sorted degree sequences are respectively (0,1,1,2) and (1,1,1,1), and graph isomorphisms preserve vertex degrees."
SEARCH_SPACE = "All 64 labeled simple undirected graphs on the fixed vertex set {0,1,2,3}; all 2016 unordered pairs were examined, including all 430 pairs with equal edge counts, and all 24 vertex bijections were checked for each such pair (10320 permutation checks total)."

VERTICES = (0, 1, 2, 3)
POSSIBLE_EDGES = tuple(itertools.combinations(VERTICES, 2))
PERMUTATIONS = tuple(itertools.permutations(VERTICES))


def graph_from_mask(mask):
    return frozenset(
        edge for index, edge in enumerate(POSSIBLE_EDGES)
        if mask & (1 << index)
    )


def degree_sequence(graph):
    degrees = []
    for vertex in VERTICES:
        degrees.append(sum(1 for edge in graph if vertex in edge))
    return tuple(sorted(degrees))


def mapped_graph(graph, permutation):
    mapped = []
    for left, right in graph:
        image = (permutation[left], permutation[right])
        mapped.append(tuple(sorted(image)))
    return frozenset(mapped)


graphs = tuple(graph_from_mask(mask) for mask in range(1 << len(POSSIBLE_EDGES)))
first_witness = None
total_pairs = 0
premise_pairs = 0
permutation_checks = 0

for left_mask in range(len(graphs)):
    for right_mask in range(left_mask + 1, len(graphs)):
        total_pairs += 1
        left_graph = graphs[left_mask]
        right_graph = graphs[right_mask]
        if len(left_graph) != len(right_graph):
            continue
        premise_pairs += 1
        isomorphic = False
        for permutation in PERMUTATIONS:
            permutation_checks += 1
            if mapped_graph(left_graph, permutation) == right_graph:
                isomorphic = True
        if not isomorphic and first_witness is None:
            first_witness = (left_mask, right_mask, left_graph, right_graph)

assert len(graphs) == 64
assert total_pairs == 2016
assert premise_pairs == 430
assert permutation_checks == 10320
assert first_witness is not None
assert first_witness[0] == 3
assert first_witness[1] == 12
assert first_witness[2] == frozenset(((0, 1), (0, 2)))
assert first_witness[3] == frozenset(((0, 3), (1, 2)))
assert degree_sequence(first_witness[2]) == (0, 1, 1, 2)
assert degree_sequence(first_witness[3]) == (1, 1, 1, 1)

result = {
    "record_id": RECORD_ID,
    "outcome": OUTCOME,
    "witness_description": WITNESS_DESCRIPTION,
    "refutation_explanation": REFUTATION_EXPLANATION,
    "search_space": SEARCH_SPACE,
}
print(json.dumps(result, separators=(",", ":")))
