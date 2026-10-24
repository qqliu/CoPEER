r"""The lower bound comes from the fact that the resistance is at least the graph distance (Manhattan distance) divided by the maximum degree"""

import json
from collections import deque
from fractions import Fraction
from itertools import product

REPORT = {
    "record_id": "Algorithms_8__sol5",
    "outcome": "WITNESS_FOUND",
    "witness_description": "The 3-dimensional hypercube Q_3 with unit-resistance edges, using opposite vertices (0,0,0) and (1,1,1), has effective resistance 5/6, graph distance 3, and maximum degree 3.",
    "refutation_explanation": "For this graph the claimed lower bound is 3/3 = 1, but the effective resistance is 5/6, and 5/6 < 1.",
    "search_space": "All hypercube graphs Q_d with unit-resistance edges for integer dimensions d = 1, 2, 3, testing the two opposite vertices in increasing dimension.",
}


def hypercube(dimension):
    vertices = list(product((0, 1), repeat=dimension))
    indices = {vertex: index for index, vertex in enumerate(vertices)}
    adjacency = []
    for vertex in vertices:
        neighbors = []
        for coordinate in range(dimension):
            changed = (
                vertex[:coordinate]
                + (1 - vertex[coordinate],)
                + vertex[coordinate + 1:]
            )
            neighbors.append(indices[changed])
        adjacency.append(tuple(neighbors))
    return vertices, tuple(adjacency)


def graph_distance(adjacency, source, sink):
    distances = [-1] * len(adjacency)
    distances[source] = 0
    pending = deque((source,))
    while pending:
        vertex = pending.popleft()
        if vertex == sink:
            return distances[vertex]
        for neighbor in adjacency[vertex]:
            if distances[neighbor] == -1:
                distances[neighbor] = distances[vertex] + 1
                pending.append(neighbor)
    raise AssertionError("The tested vertices must be connected")


def solve_exact(matrix, vector):
    size = len(vector)
    augmented = [
        [Fraction(value) for value in matrix[row]] + [Fraction(vector[row])]
        for row in range(size)
    ]
    for column in range(size):
        pivot_row = None
        for row in range(column, size):
            if augmented[row][column] != 0:
                pivot_row = row
                break
        if pivot_row is None:
            raise AssertionError("Singular reduced Laplacian")
        if pivot_row != column:
            augmented[column], augmented[pivot_row] = (
                augmented[pivot_row],
                augmented[column],
            )
        pivot = augmented[column][column]
        reciprocal = Fraction(pivot.denominator, pivot.numerator)
        for entry in range(column, size + 1):
            augmented[column][entry] *= reciprocal
        for row in range(size):
            if row == column:
                continue
            factor = augmented[row][column]
            if factor != 0:
                for entry in range(column, size + 1):
                    augmented[row][entry] -= factor * augmented[column][entry]
    return tuple(augmented[row][size] for row in range(size))


def effective_resistance(adjacency, source, sink):
    unknown_vertices = [
        vertex for vertex in range(len(adjacency)) if vertex != sink
    ]
    positions = {
        vertex: position for position, vertex in enumerate(unknown_vertices)
    }
    size = len(unknown_vertices)
    laplacian = [[0 for _ in range(size)] for _ in range(size)]
    current = [0 for _ in range(size)]
    current[positions[source]] = 1
    for vertex in unknown_vertices:
        row = positions[vertex]
        laplacian[row][row] = len(adjacency[vertex])
        for neighbor in adjacency[vertex]:
            if neighbor != sink:
                laplacian[row][positions[neighbor]] -= 1
    voltages = solve_exact(laplacian, current)
    return voltages[positions[source]]


first_violation = None
for dimension in range(1, 4):
    vertices, adjacency = hypercube(dimension)
    source = vertices.index((0,) * dimension)
    sink = vertices.index((1,) * dimension)
    distance = graph_distance(adjacency, source, sink)
    maximum_degree = max(len(neighbors) for neighbors in adjacency)
    resistance = effective_resistance(adjacency, source, sink)
    claimed_lower_bound = Fraction(distance, maximum_degree)
    if resistance < claimed_lower_bound:
        first_violation = (
            dimension,
            resistance,
            distance,
            maximum_degree,
            claimed_lower_bound,
        )
        break

assert first_violation is not None
assert first_violation == (3, Fraction(5, 6), 3, 3, Fraction(1, 1))
assert REPORT["outcome"] == "WITNESS_FOUND"
assert "5/6" in REPORT["witness_description"]
assert "5/6 < 1" in REPORT["refutation_explanation"]

print(json.dumps(REPORT, separators=(",", ":")))
