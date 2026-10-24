"""The rank of a graph's cycle space is always exactly two less than its number of edges."""

import itertools
import json

RECORD_ID = "reddit_math_2mw3v2"
OUTCOME = "WITNESS_FOUND"
WITNESS_DESCRIPTION = (
    "The graph on vertex set {0,1,2,3} with edge set "
    "{{0,1},{0,2},{0,3}} is a three-edge star. Its cycle space has rank 0 "
    "because its only even-degree edge subset is the empty subset."
)
REFUTATION_EXPLANATION = (
    "The claim requires this graph's cycle-space rank to equal 3 - 2 = 1, "
    "but its actual rank is 0."
)
SEARCH_SPACE = (
    "All 20 labeled simple undirected graphs on vertex set {0,1,2,3} "
    "having exactly 3 edges (every 3-element subset of the 6 possible edges), "
    "in lexicographic combination order."
)

vertices = tuple(range(4))
possible_edges = tuple(itertools.combinations(vertices, 2))
first_witness = None
examined = 0

for edges in itertools.combinations(possible_edges, 3):
    examined += 1
    even_degree_subsets = 0

    for mask in range(1 << len(edges)):
        parity = [0] * len(vertices)
        for index, (left, right) in enumerate(edges):
            if mask & (1 << index):
                parity[left] ^= 1
                parity[right] ^= 1
        if all(value == 0 for value in parity):
            even_degree_subsets += 1

    cycle_rank = even_degree_subsets.bit_length() - 1
    assert (1 << cycle_rank) == even_degree_subsets
    claimed_rank = len(edges) - 2

    if first_witness is None and cycle_rank != claimed_rank:
        first_witness = (edges, cycle_rank, claimed_rank)

assert examined == 20
assert first_witness == (
    ((0, 1), (0, 2), (0, 3)),
    0,
    1,
)

result = {
    "record_id": RECORD_ID,
    "outcome": OUTCOME,
    "witness_description": WITNESS_DESCRIPTION,
    "refutation_explanation": REFUTATION_EXPLANATION,
    "search_space": SEARCH_SPACE,
}
print(json.dumps(result, separators=(",", ":")))
