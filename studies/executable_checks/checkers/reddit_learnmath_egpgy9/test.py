"""A quadrilateral with all four sides equal must be a square."""

import json
from itertools import permutations

RECORD_ID = "reddit_learnmath_egpgy9"
OUTCOME = "WITNESS_FOUND"
WITNESS_DESCRIPTION = (
    "The ordered vertices (-2, 0), (0, -1), (2, 0), (0, 1) form a convex "
    "quadrilateral whose four side-length squares are all 5."
)
REFUTATION_EXPLANATION = (
    "At the first vertex, the adjacent side vectors are (2, -1) and (2, 1), "
    "whose dot product is 3 rather than 0. Thus this equal-sided quadrilateral "
    "has a non-right angle and is not a square, contradicting the claim."
)
SEARCH_SPACE = (
    "All 303600 ordered quadruples of distinct lattice points in [-2,2] x "
    "[-2,2] were examined in fixed lexicographic permutation order; strictly "
    "convex quadruples were tested for four equal squared side lengths and four "
    "right angles."
)
KNOWN_WITNESS = ((-2, 0), (0, -1), (2, 0), (0, 1))


def subtract(a, b):
    return (a[0] - b[0], a[1] - b[1])


def squared_length(vector):
    return vector[0] * vector[0] + vector[1] * vector[1]


def dot(a, b):
    return a[0] * b[0] + a[1] * b[1]


def cross(a, b):
    return a[0] * b[1] - a[1] * b[0]


def side_vectors(vertices):
    return tuple(
        subtract(vertices[(index + 1) % 4], vertices[index])
        for index in range(4)
    )


def is_strictly_convex(vertices):
    sides = side_vectors(vertices)
    turns = tuple(cross(sides[index], sides[(index + 1) % 4]) for index in range(4))
    return all(turn > 0 for turn in turns) or all(turn < 0 for turn in turns)


def has_four_equal_sides(vertices):
    lengths = tuple(squared_length(side) for side in side_vectors(vertices))
    return lengths[0] > 0 and all(length == lengths[0] for length in lengths[1:])


def is_square(vertices):
    sides = side_vectors(vertices)
    return has_four_equal_sides(vertices) and all(
        dot(sides[index], sides[(index + 1) % 4]) == 0
        for index in range(4)
    )


def main():
    points = tuple((x, y) for x in range(-2, 3) for y in range(-2, 3))
    examined = 0
    witness_seen = False
    counterexample_seen = False

    for vertices in permutations(points, 4):
        examined += 1
        if not is_strictly_convex(vertices):
            continue
        if has_four_equal_sides(vertices) and not is_square(vertices):
            counterexample_seen = True
            if vertices == KNOWN_WITNESS:
                witness_seen = True

    assert examined == 303600
    assert counterexample_seen
    assert witness_seen

    result = {
        "record_id": RECORD_ID,
        "outcome": OUTCOME,
        "witness_description": WITNESS_DESCRIPTION,
        "refutation_explanation": REFUTATION_EXPLANATION,
        "search_space": SEARCH_SPACE,
    }
    print(json.dumps(result, sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    main()
