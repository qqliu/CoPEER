"""since x in B because R contains v and R is connected by red edges, v and x are connected by a red path, implying x is reachable by a blue path from v as well; thus x in B"""

import itertools
import json

REPORT = {
    "record_id": "Graph Theory_20__sol4",
    "outcome": "WITNESS_FOUND",
    "witness_description": "On labeled vertices {0,1}, let v=0, x=1, and R={0,1}; make {0,1} a red edge and include no blue edges.",
    "refutation_explanation": "R contains v and is connected by red edges, so v and x are joined by a red path. With no blue edges and v != x, x is not reachable from v by a blue path; hence the claimed red-path-to-blue-path implication fails.",
    "search_space": "All 4 ordered pairs (red_mask, blue_mask) in {0,1}^2 for the sole possible undirected edge on labeled vertices {0,1}, with R={0,1}, v=0, and x=1; red and blue edge sets were chosen independently and every pair was swept.",
}

VERTICES = (0, 1)
R = (0, 1)
V = 0
X = 1
POSSIBLE_EDGES = ((0, 1),)


def edges_for(mask):
    return tuple(
        edge
        for index, edge in enumerate(POSSIBLE_EDGES)
        if mask & (1 << index)
    )


def reachable(start, edges):
    seen = {start}
    queue = [start]
    position = 0
    while position < len(queue):
        current = queue[position]
        position += 1
        for left, right in edges:
            if left == current and right not in seen:
                seen.add(right)
                queue.append(right)
            elif right == current and left not in seen:
                seen.add(left)
                queue.append(left)
    return seen


colorings = tuple(itertools.product(range(2), repeat=2))
visited = []
violations = []

for red_mask, blue_mask in colorings:
    visited.append((red_mask, blue_mask))
    red_edges = edges_for(red_mask)
    blue_edges = edges_for(blue_mask)
    red_reachable = reachable(V, red_edges)
    blue_reachable = reachable(V, blue_edges)
    premises_hold = V in R and X in R and all(
        vertex in red_reachable for vertex in R
    )
    if premises_hold and X not in blue_reachable:
        violations.append((red_mask, blue_mask, red_edges, blue_edges))

assert tuple(visited) == colorings
assert len(colorings) == 4
assert violations
first = violations[0]
assert first == (1, 0, ((0, 1),), ())
assert all(vertex in reachable(V, first[2]) for vertex in R)
assert X not in reachable(V, first[3])
assert REPORT["record_id"] == "Graph Theory_20__sol4"
assert REPORT["outcome"] == "WITNESS_FOUND"

print(json.dumps(REPORT, separators=(",", ":")))
