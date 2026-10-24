"""Suppose we have a graph G with |V| vertices that has a minimum spanning tree.  Suppose we also have a set of |V| - 1 edges = <$e_1$, $e_2$, ..., $e_n$>, such that each edge is a light edge for some cut C, and these edges do not form a cycle.  This set of edges must form a minimum spanning tree."""

import itertools
import json

RECORD_ID = "SE_cs_91264__q"
OUTCOME = "WITNESS_FOUND"
WITNESS_DESCRIPTION = (
    "On vertices {0,1,2}, take edges 0-1 of weight 1, 0-2 of weight 2, "
    "and 1-2 of weight 2; choose {0-2,1-2}."
)
REFUTATION_EXPLANATION = (
    "The chosen two edges are acyclic. Each is light for the cut {0,1}|{2}, "
    "where both crossing edges have minimum weight 2. Their total weight is 4, "
    "while {0-1,0-2} is a spanning tree of total weight 3, so the chosen set "
    "is not a minimum spanning tree."
)
SEARCH_SPACE = (
    "All complete undirected simple graphs on labeled vertices {0,...,n-1} for "
    "n=2,3,4, with every edge weight in {1,2,3}, and every (n-1)-edge subset: "
    "exactly 14,664 candidate subsets. For lightness, the possible cuts are all "
    "nontrivial bipartitions, represented canonically by the side containing "
    "vertex 0."
)


def complete_edges(n):
    return tuple(itertools.combinations(range(n), 2))


def is_tree(n, edges, chosen):
    if len(chosen) != n - 1:
        return False
    parent = list(range(n))

    def find(vertex):
        while parent[vertex] != vertex:
            vertex = parent[vertex]
        return vertex

    for edge_index in chosen:
        u, v = edges[edge_index]
        root_u = find(u)
        root_v = find(v)
        if root_u == root_v:
            return False
        parent[root_v] = root_u
    root = find(0)
    return all(find(vertex) == root for vertex in range(n))


def crosses(edge, mask):
    u, v = edge
    return bool(mask & (1 << u)) != bool(mask & (1 << v))


def is_light_for_some_cut(n, edges, weights, edge_index):
    full_mask = (1 << n) - 1
    for mask in range(1, full_mask):
        if not (mask & 1):
            continue
        if not crosses(edges[edge_index], mask):
            continue
        crossing_indices = tuple(
            index for index, edge in enumerate(edges) if crosses(edge, mask)
        )
        minimum_weight = min(weights[index] for index in crossing_indices)
        if weights[edge_index] == minimum_weight:
            return True
    return False


def minimum_spanning_tree_weight(n, edges, weights):
    totals = []
    for chosen in itertools.combinations(range(len(edges)), n - 1):
        if is_tree(n, edges, chosen):
            totals.append(sum(weights[index] for index in chosen))
    return min(totals)


def search():
    first_witness = None
    swept = 0
    for n in range(2, 5):
        edges = complete_edges(n)
        for weights in itertools.product((1, 2, 3), repeat=len(edges)):
            optimum = minimum_spanning_tree_weight(n, edges, weights)
            for chosen in itertools.combinations(range(len(edges)), n - 1):
                swept += 1
                if not is_tree(n, edges, chosen):
                    continue
                if not all(
                    is_light_for_some_cut(n, edges, weights, edge_index)
                    for edge_index in chosen
                ):
                    continue
                chosen_weight = sum(weights[index] for index in chosen)
                if chosen_weight > optimum and first_witness is None:
                    first_witness = (n, edges, weights, chosen)
    return swept, first_witness


def main():
    swept, witness = search()
    expected = (
        3,
        ((0, 1), (0, 2), (1, 2)),
        (1, 2, 2),
        (1, 2),
    )
    if swept != 14664 or witness != expected:
        raise RuntimeError("deterministic exhaustive search produced an unexpected result")
    result = {
        "record_id": RECORD_ID,
        "outcome": OUTCOME,
        "witness_description": WITNESS_DESCRIPTION,
        "refutation_explanation": REFUTATION_EXPLANATION,
        "search_space": SEARCH_SPACE,
    }
    print(json.dumps(result))


if __name__ == "__main__":
    main()
