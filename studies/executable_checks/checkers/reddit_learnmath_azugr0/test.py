"""The equality asserted in line 19 is valid for every allowed natural number k."""

import json
from fractions import Fraction
from math import factorial


def sides(k):
    left = Fraction(k * k + 4 * k + k + 4, k + 1)
    right = Fraction(factorial(k + 2), 2) + Fraction(k * k + 3 * k, k)
    return left, right


def main():
    violations = []
    for k in range(1, 101):
        left, right = sides(k)
        if left != right:
            violations.append((k, left, right))

    witness = violations[0]
    assert witness == (1, Fraction(5, 1), Fraction(7, 1))

    result = {
        "record_id": "reddit_learnmath_azugr0",
        "outcome": "WITNESS_FOUND",
        "witness_description": "k = 1. The left-hand side is 5, while the right-hand side is 7.",
        "refutation_explanation": "At k = 1, both denominators are nonzero and (k+2)! is defined. Exactly, (1^2 + 4*1 + 1 + 4)/(1+1) = 10/2 = 5, whereas (1+2)!/2 + (1^2 + 3*1)/1 = 6/2 + 4 = 7. Thus the asserted universal equality is false.",
        "search_space": "All integer k with 1 <= k <= 100, checked in increasing order using Fraction and exact integer factorials; the entire bounded space was swept."
    }
    print(json.dumps(result, separators=(",", ":")))


if __name__ == "__main__":
    main()
