r"""Lemma 1. Any n-dimensional simplex contained in [0, 1]n contains at least one integer point from {0, 1}n"""

import json
from fractions import Fraction
from itertools import combinations

REPORT = {
    "record_id": "Algorithms_42__sol3",
    "outcome": "WITNESS_FOUND",
    "witness_description": "Witness: n=1 and the 1-simplex [1/3, 2/3]. Its endpoints are rational grid points, it has positive length, and it is contained in [0, 1].",
    "refutation_explanation": "The only points of {0, 1} in dimension 1 are 0 and 1; neither lies in [1/3, 2/3], so this contained 1-dimensional simplex has no required integer point.",
    "search_space": "All 6 nondegenerate closed intervals with distinct endpoints chosen from the ordered grid {0, 1/3, 2/3, 1}, tested in lexicographic endpoint order.",
}

grid = tuple(Fraction(k, 3) for k in range(4))
integer_points = (Fraction(0), Fraction(1))
candidates = list(combinations(grid, 2))
searched = []
violations = []

for left, right in candidates:
    searched.append((left, right))
    assert Fraction(0) <= left < right <= Fraction(1)
    contains_integer_point = any(
        left <= point <= right for point in integer_points
    )
    if not contains_integer_point:
        violations.append((left, right))

assert searched == candidates
assert violations
first_witness = violations[0]
assert first_witness == (Fraction(1, 3), Fraction(2, 3))
assert all(
    not (first_witness[0] <= point <= first_witness[1])
    for point in integer_points
)
assert REPORT["outcome"] == "WITNESS_FOUND"

print(json.dumps(REPORT))
