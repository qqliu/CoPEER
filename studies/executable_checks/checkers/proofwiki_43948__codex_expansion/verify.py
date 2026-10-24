r'''If an edge belongs to every minimum spanning tree of the graph, then it is a minimum-weight bridge of the graph.'''

import json

RECORD_ID = "proofwiki_43948__codex_expansion"
CONFIRMED_NOTES = "The refuted statement is substantive, not plainly a typo. Exact enumeration gives a unique minimum spanning tree containing {0,1}, while deleting {0,1} leaves the graph connected, so that edge is not a bridge and therefore cannot be a minimum-weight bridge."
INVALID_NOTES = "The reported witness could not be validated by exact independent recomputation; the claimed refutation would otherwise be substantive, not plainly a typo."

vertices = (0, 1, 2)
edges = (
    (0, 1, 1),
    (0, 2, 1),
    (1, 2, 2),
)
target = (0, 1)


def connected(selected):
    reached = {vertices[0]}
    pending = [vertices[0]]
    while pending:
        current = pending.pop()
        for left, right, weight in selected:
            if left == current and right not in reached:
                reached.add(right)
                pending.append(right)
            elif right == current and left not in reached:
                reached.add(left)
                pending.append(left)
    return len(reached) == len(vertices)


spanning_trees = []
for mask in range(1 << len(edges)):
    selected = tuple(edges[index] for index in range(len(edges)) if mask & (1 << index))
    if len(selected) == len(vertices) - 1 and connected(selected):
        total_weight = sum(edge[2] for edge in selected)
        edge_set = frozenset((edge[0], edge[1]) for edge in selected)
        spanning_trees.append((total_weight, edge_set))

validated = bool(spanning_trees)
if validated:
    minimum_weight = min(item[0] for item in spanning_trees)
    minimum_trees = tuple(item[1] for item in spanning_trees if item[0] == minimum_weight)
    remaining = tuple(edge for edge in edges if (edge[0], edge[1]) != target)
    validated = (
        minimum_weight == 2
        and minimum_trees == (frozenset(((0, 1), (0, 2))),)
        and all(target in tree for tree in minimum_trees)
        and connected(remaining)
    )

verdict = "CONFIRMED" if validated else "REFUTED_WITNESS_INVALID"
notes = CONFIRMED_NOTES if validated else INVALID_NOTES
print(json.dumps({"record_id": RECORD_ID, "verdict": verdict, "notes": notes}, separators=(",", ":")))
