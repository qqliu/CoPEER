"""If u divides mn and gcd(u,m)=1, then m=±1."""

import itertools
import json
import math


def main():
    values = (2, 3)
    counterexamples = []

    for u, m, n in itertools.product(values, repeat=3):
        if (m * n) % u == 0 and math.gcd(u, m) == 1 and m not in (-1, 1):
            counterexamples.append((u, m, n))

    witness = counterexamples[0]
    assert witness == (2, 3, 2)

    result = {
        "record_id": "reddit_learnmath_a2vtxz",
        "outcome": "WITNESS_FOUND",
        "witness_description": "u=2, m=3, n=2.",
        "refutation_explanation": "2 divides 3*2=6 and gcd(2,3)=1, but m=3 is neither 1 nor -1.",
        "search_space": "All 8 ordered integer triples (u,m,n) in {2,3}^3, checked in itertools.product order.",
    }
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
