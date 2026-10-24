r"""The lower bound comes from the fact that the resistance is at least the graph distance (Manhattan distance) divided by the maximum degree"""

import json
from fractions import Fraction

REPORT = {
    "record_id": "Algorithms_8__sol5",
    "verdict": "CONFIRMED",
    "notes": "Exact recomputation on Q_3 gives unit-current effective resistance 5/6, while graph distance divided by maximum degree is 3/3 = 1. The refuted statement is substantive, not plainly a typo.",
}

vertices = tuple(
    (first, second, third)
    for first in range(2)
    for second in range(2)
    for third in range(2)
)
source = (0, 0, 0)
sink = (1, 1, 1)

adjacency = {
    vertex: tuple(
        other
        for other in vertices
        if sum(
            coordinate != other_coordinate
            for coordinate, other_coordinate in zip(vertex, other)
        ) == 1
    )
    for vertex in vertices
}

maximum_degree = max(len(adjacency[vertex]) for vertex in vertices)
assert maximum_degree == 3
assert all(len(adjacency[vertex]) == 3 for vertex in vertices)

# Recompute graph distance by an exact breadth-first traversal.
distances = {source: 0}
queue = [source]
position = 0
while position < len(queue):
    vertex = queue[position]
    position += 1
    for neighbor in adjacency[vertex]:
        if neighbor not in distances:
            distances[neighbor] = distances[vertex] + 1
            queue.append(neighbor)

assert len(distances) == len(vertices)
distance = distances[sink]
assert distance == 3

# Cube symmetries make vertices of equal Hamming weight equipotential.
# Count the unit-conductance edges crossing each successive weight layer.
weight = {vertex: sum(vertex) for vertex in vertices}
crossing_counts = tuple(
    sum(
        1
        for vertex in vertices
        for neighbor in adjacency[vertex]
        if weight[vertex] == level and weight[neighbor] == level + 1
    )
    for level in range(3)
)
assert crossing_counts == (3, 6, 3)

# With one unit of current, each layer-to-layer voltage drop is the
# reciprocal of its crossing-edge count. Build the resulting potentials.
layer_potential = [Fraction(0, 1) for _ in range(4)]
for level in range(2, -1, -1):
    layer_potential[level] = (
        layer_potential[level + 1] + Fraction(1, crossing_counts[level])
    )
potential = {vertex: layer_potential[weight[vertex]] for vertex in vertices}

# Independently verify Kirchhoff's equations at every vertex. Since the graph
# is connected, this unit-current solution uniquely determines resistance.
net_current = {
    vertex: sum(
        (potential[vertex] - potential[neighbor] for neighbor in adjacency[vertex]),
        Fraction(0, 1),
    )
    for vertex in vertices
}
for vertex in vertices:
    expected = Fraction(0, 1)
    if vertex == source:
        expected = Fraction(1, 1)
    elif vertex == sink:
        expected = Fraction(-1, 1)
    assert net_current[vertex] == expected

resistance = potential[source] - potential[sink]
claimed_lower_bound = Fraction(distance, maximum_degree)
assert resistance == Fraction(5, 6)
assert claimed_lower_bound == Fraction(1, 1)
assert resistance < claimed_lower_bound

print(json.dumps(REPORT, separators=(",", ":")))
