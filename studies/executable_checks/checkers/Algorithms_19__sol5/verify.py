r"""**Cut Property**: For any partition of the vertex set V into two subsets S and V \ S, the edge of minimum weight crossing the partition belongs to every MST."""

import json
from itertools import combinations

record_id = "Algorithms_19__sol5"
confirmed_notes = ("Exact integer enumeration confirms the witness: (0,1) is a "
                   "minimum-weight edge crossing {0}|{1,2}, while "
                   "{(0,2),(1,2)} is a minimum spanning tree and omits it. "
                   "The refuted statement is substantive, not plainly a typo: "
                   "without uniqueness, a light cut edge need only belong to "
                   "some MST, not every MST.")
invalid_notes = ("Independent exact recomputation did not validate the concrete "
                 "witness. The alleged issue would be substantive rather than "
                 "plainly a typo if established.")

vertices = (0, 1, 2)
edges = ((0, 1), (0, 2), (1, 2))
weights = {(0, 1): 1, (0, 2): 1, (1, 2): 1}
cut = {0}
selected_edge = (0, 1)
omitting_tree = frozenset(((0, 2), (1, 2)))


def is_tree(candidate):
    if len(candidate) != len(vertices) - 1:
        return False
    parent = {vertex: vertex for vertex in vertices}

    def representative(vertex):
        while parent[vertex] != vertex:
            vertex = parent[vertex]
        return vertex

    for left, right in candidate:
        left_root = representative(left)
        right_root = representative(right)
        if left_root == right_root:
            return False
        parent[left_root] = right_root
    return len({representative(vertex) for vertex in vertices}) == 1


crossing = tuple(
    edge for edge in edges
    if (edge[0] in cut) != (edge[1] in cut)
)
spanning_trees = []
for candidate in combinations(edges, len(vertices) - 1):
    if is_tree(candidate):
        spanning_trees.append(
            (frozenset(candidate), sum(weights[edge] for edge in candidate))
        )

minimum_tree_weight = min(total for _, total in spanning_trees)
minimum_crossing_weight = min(weights[edge] for edge in crossing)
omitting_tree_weight = sum(weights[edge] for edge in omitting_tree)
partition_is_proper = bool(cut) and cut < set(vertices)

witness_valid = (
    partition_is_proper
    and selected_edge in crossing
    and weights[selected_edge] == minimum_crossing_weight
    and selected_edge not in omitting_tree
    and is_tree(tuple(omitting_tree))
    and omitting_tree_weight == minimum_tree_weight
    and any(
        tree == omitting_tree and total == minimum_tree_weight
        for tree, total in spanning_trees
    )
)

result = {
    "record_id": record_id,
    "verdict": "CONFIRMED" if witness_valid else "REFUTED_WITNESS_INVALID",
    "notes": confirmed_notes if witness_valid else invalid_notes,
}
print(json.dumps(result, separators=(",", ":")))
