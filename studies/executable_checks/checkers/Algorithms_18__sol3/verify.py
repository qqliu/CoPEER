r"""Suppose G = (V, E) is a connected graph with weighted edges. Establish that for any cycle in G, the maximum-weight edge of that cycle is not included in the minimum spanning tree of G."""

import json

REPORT = {
    "record_id": "Algorithms_18__sol3",
    "verdict": "CONFIRMED",
    "notes": "The refuted statement is substantive, not plainly a typo: tied maximum-weight cycle edges can belong to an MST, so a unique or strict maximum hypothesis is missing.",
}

vertices = (0, 1, 2)
edges = ((0, 1), (0, 2), (1, 2))
weights = {
    (0, 1): 1,
    (0, 2): 1,
    (1, 2): 1,
}
reported_tree = frozenset(((0, 1), (0, 2)))
reported_maximum_edge = (0, 1)


def connected(chosen):
    reached = {vertices[0]}
    frontier = [vertices[0]]
    while frontier:
        current = frontier.pop()
        for left, right in chosen:
            if left == current and right not in reached:
                reached.add(right)
                frontier.append(right)
            elif right == current and left not in reached:
                reached.add(left)
                frontier.append(left)
    return reached == set(vertices)


def is_tree(chosen):
    if len(chosen) != len(vertices) - 1:
        return False
    parent = {vertex: vertex for vertex in vertices}

    def root(vertex):
        while parent[vertex] != vertex:
            vertex = parent[vertex]
        return vertex

    for left, right in chosen:
        left_root = root(left)
        right_root = root(right)
        if left_root == right_root:
            return False
        parent[right_root] = left_root
    return connected(chosen)


def total_weight(chosen):
    return sum(weights[edge] for edge in chosen)


assert connected(edges)

cycle_walk = (0, 1, 2, 0)
cycle_edges = []
for index in range(len(cycle_walk) - 1):
    endpoints = (cycle_walk[index], cycle_walk[index + 1])
    if endpoints[0] < endpoints[1]:
        cycle_edges.append(endpoints)
    else:
        cycle_edges.append((endpoints[1], endpoints[0]))
cycle_edges = tuple(cycle_edges)
assert len(set(cycle_walk[:-1])) == 3
assert cycle_walk[0] == cycle_walk[-1]
assert set(cycle_edges) == set(edges)

spanning_trees = []
for mask in range(1 << len(edges)):
    chosen = tuple(
        edges[index]
        for index in range(len(edges))
        if mask & (1 << index)
    )
    if is_tree(chosen):
        spanning_trees.append(frozenset(chosen))

assert len(spanning_trees) == 3
minimum_cost = min(total_weight(tree) for tree in spanning_trees)
minimum_trees = tuple(
    tree for tree in spanning_trees if total_weight(tree) == minimum_cost
)
assert minimum_cost == 2
assert reported_tree in minimum_trees
assert total_weight(reported_tree) == minimum_cost

cycle_maximum = max(weights[edge] for edge in cycle_edges)
maximum_edges = tuple(
    edge for edge in cycle_edges if weights[edge] == cycle_maximum
)
assert cycle_maximum == 1
assert set(maximum_edges) == set(edges)
assert reported_maximum_edge in maximum_edges
assert reported_maximum_edge in reported_tree
assert weights[reported_maximum_edge] == cycle_maximum

print(json.dumps(REPORT))
