r"""Let $G$ be a triangle free graph. Then center of  $G$ has atmost two vertices."""

import json
from collections import deque

record_id = "SE_math_2371897__q"
confirmed_notes = (
    "The witness is valid: it is a connected triangle-free 4-cycle, every "
    "vertex has eccentricity 2, and hence all four vertices lie in its center. "
    "The refutation is substantive, not merely a typo (although “atmost” is "
    "misspelled)."
)
invalid_notes = "The reported witness could not be independently validated."

vertices = (0, 1, 2, 3)
edges = ((0, 2), (0, 3), (1, 2), (1, 3))
neighbors = {vertex: set() for vertex in vertices}
well_formed = True

for left, right in edges:
    if left not in neighbors or right not in neighbors or left == right:
        well_formed = False
    else:
        neighbors[left].add(right)
        neighbors[right].add(left)

if sum(len(adjacent) for adjacent in neighbors.values()) != 2 * len(edges):
    well_formed = False

triangle_free = True
for first in vertices:
    for second in vertices:
        for third in vertices:
            if first < second < third:
                if (second in neighbors[first] and
                        third in neighbors[first] and
                        third in neighbors[second]):
                    triangle_free = False


def shortest_distances(start):
    distances = {start: 0}
    pending = deque((start,))
    while pending:
        current = pending.popleft()
        for adjacent in neighbors[current]:
            if adjacent not in distances:
                distances[adjacent] = distances[current] + 1
                pending.append(adjacent)
    return distances


eccentricities = {}
connected = True
for vertex in vertices:
    distances = shortest_distances(vertex)
    if len(distances) != len(vertices):
        connected = False
    else:
        eccentricities[vertex] = max(distances.values())

center = ()
if connected:
    radius = min(eccentricities.values())
    center = tuple(vertex for vertex in vertices
                   if eccentricities[vertex] == radius)

valid = (
    well_formed
    and triangle_free
    and connected
    and eccentricities == {0: 2, 1: 2, 2: 2, 3: 2}
    and center == vertices
    and len(center) > 2
)

result = {
    "record_id": record_id,
    "verdict": "CONFIRMED" if valid else "REFUTED_WITNESS_INVALID",
    "notes": confirmed_notes if valid else invalid_notes,
}
print(json.dumps(result, ensure_ascii=False, separators=(",", ":")))
