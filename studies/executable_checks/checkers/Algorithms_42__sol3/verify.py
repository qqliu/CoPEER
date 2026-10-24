r"""Lemma 1. Any n-dimensional simplex contained in [0, 1]n contains at least one integer point from {0, 1}n"""

import json

REPORT = {
    "record_id": "Algorithms_42__sol3",
    "verdict": "CONFIRMED",
    "notes": "Exact integer cross-multiplication confirms a substantive failure, not merely a typo: the 1-simplex [1/3, 2/3] lies in [0, 1] and contains neither Boolean point 0 nor 1.",
}


def compare_rationals(first, second):
    first_numerator, first_denominator = first
    second_numerator, second_denominator = second
    assert first_denominator > 0
    assert second_denominator > 0
    return first_numerator * second_denominator - second_numerator * first_denominator


def is_at_most(first, second):
    return compare_rationals(first, second) <= 0


dimension = 1
vertices = ((1, 3), (2, 3))
zero = (0, 1)
one = (1, 1)

assert len(vertices) == dimension + 1
assert compare_rationals(vertices[0], vertices[1]) < 0
assert is_at_most(zero, vertices[0])
assert is_at_most(vertices[1], one)

boolean_points = tuple((coordinate,) for coordinate in range(2))
assert boolean_points == ((0,), (1,))


def belongs_to_closed_simplex(point):
    coordinate = (point[0], 1)
    return is_at_most(vertices[0], coordinate) and is_at_most(coordinate, vertices[1])


contained_boolean_points = tuple(
    point for point in boolean_points if belongs_to_closed_simplex(point)
)
assert contained_boolean_points == ()
assert REPORT["verdict"] == "CONFIRMED"

print(json.dumps(REPORT))
