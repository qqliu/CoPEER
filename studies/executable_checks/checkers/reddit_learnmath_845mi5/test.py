"""For a unit-rate Poisson process, the proof incorrectly claims that the probability of exactly one arrival between t and s1 is e^(t-s1), omitting the factor s1-t."""

import json

RECORD_ID = "reddit_learnmath_845mi5"
WITNESS_DESCRIPTION = (
    "t = 0 and s1 = 2: the interval length is 2, so the "
    "exactly-one-arrival probability is 2*e^(-2), not e^(-2)."
)
REFUTATION_EXPLANATION = (
    "For a unit-rate Poisson process, the exactly-one-arrival probability "
    "has coefficient s1-t multiplying the common positive factor e^(t-s1). "
    "At t = 0 and s1 = 2, the correct and claimed coefficients are "
    "respectively 2 and 1. Because e^(-2) is positive, 2*e^(-2) is not "
    "e^(-2), demonstrating the omitted factor."
)
SEARCH_SPACE = (
    "All 3 integer pairs (t, s1) with t = 0 and s1 in {1, 2, 3}, "
    "checked in increasing s1 order using exact integer comparison of the "
    "coefficients multiplying the common positive factor e^(t-s1)."
)


def main():
    witnesses = []
    for t in (0,):
        for s1 in range(1, 4):
            correct_coefficient = s1 - t
            claimed_coefficient = 1
            if correct_coefficient != claimed_coefficient:
                witnesses.append((t, s1))

    assert witnesses
    assert witnesses[0] == (0, 2)

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
