"""If e belongs to a cycle, and it belongs to MST, doesn't it immediately imply that the MST has a cycle and therefore is not a tree?"""

import itertools
import json

RECORD_ID = "SE_cs_35434__q"
OUTCOME = "WITNESS_FOUND"
WITNESS_DESCRIPTION = (
    "Let G be the triangle on vertices {0,1,2}, with all three edges having "
    "weight 1. Let T have edges {(0,1),(0,2)}, and let e=(0,1). Then e lies "
    "on the cycle 0-1-2-0 in G and e belongs to the MST T, while T is the "
    "acyclic path 1-0-2."
)
REFUTATION_EXPLANATION = (
    "T has total weight 2, equal to every spanning tree of G, so T is an MST. "
    "The cycle containing e in G uses edge (1,2), which is absent from T; "
    "consequently, membership of e in both the ambient cycle and T does not "
    "put the whole cycle in T."
)
SEARCH_SPACE = (
    "Exhaustively swept all 64 simple undirected weighted graphs on the fixed "
    "vertex set {0,1,2}, where each present edge has weight in {1,2,3}, "
    "together with all 8 subsets of the three possible edges as candidate MSTs "
    "and all 3 possible distinguished edges: 64*8*3 = 1536 tuples, in fixed "
    "lexicographic order."
)

VERTICES = (0, 1, 2)
EDGES = ((0, 1), (0, 2), (1, 2))


def connected(edge_mask):
    reached = {0}
    changed = True
    while changed:
        changed = False
        for index, (left, right) in enumerate(EDGES):
            if edge_mask & (1 << index):
                if left in reached and right not in reached:
                    reached.add(right)
                    changed = True
                if right in reached and left not in reached:
                    reached.add(left)
                    changed = True
    return len(reached) == len(VERTICES)


def is_tree(edge_mask):
    return edge_mask.bit_count() == len(VERTICES) - 1 and connected(edge_mask)


def edge_is_on_cycle(graph_mask, edge_index):
    bit = 1 << edge_index
    if not graph_mask & bit:
        return False
    left, right = EDGES[edge_index]
    reduced_mask = graph_mask & ~bit
    reached = {left}
    changed = True
    while changed:
        changed = False
        for index, (a, b) in enumerate(EDGES):
            if reduced_mask & (1 << index):
                if a in reached and b not in reached:
                    reached.add(b)
                    changed = True
                if b in reached and a not in reached:
                    reached.add(a)
                    changed = True
    return right in reached


def tree_weight(tree_mask, weights):
    return sum(
        weights[index]
        for index in range(len(EDGES))
        if tree_mask & (1 << index)
    )


def is_mst(graph_mask, tree_mask, weights):
    if tree_mask & ~graph_mask or not is_tree(tree_mask):
        return False
    spanning_trees = tuple(
        candidate
        for candidate in range(1 << len(EDGES))
        if not candidate & ~graph_mask and is_tree(candidate)
    )
    if not spanning_trees:
        return False
    minimum_weight = min(tree_weight(candidate, weights) for candidate in spanning_trees)
    return tree_weight(tree_mask, weights) == minimum_weight


witnesses = []
weighted_graph_count = 0
examined_tuple_count = 0
for graph_mask in range(1 << len(EDGES)):
    present_indices = tuple(
        index for index in range(len(EDGES)) if graph_mask & (1 << index)
    )
    for assigned_weights in itertools.product((1, 2, 3), repeat=len(present_indices)):
        weighted_graph_count += 1
        mutable_weights = [0, 0, 0]
        for position, edge_index in enumerate(present_indices):
            mutable_weights[edge_index] = assigned_weights[position]
        weights = tuple(mutable_weights)
        for tree_mask in range(1 << len(EDGES)):
            for edge_index in range(len(EDGES)):
                examined_tuple_count += 1
                edge_bit = 1 << edge_index
                if (
                    tree_mask & edge_bit
                    and edge_is_on_cycle(graph_mask, edge_index)
                    and is_mst(graph_mask, tree_mask, weights)
                    and is_tree(tree_mask)
                ):
                    witnesses.append((graph_mask, weights, tree_mask, edge_index))

assert weighted_graph_count == 64
assert examined_tuple_count == 1536
assert witnesses
assert witnesses[0] == (7, (1, 1, 1), 3, 0)

print(json.dumps({
    "record_id": RECORD_ID,
    "outcome": OUTCOME,
    "witness_description": WITNESS_DESCRIPTION,
    "refutation_explanation": REFUTATION_EXPLANATION,
    "search_space": SEARCH_SPACE,
}, separators=(",", ":")))
