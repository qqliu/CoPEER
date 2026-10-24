r"""A planar graph is outerplanar if and only if its dual is a forest. Since G is not outerplanar, Gcontains a cycle C."""

import json
from functools import cmp_to_key

REPORT = {
    "record_id": "Graph Theory_10__sol3",
    "verdict": "CONFIRMED",
    "notes": "Confirmed independently: the square with diagonal 02 has a crossing-free embedding with all four vertices on its outer face, while its full planar dual simplifies to a triangle and therefore is not a forest. Thus the biconditional fails. This is a substantive mathematical error as written, not merely the visible spacing typo in 'Gcontains' (it may reflect omission of 'weak' before 'dual')."
}

points = ((0, 0), (2, 0), (2, 2), (0, 2))
vertices = tuple(range(len(points)))
edges = ((0, 1), (0, 2), (0, 3), (1, 2), (2, 3))


def orientation(a, b, c):
    return ((b[0] - a[0]) * (c[1] - a[1])
            - (b[1] - a[1]) * (c[0] - a[0]))


def on_segment(a, b, p):
    return (min(a[0], b[0]) <= p[0] <= max(a[0], b[0])
            and min(a[1], b[1]) <= p[1] <= max(a[1], b[1]))


def segments_intersect(first, second):
    a, b = points[first[0]], points[first[1]]
    c, d = points[second[0]], points[second[1]]
    ac = orientation(a, b, c)
    ad = orientation(a, b, d)
    ca = orientation(c, d, a)
    cb = orientation(c, d, b)
    if ac == 0 and on_segment(a, b, c):
        return True
    if ad == 0 and on_segment(a, b, d):
        return True
    if ca == 0 and on_segment(c, d, a):
        return True
    if cb == 0 and on_segment(c, d, b):
        return True
    return ((ac < 0 < ad or ad < 0 < ac)
            and (ca < 0 < cb or cb < 0 < ca))


crossing_free = True
for first_index in range(len(edges)):
    for second_index in range(first_index + 1, len(edges)):
        first = edges[first_index]
        second = edges[second_index]
        if set(first).isdisjoint(second) and segments_intersect(first, second):
            crossing_free = False
assert crossing_free


def turn(first, second, third):
    return orientation(points[first], points[second], points[third])


def half_hull(sequence):
    result = []
    for vertex in sequence:
        while len(result) >= 2 and turn(result[-2], result[-1], vertex) <= 0:
            result.pop()
        result.append(vertex)
    return result


ordered = tuple(sorted(vertices, key=lambda v: (points[v][0], points[v][1])))
lower = half_hull(ordered)
upper = half_hull(tuple(reversed(ordered)))
hull = tuple(lower[:-1] + upper[:-1])
assert len(hull) == len(vertices)
assert set(hull) == set(vertices)

neighbors = [set() for vertex in vertices]
for u, v in edges:
    assert u < v
    neighbors[u].add(v)
    neighbors[v].add(u)


def direction(origin, neighbor):
    return (points[neighbor][0] - points[origin][0],
            points[neighbor][1] - points[origin][1], neighbor)


def vector_half(vector):
    return 0 if vector[1] > 0 or (vector[1] == 0 and vector[0] >= 0) else 1


def compare_vectors(left, right):
    left_half = vector_half(left)
    right_half = vector_half(right)
    if left_half != right_half:
        return -1 if left_half < right_half else 1
    determinant = left[0] * right[1] - left[1] * right[0]
    if determinant != 0:
        return -1 if determinant > 0 else 1
    left_length = left[0] * left[0] + left[1] * left[1]
    right_length = right[0] * right[0] + right[1] * right[1]
    if left_length != right_length:
        return -1 if left_length < right_length else 1
    return -1 if left[2] < right[2] else (1 if left[2] > right[2] else 0)


rotation = []
for vertex in vertices:
    vectors = [direction(vertex, neighbor) for neighbor in neighbors[vertex]]
    vectors.sort(key=cmp_to_key(compare_vectors))
    rotation.append(tuple(vector[2] for vector in vectors))

unseen = set()
for u, v in edges:
    unseen.add((u, v))
    unseen.add((v, u))

faces = []
dart_face = dict()
while unseen:
    start = min(unseen)
    dart = start
    boundary = []
    while True:
        assert dart in unseen
        unseen.remove(dart)
        u, v = dart
        boundary.append(dart)
        dart_face[dart] = len(faces)
        cyclic_neighbors = rotation[v]
        incoming_index = cyclic_neighbors.index(u)
        next_vertex = cyclic_neighbors[(incoming_index - 1) % len(cyclic_neighbors)]
        dart = (v, next_vertex)
        if dart == start:
            break
        assert len(boundary) <= 2 * len(edges)
    faces.append(tuple(boundary))

assert len(dart_face) == 2 * len(edges)
assert len(vertices) - len(edges) + len(faces) == 2


def face_area_twice(face):
    total = 0
    for index in range(len(face)):
        vertex = face[index][0]
        next_vertex = face[(index + 1) % len(face)][0]
        total += (points[vertex][0] * points[next_vertex][1]
                  - points[vertex][1] * points[next_vertex][0])
    return total


areas = tuple(face_area_twice(face) for face in faces)
assert tuple(sorted(areas)) == (-8, 4, 4)
outer_face = areas.index(min(areas))
outer_vertices = set(dart[0] for dart in faces[outer_face])
all_on_outer_face = outer_vertices == set(vertices)
assert all_on_outer_face

dual_occurrences = []
for u, v in edges:
    first_face = dart_face[(u, v)]
    second_face = dart_face[(v, u)]
    assert first_face != second_face
    dual_occurrences.append(tuple(sorted((first_face, second_face))))

assert len(dual_occurrences) == len(edges)
simple_dual = tuple(sorted(set(dual_occurrences)))
assert len(faces) == 3
assert simple_dual == ((0, 1), (0, 2), (1, 2))


def contains_cycle(vertex_count, graph_edges):
    parent = list(range(vertex_count))

    def root(vertex):
        while parent[vertex] != vertex:
            parent[vertex] = parent[parent[vertex]]
            vertex = parent[vertex]
        return vertex

    for u, v in graph_edges:
        first_root = root(u)
        second_root = root(v)
        if first_root == second_root:
            return True
        parent[second_root] = first_root
    return False


dual_has_cycle = contains_cycle(len(faces), simple_dual)
assert dual_has_cycle
counterexample_established = crossing_free and all_on_outer_face and dual_has_cycle
assert counterexample_established
assert REPORT["record_id"] == "Graph Theory_10__sol3"
assert REPORT["verdict"] == ("CONFIRMED" if counterexample_established else "REFUTED_WITNESS_INVALID")

print(json.dumps(REPORT, separators=(",", ":")))
