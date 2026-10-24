r"""By construction, X can be ordered as x1, x2, . . . , x|X| in the order they were deleted, and at the time xj was deleted it had fewer than t neighbors remaining. In particular, in the induced subgraph on {x1, . . . , xj-1} it has degree at most t - 1."""

import itertools
import json

REPORT = {
    "record_id": "Graph Theory_19__sol1",
    "outcome": "NO_WITNESS_INCONCLUSIVE",
    "witness_description": "No certified witness. In the illustrative 48-pair sweep, the first reverse-direction obstruction is the graph with edges {0,1} and {0,2} and deletion order (1,2,0), but the quote does not say that this graph/order can arise from the referenced construction.",
    "refutation_explanation": "The construction defining X is absent, and the displayed induced subgraph on {x1,...,xj-1} does not contain xj, so \"it has degree\" is not a defined test as written. A bounded graph sweep cannot decide the claim without inventing an admissibility rule or repairing the conclusion.",
    "search_space": "Illustrative exhaustive sweep of all 8 simple undirected graphs on labeled vertex set {0,1,2} and all 6 deletion orders at t=2 (48 graph-order pairs), in increasing edge-mask and lexicographic order; this is not the unspecified construction's admissible space.",
}

vertices = (0, 1, 2)
t = 2
possible_edges = tuple(itertools.combinations(vertices, 2))
orders = tuple(itertools.permutations(vertices))
masks = tuple(range(2 ** len(possible_edges)))
checked = 0
first_reverse_obstruction = None


def edge_key(a, b):
    return (a, b) if a < b else (b, a)


for mask in masks:
    edges = frozenset(
        edge
        for bit, edge in enumerate(possible_edges)
        if mask & (1 << bit)
    )
    for order in orders:
        checked += 1
        remaining_counts = []
        premise_holds = True
        for position, vertex in enumerate(order):
            remaining = order[position + 1:]
            count = sum(
                1 for other in remaining
                if edge_key(vertex, other) in edges
            )
            remaining_counts.append(count)
            if count >= t:
                premise_holds = False

        if premise_holds:
            for position, vertex in enumerate(order):
                earlier = order[:position]
                earlier_count = sum(
                    1 for other in earlier
                    if edge_key(vertex, other) in edges
                )
                if earlier_count > t - 1:
                    candidate = (
                        mask,
                        order,
                        tuple(remaining_counts),
                        position,
                        earlier_count,
                    )
                    if first_reverse_obstruction is None:
                        first_reverse_obstruction = candidate
                    break

space_size = len(masks) * len(orders)
assert checked == space_size
assert space_size == 48
assert first_reverse_obstruction == (3, (1, 2, 0), (1, 1, 0), 2, 2)

print(json.dumps(REPORT, separators=(",", ":")))
