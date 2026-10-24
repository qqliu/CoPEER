"""A countable subset of [0,1] with no limit points cannot exist."""

import json
from fractions import Fraction

RECORD_ID = "reddit_askmath_15fli49"
WITNESS_DESCRIPTION = "The singleton set {0} is a countable subset of [0,1] with no limit points."
REFUTATION_EXPLANATION = (
    "Under the standard meaning of countable, finite sets are countable. "
    "For x = 0, every punctured neighborhood contains no member of {0}; "
    "for any x != 0, some sufficiently small neighborhood excludes 0. "
    "Thus no x is a limit point of {0}, contradicting the claim as written."
)
SEARCH_SPACE = (
    "All 4 subsets of the exact rational grid {0, 1}, represented by masks "
    "0 through 3 and swept in increasing mask order."
)


def main():
    grid = (Fraction(0, 1), Fraction(1, 1))
    witnesses = []

    # Exhaustively sweep every subset of the two-point grid. Every finite set
    # is countable and has no limit points; require nonempty candidates so the
    # reported counterexample does not depend on whether empty sets are allowed.
    for mask in range(1 << len(grid)):
        candidate = tuple(
            grid[index]
            for index in range(len(grid))
            if mask & (1 << index)
        )
        is_subset_of_unit_interval = all(
            Fraction(0, 1) <= value <= Fraction(1, 1)
            for value in candidate
        )
        is_countable = True  # Each generated candidate is finite.
        has_no_limit_points = True  # Every finite subset of R has none.
        if candidate and is_subset_of_unit_interval and is_countable and has_no_limit_points:
            witnesses.append(candidate)

    expected = (Fraction(0, 1),)
    if expected not in witnesses:
        raise AssertionError("exhaustive sweep failed to recover {0}")

    result = {
        "record_id": RECORD_ID,
        "outcome": "WITNESS_FOUND",
        "witness_description": WITNESS_DESCRIPTION,
        "refutation_explanation": REFUTATION_EXPLANATION,
        "search_space": SEARCH_SPACE,
    }
    print(json.dumps(result, separators=(",", ":")))


if __name__ == "__main__":
    main()
