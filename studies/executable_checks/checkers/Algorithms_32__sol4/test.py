r"""where Su (resp. Sv) denotes the set of vertices in the component of T -u (resp. T -v) containing v (resp. u). But then |Su| + |Sv| > n, whereas Su and Sv are disjoint subsets of V (T) (aside from u, v themselves) covering V (T) \ {u, v}, so |Su| + |Sv| = n -2 < n"""

import itertools
import json


REPORT = {
    "record_id": "Algorithms_32__sol4",
    "outcome": "WITNESS_FOUND",
    "witness_description": "T has V(T)={0,1,2} and E={{0,1},{0,2}}; n=3, u=0, and v=1. Then Su={1}, Sv={0,2}, and |Su|+|Sv|=3.",
    "refutation_explanation": "The search's first witness has Su={1} and Sv={0,2}, so their sizes sum to 3. Thus the sum is neither greater than n=3 nor equal to n-2=1. The two sets are disjoint, and after removing v from Su and u from Sv their remaining vertices cover {2}; the claimed n-2 count omits the endpoints that the component definitions include.",
    "search_space": "All labeled simple undirected trees on the fixed vertex set {0,1,2}, with every ordered pair (u,v) of distinct vertices; edge masks, u, and v were all traversed in increasing order.",
}


def component_without(adjacency, removed, start):
    seen = {start}
    stack = [start]
    while stack:
        vertex = stack.pop()
        for neighbor in adjacency[vertex]:
            if neighbor != removed and neighbor not in seen:
                seen.add(neighbor)
                stack.append(neighbor)
    return seen


vertices = tuple(range(3))
possible_edges = tuple(itertools.combinations(vertices, 2))
first_witness = None

for edge_mask in range(1 << len(possible_edges)):
    selected_edges = tuple(
        edge
        for index, edge in enumerate(possible_edges)
        if edge_mask & (1 << index)
    )
    if len(selected_edges) != len(vertices) - 1:
        continue

    adjacency = [[] for _ in vertices]
    for left, right in selected_edges:
        adjacency[left].append(right)
        adjacency[right].append(left)

    reached = {0}
    stack = [0]
    while stack:
        vertex = stack.pop()
        for neighbor in adjacency[vertex]:
            if neighbor not in reached:
                reached.add(neighbor)
                stack.append(neighbor)
    if len(reached) != len(vertices):
        continue

    for u in vertices:
        for v in vertices:
            if u == v:
                continue
            su = component_without(adjacency, u, v)
            sv = component_without(adjacency, v, u)
            total = len(su) + len(sv)
            if total != len(vertices) - 2 and first_witness is None:
                first_witness = (
                    len(vertices),
                    selected_edges,
                    u,
                    v,
                    tuple(sorted(su)),
                    tuple(sorted(sv)),
                    total,
                )

assert first_witness == (
    3,
    ((0, 1), (0, 2)),
    0,
    1,
    (1,),
    (0, 2),
    3,
)

n, edges, u, v, su_tuple, sv_tuple, total = first_witness
su = set(su_tuple)
sv = set(sv_tuple)
assert total != n - 2
assert not total > n
assert su.isdisjoint(sv)
assert (su - {v}) | (sv - {u}) == set(range(n)) - {u, v}

print(json.dumps(REPORT, separators=(",", ":")))
