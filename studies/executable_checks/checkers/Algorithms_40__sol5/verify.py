"""For the remaining edges in M1 (those in alternating paths or cycles), the
number is at most |M2| (since in each component, the number of M1 edges is
at most the number of M2 edges plus one, and summing over all components
gives at most |M2|)."""

import json


def matching(edge_set):
    incident = set()
    for edge in edge_set:
        if len(edge) != 2:
            return False
        left, right = tuple(edge)
        if left == right or left in incident or right in incident:
            return False
        incident.update((left, right))
    return True


def main():
    ordered_path = (
        frozenset(("v0", "v1")),
        frozenset(("v1", "v2")),
        frozenset(("v2", "v3")),
    )
    m1 = {ordered_path[0], ordered_path[2]}
    m2 = {ordered_path[1]}

    vertices = set().union(*ordered_path)
    adjacency = {vertex: set() for vertex in vertices}
    for edge in ordered_path:
        left, right = tuple(edge)
        adjacency[left].add(right)
        adjacency[right].add(left)

    reached = set()
    pending = ["v0"]
    while pending:
        vertex = pending.pop()
        if vertex not in reached:
            reached.add(vertex)
            pending.extend(adjacency[vertex] - reached)

    labels = []
    for edge in ordered_path:
        in_first = edge in m1
        in_second = edge in m2
        if in_first == in_second:
            raise AssertionError("each path edge must belong to exactly one matching")
        labels.append(1 if in_first else 2)

    degrees = sorted(len(neighbors) for neighbors in adjacency.values())
    checks = (
        len(vertices) == 4,
        len(ordered_path) == 3,
        reached == vertices,
        degrees == [1, 1, 2, 2],
        matching(m1),
        matching(m2),
        labels == [1, 2, 1],
        all(labels[index] != labels[index + 1] for index in range(len(labels) - 1)),
    )
    if not all(checks):
        raise AssertionError("reported construction is not an alternating path of matchings")

    remaining_m1 = sum(1 for edge in ordered_path if edge in m1)
    m2_size = len(m2)
    if remaining_m1 != 2 or m2_size != 1 or not remaining_m1 > m2_size:
        raise AssertionError("reported inequality violation was not reproduced")
    if not remaining_m1 <= m2_size + 1:
        raise AssertionError("componentwise premise was not satisfied")

    result = {
        "record_id": "Algorithms_40__sol5",
        "verdict": "CONFIRMED",
        "notes": "The witness is valid. The refuted statement is substantive, not plainly a typo: one alternating path can contain one more M1 edge than M2 edges, so summing the componentwise bounds does not imply a global bound of |M2|.",
    }
    print(json.dumps(result, separators=(",", ":")))


if __name__ == "__main__":
    main()
