"""Every prescribed finite system of pairwise distances is realizable in some Euclidean dimension."""

import itertools
import json


RECORD_ID = "reddit_math_1akxj1h"
OUTCOME = "WITNESS_FOUND"
WITNESS_DESCRIPTION = (
    "Three labeled points 0, 1, 2 with d(0,1)=1, d(0,2)=1, "
    "and d(1,2)=3."
)
REFUTATION_EXPLANATION = (
    "Every Euclidean distance satisfies the triangle inequality, but this "
    "assignment requires d(1,2)=3 > d(1,0)+d(0,2)=1+1. Hence it is "
    "unrealizable in every Euclidean dimension and refutes the universal claim."
)
SEARCH_SPACE = (
    "All 27 assignments (d(0,1), d(0,2), d(1,2)) in {1,2,3}^3, "
    "swept in lexicographic product order."
)


def violates_triangle_inequality(distances):
    d01, d02, d12 = distances
    return d01 + d02 < d12 or d01 + d12 < d02 or d02 + d12 < d01


def main():
    counterexamples = []
    for distances in itertools.product(range(1, 4), repeat=3):
        if violates_triangle_inequality(distances):
            counterexamples.append(distances)

    assert counterexamples
    assert counterexamples[0] == (1, 1, 3)

    result = {
        "record_id": RECORD_ID,
        "outcome": OUTCOME,
        "witness_description": WITNESS_DESCRIPTION,
        "refutation_explanation": REFUTATION_EXPLANATION,
        "search_space": SEARCH_SPACE,
    }
    print(json.dumps(result, separators=(",", ":")))


if __name__ == "__main__":
    main()
