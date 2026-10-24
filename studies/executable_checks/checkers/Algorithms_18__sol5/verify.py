"""Independent exact witness checker.

we conclude that no maximum-weight edge of any cycle in G can belong to the MST.
"""

import json
from itertools import combinations

RECORD_ID = "Algorithms_18__sol5"
CONFIRMED_NOTES = (
    "Exact recomputation confirms that the equal-weight triangle has three "
    "MSTs of weight 2, and every edge in every MST is tied for maximum weight "
    "on the triangle cycle. The refuted statement is substantive, not plainly "
    "a typo: it omits the uniqueness/strict-heaviness condition required by "
    "the cycle property."
)

vertices = (0, 1, 2)
edges = ((0, 1), (0, 2), (1, 2))
weights = {edge: 1 for edge in edges}


def connected(vertex_set, edge_set):
    if not vertex_set:
        return True
    reached = {vertex_set[0]}
    changed = True
    while changed:
        changed = False
        for u, v in edge_set:
            if u in reached and v not in reached:
                reached.add(v)
                changed = True
            if v in reached and u not in reached:
                reached.add(u)
                changed = True
    return reached == set(vertex_set)


def is_tree(edge_set):
    return len(edge_set) == len(vertices) - 1 and connected(vertices, edge_set)


def is_cycle(edge_set):
    if len(edge_set) < 3:
        return False
    incident = sorted({x for edge in edge_set for x in edge})
    degrees = {x: 0 for x in incident}
    for u, v in edge_set:
        degrees[u] += 1
        degrees[v] += 1
    return all(degrees[x] == 2 for x in incident) and connected(incident, edge_set)


spanning_trees = [
    frozenset(candidate)
    for candidate in combinations(edges, len(vertices) - 1)
    if is_tree(candidate)
]
tree_weights = {tree: sum(weights[edge] for edge in tree) for tree in spanning_trees}
minimum_weight = min(tree_weights.values())
msts = [tree for tree in spanning_trees if tree_weights[tree] == minimum_weight]

cycles = []
for size in range(3, len(edges) + 1):
    for candidate in combinations(edges, size):
        if is_cycle(candidate):
            cycles.append(frozenset(candidate))

cycle_max_edges = set()
for cycle in cycles:
    maximum = max(weights[edge] for edge in cycle)
    cycle_max_edges.update(edge for edge in cycle if weights[edge] == maximum)

witness_valid = (
    connected(vertices, edges)
    and cycles == [frozenset(edges)]
    and len(spanning_trees) == 3
    and len(msts) == 3
    and minimum_weight == 2
    and cycle_max_edges == set(edges)
    and all(any(edge in cycle_max_edges for edge in tree) for tree in msts)
)

if witness_valid:
    verdict = "CONFIRMED"
    notes = CONFIRMED_NOTES
else:
    verdict = "REFUTED_WITNESS_INVALID"
    notes = "Exact recomputation did not validate the reported witness."

print(json.dumps({
    "record_id": RECORD_ID,
    "verdict": verdict,
    "notes": notes,
}, separators=(",", ":")))
