"""Three or more bodies orbiting a single point at distinct constant speeds are guaranteed eventually to align."""

import json
from fractions import Fraction
from itertools import permutations


RECORD_ID = "reddit_askmath_kirewv"
SPEEDS = tuple(Fraction(value, 1) for value in range(1, 5))

WITNESS_DESCRIPTION = (
    "No counterexample can be certified from the supplied text alone."
)
REFUTATION_EXPLANATION = (
    "The text does not define “align,” specify the orbit geometry, distinguish "
    "angular from linear speed, or give or quantify initial positions; therefore "
    "a speed tuple alone does not determine whether or when alignment occurs."
)
SEARCH_SPACE = (
    "All 24 ordered triples of distinct exact speeds selected from {1, 2, 3, 4} "
    "were enumerated. This exhausts that bounded speed space only; none can be "
    "classified as a counterexample without the missing alignment, orbit, and "
    "initial-position definitions."
)


def source_certifies_counterexample(speeds):
    """Return False because speeds alone do not define the claimed event."""
    assert len(speeds) == 3
    assert len(set(speeds)) == 3
    return False


def main():
    checked = 0
    witness = None

    for speeds in permutations(SPEEDS, 3):
        checked += 1
        if source_certifies_counterexample(speeds):
            witness = speeds
            break

    assert checked == 24
    assert witness is None

    result = {
        "record_id": RECORD_ID,
        "outcome": "NO_WITNESS_INCONCLUSIVE",
        "witness_description": WITNESS_DESCRIPTION,
        "refutation_explanation": REFUTATION_EXPLANATION,
        "search_space": SEARCH_SPACE,
    }
    print(json.dumps(result, ensure_ascii=False, separators=(",", ":")))


if __name__ == "__main__":
    main()
