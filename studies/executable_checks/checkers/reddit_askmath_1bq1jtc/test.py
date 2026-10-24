"""The asserted factorization 6q + 2 = 2(3q + 2) is valid for integers q."""

import json


def main():
    search_values = tuple(range(-2, 3))
    witnesses = []
    for q in search_values:
        left = 6 * q + 2
        right = 2 * (3 * q + 2)
        if left != right:
            witnesses.append((q, left, right))

    q, left, right = witnesses[0]
    result = {
        "record_id": "reddit_askmath_1bq1jtc",
        "outcome": "WITNESS_FOUND",
        "witness_description": "q = -2 is an integer; 6q + 2 = -10, while 2(3q + 2) = -8.",
        "refutation_explanation": "The two sides differ at q = -2, so the asserted identity is not valid for all integers q.",
        "search_space": "All integers q in the bounded set {-2, -1, 0, 1, 2}, checked in increasing order using exact integer arithmetic."
    }
    assert (q, left, right) == (-2, -10, -8)
    print(json.dumps(result, separators=(",", ":"), sort_keys=False))


if __name__ == "__main__":
    main()
