"""In all cases, we conclude that our assumption was wrong: the edge emax (the heaviest
edge of cycle C) cannot be part of any minimum spanning tree."""

import itertools
import json

RECORD_ID = "Algorithms_18__sol4"
CONFIRMED_NOTES = "Exact recomputation confirms the all-weight-1 triangle witness: (0,1) is maximal on the cycle and belongs to a spanning tree of weight 2, while every spanning tree has weight 2. The refuted statement is substantive, not plainly a typo: it omits a strict-heaviest (or equivalent distinct-weights) hypothesis."
INVALID_NOTES = "The reported triangle did not independently verify as a counterexample. The alleged defect would be substantive rather than plainly a typo."

vertices = (0, 1, 2)
edges = ((0, 1), (0, 2), (1, 2))
weights = {(0, 1): 1, (0, 2): 1, (1, 2): 1}
cycle = ((0, 1), (0, 2), (1, 2))
emax = (0, 1)
reported_tree = ((0, 1), (0, 2))


def is_tree(candidate):
    if len(candidate) != len(vertices) - 1:
        return False
    reached = {vertices[0]}
    changed = True
    while changed:
        changed = False
        for u, v in candidate:
            if u in reached and v not in reached:
                reached.add(v)
                changed = True
            elif v in reached and u not in reached:
                reached.add(u)
                changed = True
    return len(reached) == len(vertices)


def is_cycle(candidate):
    degree = {v: 0 for v in vertices}
    for u, v in candidate:
        degree[u] += 1
        degree[v] += 1
    return len(candidate) == len(vertices) and all(degree[v] == 2 for v in vertices)


spanning_trees = [
    candidate
    for candidate in itertools.combinations(edges, len(vertices) - 1)
    if is_tree(candidate)
]
totals = {candidate: sum(weights[edge] for edge in candidate) for candidate in spanning_trees}
minimum = min(totals.values())

valid = (
    is_cycle(cycle)
    and emax in cycle
    and weights[emax] == max(weights[edge] for edge in cycle)
    and reported_tree in spanning_trees
    and emax in reported_tree
    and totals[reported_tree] == minimum
    and minimum == 2
    and all(total == 2 for total in totals.values())
)

result = {
    "record_id": RECORD_ID,
    "verdict": "CONFIRMED" if valid else "REFUTED_WITNESS_INVALID",
    "notes": CONFIRMED_NOTES if valid else INVALID_NOTES,
}
print(json.dumps(result, separators=(",", ":")))
