"""Proof of lemma: We need to show that in any 2(k + 1)-edge-connected graph G, there exists a spanning tree T such that G/E(T) is 2k-edge-connected."""

import json
from itertools import combinations

RECORD_ID = "Algorithms_38__sol5"
OUTCOME = "NO_WITNESS_INCONCLUSIVE"
WITNESS_DESCRIPTION = "No concrete witness was found in the bounded illustrative sweep."
REFUTATION_EXPLANATION = "The quote does not specify the domain of k, the permitted graph category, or the edge-connectivity convention for the one-vertex graph produced by contracting every edge of a spanning tree. Under the program's explicitly illustrative simple-graph, cut-based convention, every such contraction has one vertex and satisfies every cut requirement vacuously. The finite negative search therefore cannot decide the supplied claim under its unstated intended conventions."
SEARCH_SPACE = "Exactly 3,294 pairs (k,G): k in {0,1,2} and every labeled loopless simple undirected graph G on n in {2,3,4,5} vertices (2^C(n,2) graphs for each n). For each qualifying G, spanning-tree edge subsets are examined in lexicographic combination order as needed. Eligibility and quotient connectivity use the illustrative convention that r-edge-connectivity means every nonempty proper vertex cut has at least r crossing edges, so the condition is vacuous for a one-vertex quotient."


def is_r_edge_connected(vertex_count, edges, required):
    full = (1 << vertex_count) - 1
    for side in range(1, full):
        crossing = 0
        for u, v in edges:
            if ((side >> u) & 1) != ((side >> v) & 1):
                crossing += 1
        if crossing < required:
            return False
    return True


def spanning_tree(vertex_count, chosen_edges):
    parent = list(range(vertex_count))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for u, v in chosen_edges:
        ru = find(u)
        rv = find(v)
        if ru == rv:
            return False
        parent[rv] = ru
    root = find(0)
    return all(find(v) == root for v in range(vertex_count))


def quotient(vertex_count, edges, tree_edges):
    parent = list(range(vertex_count))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def unite(a, b):
        ra = find(a)
        rb = find(b)
        if ra != rb:
            parent[rb] = ra

    for u, v in tree_edges:
        unite(u, v)
    roots = []
    for vertex in range(vertex_count):
        root = find(vertex)
        if root not in roots:
            roots.append(root)
    index = {root: position for position, root in enumerate(roots)}
    quotient_edges = []
    for u, v in edges:
        quotient_edges.append((index[find(u)], index[find(v)]))
    return len(roots), tuple(quotient_edges)


def has_required_tree(vertex_count, edges, k):
    for chosen_indices in combinations(range(len(edges)), vertex_count - 1):
        tree_edges = tuple(edges[i] for i in chosen_indices)
        if not spanning_tree(vertex_count, tree_edges):
            continue
        quotient_vertices, quotient_edges = quotient(vertex_count, edges, tree_edges)
        if is_r_edge_connected(quotient_vertices, quotient_edges, 2 * k):
            return True
    return False


def search():
    counterexample = None
    examined_pairs = 0
    for k in range(3):
        for vertex_count in range(2, 6):
            possible_edges = tuple(combinations(range(vertex_count), 2))
            for edge_mask in range(1 << len(possible_edges)):
                examined_pairs += 1
                edges = tuple(
                    possible_edges[i]
                    for i in range(len(possible_edges))
                    if (edge_mask >> i) & 1
                )
                if not is_r_edge_connected(vertex_count, edges, 2 * (k + 1)):
                    continue
                if not has_required_tree(vertex_count, edges, k):
                    counterexample = (k, vertex_count, edge_mask)
                    return examined_pairs, counterexample
    return examined_pairs, counterexample


def main():
    examined_pairs, counterexample = search()
    assert examined_pairs == 3294
    assert counterexample is None
    result = {
        "record_id": RECORD_ID,
        "outcome": OUTCOME,
        "witness_description": WITNESS_DESCRIPTION,
        "refutation_explanation": REFUTATION_EXPLANATION,
        "search_space": SEARCH_SPACE,
    }
    print(json.dumps(result, separators=(",", ":")))


if __name__ == "__main__":
    main()
