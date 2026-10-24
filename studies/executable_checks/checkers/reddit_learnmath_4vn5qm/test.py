"""For every nonzero real number a and every nonnegative integer n, a^n = 1."""

import json
import itertools


def main():
    a_values = (-2, -1, 1, 2)
    n_values = (0, 1, 2)
    violations = []

    for a, n in itertools.product(a_values, n_values):
        if a ** n != 1:
            violations.append((a, n, a ** n))

    first = violations[0]
    assert first == (-2, 1, -2)

    result = {
        "record_id": "reddit_learnmath_4vn5qm",
        "outcome": "WITNESS_FOUND",
        "witness_description": "a = -2 and n = 1.",
        "refutation_explanation": "The searched pair has a nonzero real number a = -2 and a nonnegative integer n = 1, but (-2)^1 = -2, which is not 1.",
        "search_space": "All 12 ordered pairs (a, n) with a in {-2, -1, 1, 2} and n in {0, 1, 2}, checked in ascending lexicographic order."
    }
    print(json.dumps(result))


if __name__ == "__main__":
    main()
