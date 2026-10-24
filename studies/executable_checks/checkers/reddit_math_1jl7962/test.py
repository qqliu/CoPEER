"""For real x and y such that sqrt(xy) is defined, sqrt(xy) is less than or equal to (x+y)/2."""

import json
from fractions import Fraction
from itertools import product


def violates_claim(x, y):
    product_xy = x * y
    if product_xy < 0:
        return False
    right_side = Fraction(x + y, 2)
    if right_side < 0:
        return True
    return Fraction(product_xy, 1) > right_side * right_side


def main():
    values = (-1, 0, 1)
    witnesses = []
    visited = 0
    domain_valid = 0

    for x, y in product(values, repeat=2):
        visited += 1
        if x * y >= 0:
            domain_valid += 1
            if violates_claim(x, y):
                witnesses.append((x, y))

    assert visited == 9
    assert domain_valid == 7
    assert witnesses[0] == (-1, -1)

    result = {
        "record_id": "reddit_math_1jl7962",
        "outcome": "WITNESS_FOUND",
        "witness_description": "x = -1 and y = -1.",
        "refutation_explanation": "Here xy = 1, so sqrt(xy) is defined and equals 1, while (x+y)/2 = -1. Thus the claimed inequality would require 1 <= -1, which is false.",
        "search_space": "All 9 ordered integer pairs (x, y) in {-1, 0, 1}^2 were visited in lexicographic product order; the inequality was tested on all 7 pairs satisfying xy >= 0."
    }
    print(json.dumps(result, separators=(",", ":")))


if __name__ == "__main__":
    main()
