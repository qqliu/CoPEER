"""However since $G$ is $k$-edge-connected and $|X-v|=k-1$, then $G- (X-{v})$ is still connected because we have not removed enough vertices in order for sufficient edges to be removed to disconnect the graph."""

import json
from itertools import combinations

RECORD_ID = "SE_math_2693226__q"
OUTCOME = "WITNESS_FOUND"
WITNESS_DESCRIPTION = (
    "Take k=2 and the simple graph on vertices {0,1,2,3,4} with edges "
    "{0-1,0-2,1-2,0-3,0-4,3-4}. Let v=1 and X={0,1}. Then "
    "X-{v}={0} has size 1=k-1."
)
REFUTATION_EXPLANATION = (
    "Every edge lies on one of the two triangles, so deleting any one edge "
    "leaves G connected; deleting the two edges incident with vertex 1 "
    "isolates it, so G has edge-connectivity exactly 2. But "
    "G-(X-{v})=G-{0} has two components, with vertex sets {1,2} and "
    "{3,4}. Thus the stated premises hold while the asserted connectivity "
    "fails."
)
SEARCH_SPACE = (
    "All 1,099 labeled simple undirected graphs on vertex sets {0,...,n-1} "
    "for 1<=n<=5; for each graph, every k in {1,2,3,4}, every "
    "distinguished vertex v, and every vertex-deletion set S not containing "
    "v with |S|=k-1. Edge-connectivity and connectivity after deletion are "
    "checked exactly by finite cut enumeration and graph traversal."
)


def edge_connectivity_at_least(n, edges, k):
    if n < 2:
        return False
    full_mask = (1 << n) - 1
    for side_mask in range(1, full_mask):
        crossing = 0
        for a, b in edges:
            if bool(side_mask & (1 << a)) != bool(side_mask & (1 << b)):
                crossing += 1
        if crossing < k:
            return False
    return True


def connected_after_deleting(n, edges, deleted):
    remaining = [vertex for vertex in range(n) if vertex not in deleted]
    if len(remaining) <= 1:
        return True
    adjacency = {vertex: [] for vertex in remaining}
    for a, b in edges:
        if a in adjacency and b in adjacency:
            adjacency[a].append(b)
            adjacency[b].append(a)
    seen = {remaining[0]}
    stack = [remaining[0]]
    while stack:
        current = stack.pop()
        for neighbor in adjacency[current]:
            if neighbor not in seen:
                seen.add(neighbor)
                stack.append(neighbor)
    return len(seen) == len(remaining)


def exhaustive_search():
    canonical_edges = frozenset(
        {(0, 1), (0, 2), (1, 2), (0, 3), (0, 4), (3, 4)}
    )
    canonical_found = False
    graph_count = 0
    for n in range(1, 6):
        possible_edges = tuple(combinations(range(n), 2))
        for edge_mask in range(1 << len(possible_edges)):
            graph_count += 1
            edges = frozenset(
                possible_edges[index]
                for index in range(len(possible_edges))
                if edge_mask & (1 << index)
            )
            for k in range(1, 5):
                if not edge_connectivity_at_least(n, edges, k):
                    continue
                deletion_size = k - 1
                for distinguished_v in range(n):
                    eligible = tuple(
                        vertex for vertex in range(n)
                        if vertex != distinguished_v
                    )
                    for deletion_tuple in combinations(eligible, deletion_size):
                        deleted = frozenset(deletion_tuple)
                        disconnected = not connected_after_deleting(
                            n, edges, deleted
                        )
                        if (
                            disconnected
                            and n == 5
                            and k == 2
                            and edges == canonical_edges
                            and distinguished_v == 1
                            and deleted == frozenset({0})
                        ):
                            canonical_found = True
    assert graph_count == 1099
    assert canonical_found


exhaustive_search()
print(json.dumps({
    "record_id": RECORD_ID,
    "outcome": OUTCOME,
    "witness_description": WITNESS_DESCRIPTION,
    "refutation_explanation": REFUTATION_EXPLANATION,
    "search_space": SEARCH_SPACE,
}, sort_keys=False))
