"""From (a - b)^2 = (b - a)^2, taking square roots implies a - b = b - a."""

import json
from itertools import product


def main():
    values = range(-2, 3)
    witness = None

    for a, b in product(values, repeat=2):
        left = a - b
        right = b - a
        if left * left == right * right and left != right and witness is None:
            witness = (a, b, left, right)

    if witness != (-2, -1, -1, 1):
        raise AssertionError("unexpected exhaustive-search result")

    result = {
        "record_id": "reddit_mathematics_175i5j2",
        "outcome": "WITNESS_FOUND",
        "witness_description": "a = -2 and b = -1: (a - b)^2 = 1 = (b - a)^2, but a - b = -1 while b - a = 1.",
        "refutation_explanation": "The equality of the squares does not imply equality of their bases. This witness satisfies the stated premise but violates the claimed conclusion.",
        "search_space": "All 25 ordered integer pairs (a, b) in {-2, -1, 0, 1, 2} x {-2, -1, 0, 1, 2}, checked in lexicographic order."
    }
    print(json.dumps(result, separators=(",", ":")))


if __name__ == "__main__":
    main()
