"""Every even integer a can be written as a=2n for some positive integer n."""

import json


def is_representable(a):
    n = a // 2
    return n > 0 and 2 * n == a


def main():
    counterexamples = []
    for a in range(-4, 5):
        if a % 2 == 0 and not is_representable(a):
            counterexamples.append(a)

    witness = counterexamples[0]
    result = {
        "record_id": "reddit_askmath_21hl35",
        "outcome": "WITNESS_FOUND",
        "witness_description": "a = -4 is an even integer, but there is no positive integer n such that -4 = 2n.",
        "refutation_explanation": "If n is a positive integer, then 2n is positive, whereas -4 is negative. Thus the even integer a = -4 violates the universal claim.",
        "search_space": "All integers a from -4 through 4 inclusive (9 integers), in increasing order; for each even a, the unique possible n = a // 2 was checked exactly for positivity and the equality 2*n = a."
    }
    assert witness == -4
    print(json.dumps(result, separators=(",", ":")))


if __name__ == "__main__":
    main()
