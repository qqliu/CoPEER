"""Lemma 5's asserted identity holds for all positive integers k, interpreting the displayed notation as powers of 2."""

import json


def sides(k):
    left = 2 ** (2 ** k) - 1
    previous = 2 ** (2 ** (k - 1)) - 1
    right = previous * (2 ** k) + previous
    return left, right


def main():
    violations = []
    for k in range(1, 11):
        left, right = sides(k)
        if left != right:
            violations.append((k, left, right))

    assert violations
    assert violations[0] == (3, 255, 135)

    result = {
        "record_id": "reddit_mathematics_2xwqaj",
        "outcome": "WITNESS_FOUND",
        "witness_description": "k = 3: interpreting 22k as 2^(2^k), the left side is 2^(2^3) - 1 = 255, while the right side is (2^(2^(3-1)) - 1) * 2^3 + (2^(2^(3-1)) - 1) = 15 * 8 + 15 = 135.",
        "refutation_explanation": "The asserted universal identity fails because 255 != 135 at the positive integer k = 3.",
        "search_space": "All positive integers k from 1 through 10 inclusive, checked in increasing order under the interpretation 22k = 2^(2^k), 22(k-1) = 2^(2^(k-1)), and 2k = 2^k."
    }
    print(json.dumps(result, separators=(",", ":")))


if __name__ == "__main__":
    main()
