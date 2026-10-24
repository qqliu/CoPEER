r"""Induction hypothesis: Suppose any bipartite graph $G$ with bipartition $A,B$, satisfying Hall's condition for $A$, and such that $\deg(v)\geq m$ for all $v\in A$ admits $m!$ matchings saturating all of $A$."""

import json
from math import factorial

RECORD_ID = "mse_354006__ans354460"
M = 3
A = ("a0",)
B = ("b0", "b1", "b2")


def edges_from_mask(mask):
    edges = set()
    bit = 0
    for a in A:
        for b in B:
            if mask & (1 << bit):
                edges.add((a, b))
            bit += 1
    return edges


def satisfies_hall(edges):
    for subset_mask in range(1 << len(A)):
        subset = tuple(A[i] for i in range(len(A)) if subset_mask & (1 << i))
        neighbors = {b for a in subset for b in B if (a, b) in edges}
        if len(neighbors) < len(subset):
            return False
    return True


def minimum_degree_at_least(edges, bound):
    return all(sum((a, b) in edges for b in B) >= bound for a in A)


def count_saturating_matchings(edges):
    def extend(index, used_b):
        if index == len(A):
            return 1
        total = 0
        a = A[index]
        for b in B:
            if b not in used_b and (a, b) in edges:
                total += extend(index + 1, used_b | {b})
        return total

    return extend(0, set())


violations = []
checked = 0
for edge_mask in range(1 << (len(A) * len(B))):
    checked += 1
    graph_edges = edges_from_mask(edge_mask)
    if satisfies_hall(graph_edges) and minimum_degree_at_least(graph_edges, M):
        matching_count = count_saturating_matchings(graph_edges)
        if matching_count < factorial(M):
            violations.append((edge_mask, matching_count))

assert checked == 8
assert violations == [(7, 3)]

result = {
    "record_id": RECORD_ID,
    "outcome": "WITNESS_FOUND",
    "witness_description": "Take m=3, A={a0}, B={b0,b1,b2}, and E={(a0,b0),(a0,b1),(a0,b2)}. This graph satisfies Hall's condition for A, deg(a0)=3, and has exactly 3 matchings saturating A.",
    "refutation_explanation": "The claimed conclusion requires at least 3!=6 distinct matchings saturating A, but the witness has only 3, one for each possible edge incident to a0. Thus it does not admit 3! such matchings.",
    "search_space": "All 8 labeled simple bipartite graphs with A={a0} and B={b0,b1,b2}, obtained from all 2^3 edge subsets, at fixed m=3. Every graph was checked for Hall's condition, minimum A-degree at least 3, and its exact number of A-saturating matchings."
}
print(json.dumps(result))
