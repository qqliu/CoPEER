r"""Suppose G = (V, E) is a connected graph with weighted edges. Establish that for any cycle in G, the maximum-weight edge of that cycle is not included in the minimum spanning tree of G."""

import itertools
import json

REPORT = {
    "record_id": "Algorithms_18__sol3",
    "outcome": "WITNESS_FOUND",
    "witness_description": "On V={0,1,2}, let E={(0,1),(0,2),(1,2)} and give every edge weight 1. The spanning tree T={(0,1),(0,2)} is a minimum spanning tree, while the cycle ((0,1),(0,2),(1,2)) has maximum weight 1 and T contains the maximum-weight edge (0,1).",
    "refutation_explanation": "All three spanning trees have total weight 2, so T is minimum. Because all three cycle edges attain the maximum weight, the claim fails without a distinct-weights or unique-maximum assumption.",
    "search_space": "All 8 labeled simple undirected graphs on V={0,1,2}, with every present edge assigned the sole allowed weight 1; for each connected graph, every 2-edge subset was checked as a spanning-tree candidate and the sole possible 3-cycle was checked."
}

VERTICES = (0, 1, 2)
ALL_EDGES = ((0, 1), (0, 2), (1, 2))
ALLOWED_WEIGHTS = (1,)


def is_connected(edges):
    seen = {VERTICES[0]}
    changed = True
    while changed:
        changed = False
        for left, right in edges:
            if left in seen and right not in seen:
                seen.add(right)
                changed = True
            elif right in seen and left not in seen:
                seen.add(left)
                changed = True
    return len(seen) == len(VERTICES)


def is_spanning_tree(edges):
    return len(edges) == len(VERTICES) - 1 and is_connected(edges)


violations = []
for mask in range(1 << len(ALL_EDGES)):
    present_edges = tuple(
        edge for index, edge in enumerate(ALL_EDGES)
        if mask & (1 << index)
    )
    for assignment in itertools.product(ALLOWED_WEIGHTS, repeat=len(present_edges)):
        weights = dict(zip(present_edges, assignment))
        if not is_connected(present_edges):
            continue

        candidates = []
        for chosen in itertools.combinations(present_edges, len(VERTICES) - 1):
            if is_spanning_tree(chosen):
                candidates.append((sum(weights[edge] for edge in chosen), chosen))
        minimum_cost = min(cost for cost, chosen in candidates)
        minimum_trees = tuple(
            chosen for cost, chosen in candidates if cost == minimum_cost
        )

        cycles = (ALL_EDGES,) if all(edge in weights for edge in ALL_EDGES) else ()
        for cycle in cycles:
            maximum_weight = max(weights[edge] for edge in cycle)
            for tree in minimum_trees:
                for edge in cycle:
                    if edge in tree and weights[edge] == maximum_weight:
                        violations.append(
                            (present_edges, assignment, cycle, tree,
                             minimum_cost, maximum_weight, edge)
                        )

first = violations[0] if violations else None
assert first is not None
assert first == (
    ALL_EDGES,
    (1, 1, 1),
    ALL_EDGES,
    ((0, 1), (0, 2)),
    2,
    1,
    (0, 1),
)
assert REPORT["outcome"] == "WITNESS_FOUND"
print(json.dumps(REPORT))
