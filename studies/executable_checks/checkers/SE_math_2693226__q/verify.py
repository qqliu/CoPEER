r'''However since $G$ is $k$-edge-connected and $|X-v|=k-1$, then $G- (X-{v})$ is still connected because we have not removed enough vertices in order for sufficient edges to be removed to disconnect the graph.'''

import json

record_id = "SE_math_2693226__q"
confirmed_note = ("The refuted statement is substantive, not a typo: exact cut "
                  "enumeration gives edge-connectivity 2, while deleting "
                  "X-{v}={0} leaves the two components {1,2} and {3,4}. "
                  "Edge-connectivity does not imply the corresponding "
                  "vertex-deletion property.")
invalid_note = ("The reported witness could not be validated; the refuted "
                "statement would be substantive rather than plainly a typo.")

vertices = frozenset((0, 1, 2, 3, 4))
edges = frozenset(((0, 1), (0, 2), (1, 2),
                   (0, 3), (0, 4), (3, 4)))
k = 2
v = 1
X = frozenset((0, 1))


def components(active):
    unseen = set(active)
    result = []
    while unseen:
        start = min(unseen)
        reached = {start}
        frontier = [start]
        unseen.remove(start)
        while frontier:
            current = frontier.pop()
            for edge in edges:
                if current == edge[0]:
                    neighbor = edge[1]
                elif current == edge[1]:
                    neighbor = edge[0]
                else:
                    continue
                if neighbor in unseen and neighbor in active:
                    unseen.remove(neighbor)
                    reached.add(neighbor)
                    frontier.append(neighbor)
        result.append(frozenset(reached))
    return frozenset(result)


ordered_vertices = tuple(sorted(vertices))
cut_sizes = []
for mask in range(1, 1 << len(ordered_vertices)):
    side = frozenset(
        ordered_vertices[index]
        for index in range(len(ordered_vertices))
        if mask & (1 << index)
    )
    if side == vertices:
        continue
    boundary = sum(
        1 for a, b in edges if (a in side) != (b in side)
    )
    cut_sizes.append(boundary)

simple_graph = (
    all(a in vertices and b in vertices and a != b for a, b in edges)
    and len(edges) == 6
)
edge_connectivity = min(cut_sizes)
deleted = X.difference((v,))
remaining_components = components(vertices.difference(deleted))
expected_components = frozenset((frozenset((1, 2)), frozenset((3, 4))))
valid = (
    simple_graph
    and v in X
    and len(deleted) == k - 1
    and edge_connectivity == k
    and components(vertices) == frozenset((vertices,))
    and remaining_components == expected_components
)

if valid:
    verdict = "CONFIRMED"
    notes = confirmed_note
else:
    verdict = "REFUTED_WITNESS_INVALID"
    notes = invalid_note

print(json.dumps({"record_id": record_id, "verdict": verdict, "notes": notes}))
