"""The set of valid nonzero radii must have a positive lower bound because no valid radius equals zero."""

import json
from fractions import Fraction
from itertools import combinations

RECORD_ID = "reddit_learnmath_1mmagfb"
WITNESS_DESCRIPTION = (
    "No witness can be certified because the quote never defines the condition "
    "that makes a radius valid."
)
REFUTATION_EXPLANATION = (
    "Every candidate in the bounded sweep is finite and therefore has a positive "
    "minimum. This cannot decide the claim for the unspecified set of valid radii, "
    "which could be infinite."
)
SEARCH_SPACE = (
    "All 511 nonempty subsets of the exact rational grid {1/d : d is an integer "
    "from 1 through 9}, enumerated by increasing subset size and "
    "itertools.combinations order."
)


def main():
    grid = tuple(Fraction(1, denominator) for denominator in range(1, 10))
    swept = 0

    for subset_size in range(1, len(grid) + 1):
        for candidate in combinations(grid, subset_size):
            swept += 1
            assert all(radius != 0 for radius in candidate)
            lower_bound = min(candidate)
            assert lower_bound > 0
            assert all(lower_bound <= radius for radius in candidate)

    assert swept == 511
    result = {
        "record_id": RECORD_ID,
        "outcome": "NO_WITNESS_INCONCLUSIVE",
        "witness_description": WITNESS_DESCRIPTION,
        "refutation_explanation": REFUTATION_EXPLANATION,
        "search_space": SEARCH_SPACE,
    }
    print(json.dumps(result, separators=(",", ":")))


if __name__ == "__main__":
    main()
