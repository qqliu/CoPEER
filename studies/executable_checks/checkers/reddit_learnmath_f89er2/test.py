"""For all integers p and n, if p divides n^2 then p divides n."""

import json


def divides(divisor, value):
    return value % divisor == 0


def main():
    counterexamples = []
    for p in range(1, 5):
        for n in range(0, 5):
            if divides(p, n * n) and not divides(p, n):
                counterexamples.append((p, n))

    assert counterexamples
    assert counterexamples[0] == (4, 2)

    result = {
        "record_id": "reddit_learnmath_f89er2",
        "outcome": "WITNESS_FOUND",
        "witness_description": "p = 4, n = 2.",
        "refutation_explanation": "4 divides 2^2 = 4, but 4 does not divide 2.",
        "search_space": "All 20 ordered pairs (p, n) with p in {1, 2, 3, 4} and n in {0, 1, 2, 3, 4}.",
    }
    print(json.dumps(result, separators=(",", ":")))


if __name__ == "__main__":
    main()
