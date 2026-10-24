"""The inductive-step equality 5^(k+1) − 2^(k+1) = 3^(k+1) holds."""

import json


def main():
    counterexamples = []
    for k in range(0, 101):
        left = 5 ** (k + 1) - 2 ** (k + 1)
        right = 3 ** (k + 1)
        if left != right:
            counterexamples.append((k, left, right))

    assert counterexamples
    k, left, right = counterexamples[0]
    assert (k, left, right) == (1, 21, 9)

    result = {
        "record_id": "reddit_askmath_g7lcfx",
        "outcome": "WITNESS_FOUND",
        "witness_description": "k = 1: 5^(1+1) - 2^(1+1) = 21, while 3^(1+1) = 9.",
        "refutation_explanation": "The two sides are unequal at k = 1 (21 != 9), so the stated equality does not hold for that value.",
        "search_space": "All integers k from 0 through 100 inclusive, checked in increasing order using exact integer arithmetic."
    }
    print(json.dumps(result, sort_keys=False))


if __name__ == "__main__":
    main()
