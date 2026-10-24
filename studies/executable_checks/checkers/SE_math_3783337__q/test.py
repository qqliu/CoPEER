"""Removing edges on cycles from $G$ doesn't change the number of connected components, because, for each edge $e$ that was removed from $G$, there is a path between the endpoints of $e$ that doesn't include $e$."""

import json
from itertools import combinations


def connected(n, edges, active_mask, start, goal):
    seen = [False] * n
    seen[start] = True
    queue = [start]
    head = 0
    while head < len(queue):
        vertex = queue[head]
        head += 1
        if vertex == goal:
            return True
        for bit, edge in enumerate(edges):
            if active_mask & (1 << bit):
                a, b = edge
                if a == vertex and not seen[b]:
                    seen[b] = True
                    queue.append(b)
                elif b == vertex and not seen[a]:
                    seen[a] = True
                    queue.append(a)
    return False


def component_count(n, edges, active_mask):
    seen = [False] * n
    count = 0
    for start in range(n):
        if seen[start]:
            continue
        count += 1
        seen[start] = True
        queue = [start]
        head = 0
        while head < len(queue):
            vertex = queue[head]
            head += 1
            for bit, edge in enumerate(edges):
                if active_mask & (1 << bit):
                    a, b = edge
                    neighbor = -1
                    if a == vertex:
                        neighbor = b
                    elif b == vertex:
                        neighbor = a
                    if neighbor != -1 and not seen[neighbor]:
                        seen[neighbor] = True
                        queue.append(neighbor)
    return count


first_witness = None
swept = 0
for n in range(1, 5):
    edges = tuple(combinations(range(n), 2))
    mask_limit = 1 << len(edges)
    for graph_mask in range(mask_limit):
        for removal_mask in range(mask_limit):
            if removal_mask & ~graph_mask:
                continue
            swept += 1
            all_removed_edges_are_on_cycles = True
            for bit, edge in enumerate(edges):
                if removal_mask & (1 << bit):
                    without_edge = graph_mask & ~(1 << bit)
                    if not connected(n, edges, without_edge, edge[0], edge[1]):
                        all_removed_edges_are_on_cycles = False
                        break
            if not all_removed_edges_are_on_cycles:
                continue
            before = component_count(n, edges, graph_mask)
            after = component_count(n, edges, graph_mask & ~removal_mask)
            if after != before and first_witness is None:
                first_witness = (n, edges, graph_mask, removal_mask, before, after)

assert swept == 760
assert first_witness == (
    3,
    ((0, 1), (0, 2), (1, 2)),
    7,
    3,
    1,
    2,
)

result = {
    "record_id": "SE_math_3783337__q",
    "outcome": "WITNESS_FOUND",
    "witness_description": "Let G be the labeled triangle on vertices {0,1,2}, and remove R={{0,1},{0,2}} simultaneously. Each removed edge is on the triangle's cycle. G has one connected component, while G-R has two: {0} and {1,2}.",
    "refutation_explanation": "For edge {0,1}, the alternate path 0-2-1 uses the other removed edge {0,2}; for edge {0,2}, the alternate path 0-1-2 uses the other removed edge {0,1}. Thus the separate alternate paths exist in G but neither survives the simultaneous removal, so the number of connected components increases.",
    "search_space": "Exhaustively swept all 760 pairs (G,R) where G is a labeled simple undirected graph on n vertices for each n in {1,2,3,4}, and R is every subset of E(G). For every pair, each edge of R was required to have its endpoints connected in G with that edge deleted (equivalently, to lie on a cycle of G), and the component counts of G and G-R were compared. The lexicographically first witness under increasing n, graph bitmask, and removal bitmask is reported.",
}
print(json.dumps(result, separators=(",", ":")))
