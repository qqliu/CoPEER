"""By partitioning any even cycle within the graph by their subscripts such that all even subscripted vertex are separated from the odd subscripted vertex, we have created a bipartite graph."""

import itertools
import json

RECORD_ID = "SE_math_2233469__q"
WITNESS_DESCRIPTION = (
    "On vertices {0,1,2,3}, take edges {0,1}, {0,2}, {0,3}, {1,2}, "
    "and {1,3}. The indexed 4-cycle (v0,v1,v2,v3)=(0,2,1,3) has "
    "parity parts {0,1} and {2,3}."
)
REFUTATION_EXPLANATION = (
    "The graph contains the stated even cycle, but edge {0,1} has both "
    "endpoints in the even-indexed part, so the proposed partition is not "
    "a bipartition of the ambient graph. Indeed, {0,1}, {0,2}, and {1,2} "
    "form a triangle."
)
SEARCH_SPACE = (
    "All 64 labeled simple undirected graphs on vertex set {0,1,2,3}, "
    "with all three canonical indexed 4-cycles checked in every graph."
)

vertices = tuple(range(4))
edges = tuple(itertools.combinations(vertices, 2))
edge_index = {edge: index for index, edge in enumerate(edges)}
cycles = tuple(
    (0,) + tail
    for tail in itertools.permutations((1, 2, 3))
    if tail[0] < tail[-1]
)


def present(mask, left, right):
    edge = (left, right) if left < right else (right, left)
    return ((mask >> edge_index[edge]) & 1) == 1


counterexamples = []
for mask in range(1 << len(edges)):
    for cycle in cycles:
        cycle_is_present = all(
            present(mask, cycle[index], cycle[(index + 1) % 4])
            for index in range(4)
        )
        if not cycle_is_present:
            continue
        even_part = (cycle[0], cycle[2])
        odd_part = (cycle[1], cycle[3])
        bad_edges = tuple(
            edge
            for edge in edges
            if present(mask, edge[0], edge[1])
            and (
                (edge[0] in even_part and edge[1] in even_part)
                or (edge[0] in odd_part and edge[1] in odd_part)
            )
        )
        if bad_edges:
            counterexamples.append((mask, cycle, bad_edges))

expected_mask = sum(
    1 << edge_index[edge]
    for edge in ((0, 1), (0, 2), (0, 3), (1, 2), (1, 3))
)
assert counterexamples
assert counterexamples[0] == (expected_mask, (0, 2, 1, 3), ((0, 1),))

result = {
    "record_id": RECORD_ID,
    "outcome": "WITNESS_FOUND",
    "witness_description": WITNESS_DESCRIPTION,
    "refutation_explanation": REFUTATION_EXPLANATION,
    "search_space": SEARCH_SPACE,
}
print(json.dumps(result, separators=(",", ":")))
