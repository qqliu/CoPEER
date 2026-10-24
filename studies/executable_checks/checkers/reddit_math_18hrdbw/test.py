"""For every positive integer n, the sum 1^2+2^2+...+n^2 equals n(n+1)/2."""

import json


def main():
    counterexamples = []
    for n in range(1, 101):
        left = sum(k * k for k in range(1, n + 1))
        right = n * (n + 1) // 2
        if left != right:
            counterexamples.append((n, left, right))

    first = counterexamples[0]
    assert first == (2, 5, 3)

    result = {
        "record_id": "reddit_math_18hrdbw",
        "outcome": "WITNESS_FOUND",
        "witness_description": "n = 2: 1^2 + 2^2 = 5, while 2(2+1)/2 = 3.",
        "refutation_explanation": "The universal claim is false because n = 2 is a positive integer and its two sides are unequal (5 != 3).",
        "search_space": "All positive integers n with 1 <= n <= 100, checked in increasing order using exact integer arithmetic."
    }
    print(json.dumps(result))


if __name__ == "__main__":
    main()
