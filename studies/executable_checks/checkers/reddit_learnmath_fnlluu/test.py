"""For every integer n ≥ 1, the sum of the squares from 1 through n equals n(n+1)(n+2)/6."""

import json
from fractions import Fraction


def main():
    counterexamples = []
    for n in range(1, 1001):
        left = sum(k * k for k in range(1, n + 1))
        right = Fraction(n * (n + 1) * (n + 2), 6)
        if Fraction(left, 1) != right:
            counterexamples.append((n, left, right))

    first_n, first_left, first_right = counterexamples[0]
    if (first_n, first_left, first_right) != (2, 5, Fraction(4, 1)):
        raise AssertionError("unexpected first counterexample")

    result = {
        "record_id": "reddit_learnmath_fnlluu",
        "outcome": "WITNESS_FOUND",
        "witness_description": "n = 2: the sum of squares is 1^2 + 2^2 = 5, while n(n+1)(n+2)/6 = 2·3·4/6 = 4.",
        "refutation_explanation": "The universal claim is false because at n = 2 its left-hand side equals 5 and its right-hand side equals 4, and 5 is not equal to 4.",
        "search_space": "All integers n from 1 through 1000 inclusive, checked in increasing order using exact integer and Fraction arithmetic."
    }
    print(json.dumps(result, ensure_ascii=False, separators=(",", ":")))


if __name__ == "__main__":
    main()
