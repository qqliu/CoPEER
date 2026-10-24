"""Then, the biggest group of fully connected vertices would be 4 as in the modified $K_5$."""

import json
from itertools import combinations

RECORD_ID = "SE_math_696164__q"
OUTCOME = "NO_WITNESS_INCONCLUSIVE"
WITNESS_DESCRIPTION = "No certified witness: the quote does not define the graph denoted by \"the modified K_5\" or specify which modification is allowed."
REFUTATION_EXPLANATION = "The modeled finite sweep contains proper edge-deleted subgraphs of K_5 with clique numbers 1, 2, 3, and 4, so the value 4 is not forced by that broad interpretation. However, because the supplied quote never defines \"modified K_5\", none of those modeled graphs can be certified as the graph addressed by the claim; the result is therefore inconclusive rather than a refutation."
SEARCH_SPACE = "All 2^10 = 1024 labeled simple undirected graphs on vertices {0,1,2,3,4} whose edges are subsets of the 10 edges of K_5, enumerated by edge-mask integers 0 through 1023; every nonempty vertex subset was checked exactly for being a clique."

vertices = tuple(range(5))
edges = tuple(combinations(vertices, 2))
edge_index = {edge: index for index, edge in enumerate(edges)}


def has_edge(mask, left, right):
    edge = (left, right) if left < right else (right, left)
    return (mask & (1 << edge_index[edge])) != 0


def clique_number(mask):
    largest = 0
    for size in range(1, len(vertices) + 1):
        for subset in combinations(vertices, size):
            if all(has_edge(mask, left, right) for left, right in combinations(subset, 2)):
                largest = size
    return largest


complete_mask = (1 << len(edges)) - 1
proper_subgraph_clique_numbers = set()
searched = 0
for mask in range(complete_mask + 1):
    omega = clique_number(mask)
    searched += 1
    if mask != complete_mask:
        proper_subgraph_clique_numbers.add(omega)

assert searched == 1024
assert proper_subgraph_clique_numbers == {1, 2, 3, 4}

result = {
    "record_id": RECORD_ID,
    "outcome": OUTCOME,
    "witness_description": WITNESS_DESCRIPTION,
    "refutation_explanation": REFUTATION_EXPLANATION,
    "search_space": SEARCH_SPACE,
}
print(json.dumps(result, separators=(",", ":")))
