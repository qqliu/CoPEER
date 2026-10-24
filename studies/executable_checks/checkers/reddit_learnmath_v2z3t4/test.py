"""The recursive algorithm outputs a quotient q satisfying qd <= n < (q+1)d."""

import json


def quotient(n, d):
    if n < d:
        return 0
    return 1 + quotient(n - 1, d)


def main():
    witnesses = []
    for n in range(33):
        for d in range(1, 17):
            q = quotient(n, d)
            if not (q * d <= n < (q + 1) * d):
                witnesses.append((n, d, q))

    if not witnesses or witnesses[0] != (3, 2, 2):
        raise AssertionError("unexpected exhaustive-search result")

    result = {
        "record_id": "reddit_learnmath_v2z3t4",
        "outcome": "WITNESS_FOUND",
        "witness_description": "n = 3, d = 2, q = 2.",
        "refutation_explanation": "The stated recursion gives q(3,2) = 1 + q(2,2) = 2, because q(2,2) = 1 + q(1,2) = 1. The required lower bound fails: qd = 4 is not <= n = 3.",
        "search_space": "All 528 ordered pairs (n,d) with n in {0,...,32} and d in {1,...,16}, evaluated in fixed lexicographic (n,d) order using the stated recursion; every pair was swept."
    }
    print(json.dumps(result, separators=(",", ":")))


if __name__ == "__main__":
    main()
