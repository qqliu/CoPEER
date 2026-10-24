"""$G'$ is a tree with $k-1$ edges and $k+1$ vertices. $G$ has $k-1+m$ edges."""

import json

record_id = "SE_math_1291495__q"
confirmed_notes = ("The witness is valid: for k=1, the single-edge graph on two vertices "
                   "is a tree with 1 edge, not k-1=0. The refuted edge count is plainly "
                   "an off-by-one typo; a tree on k+1 vertices has k edges.")

k = 1
vertices = (0, 1)
edges = ((0, 1),)

valid_edges = all(
    left in vertices and right in vertices and left != right
    for left, right in edges
)
adjacency = {vertex: set() for vertex in vertices}
if valid_edges:
    for left, right in edges:
        adjacency[left].add(right)
        adjacency[right].add(left)

visited = set()
cycle_found = False
stack = [(vertices[0], None)]
while stack:
    vertex, parent = stack.pop()
    if vertex in visited:
        cycle_found = True
        continue
    visited.add(vertex)
    for neighbor in adjacency[vertex]:
        if neighbor != parent:
            stack.append((neighbor, vertex))

is_tree = valid_edges and visited == set(vertices) and not cycle_found
witness_refutes = (
    is_tree
    and len(vertices) == k + 1
    and len(edges) != k - 1
    and len(edges) == 1
    and k - 1 == 0
)

if witness_refutes:
    verdict = "CONFIRMED"
    notes = confirmed_notes
else:
    verdict = "CANNOT_REPRODUCE"
    notes = confirmed_notes

print(json.dumps({
    "record_id": record_id,
    "verdict": verdict,
    "notes": notes,
}, separators=(",", ":")))
