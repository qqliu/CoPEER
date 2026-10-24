"""Removing edges on cycles from $G$ doesn't change the number of connected components, because, for each edge $e$ that was removed from $G$, there is a path between the endpoints of $e$ that doesn't include $e$."""

import json


def reachable(vertices, edge_set, source, destination):
    pending = [source]
    visited = {source}
    while pending:
        current = pending.pop()
        if current == destination:
            return True
        for left, right in edge_set:
            if left == current:
                neighbor = right
            elif right == current:
                neighbor = left
            else:
                continue
            if neighbor not in visited:
                visited.add(neighbor)
                pending.append(neighbor)
    return False


def number_of_components(vertices, edge_set):
    unseen = set(vertices)
    total = 0
    while unseen:
        total += 1
        seed = min(unseen)
        pending = [seed]
        unseen.remove(seed)
        while pending:
            current = pending.pop()
            for left, right in edge_set:
                if left == current:
                    neighbor = right
                elif right == current:
                    neighbor = left
                else:
                    continue
                if neighbor in unseen:
                    unseen.remove(neighbor)
                    pending.append(neighbor)
    return total


vertices = frozenset((0, 1, 2))
graph = frozenset(((0, 1), (0, 2), (1, 2)))
deleted = frozenset(((0, 1), (0, 2)))

for edge in deleted:
    remaining_for_this_edge = graph - frozenset((edge,))
    assert reachable(vertices, remaining_for_this_edge, edge[0], edge[1])

before = number_of_components(vertices, graph)
after = number_of_components(vertices, graph - deleted)
assert before == 1
assert after == 2
assert after != before

result = {
    "record_id": "SE_math_3783337__q",
    "verdict": "CONFIRMED",
    "notes": "The triangle witness is valid: each deleted edge individually has an alternate path in the original graph, but deleting both edges isolates vertex 0 and increases the component count from 1 to 2. The refuted statement is substantive, not plainly a typo; its per-edge justification fails for simultaneous deletion because alternate paths may use other deleted edges.",
}
print(json.dumps(result, separators=(",", ":")))
