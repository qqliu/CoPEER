"""The initialization a_1=0 implies the strict inequality a_2>a_1 and hence begins a strictly increasing sequence."""

import itertools
import json
from fractions import Fraction

RECORD_ID = "reddit_learnmath_10ypfsa"
OUTCOME = "WITNESS_FOUND"
WITNESS_DESCRIPTION = (
    "Let X be identically 0 (probability 1 on 0), let r=0, and initialize "
    "a_1=0. Then a_2=E[max(X,a_1)]/(1+r)=0."
)
REFUTATION_EXPLANATION = (
    "For this witness, max(X,a_1)=max(0,0)=0 surely, so its expectation is 0 "
    "and a_2=a_1=0. Thus the claimed strict inequality a_2>a_1 fails."
)
SEARCH_SPACE = (
    "All probability mass functions on the ordered support (-1,0,1) with "
    "probabilities that are multiples of 1/2, total probability 1, and exact "
    "mean 0, paired with every r in (0,1). This is exactly 2 distributions "
    "times 2 choices of r, hence 4 cases, all of which are swept."
)


def main():
    support = (-1, 0, 1)
    searched = []
    violations = []

    for weights in itertools.product(range(3), repeat=3):
        if sum(weights) != 2:
            continue
        probabilities = tuple(Fraction(weight, 2) for weight in weights)
        mean = sum(
            (probability * value for probability, value in zip(probabilities, support)),
            Fraction(0, 1),
        )
        if mean != Fraction(0, 1):
            continue

        for r in (0, 1):
            a_1 = Fraction(0, 1)
            expected_max = sum(
                (
                    probability * max(value, a_1)
                    for probability, value in zip(probabilities, support)
                ),
                Fraction(0, 1),
            )
            a_2 = expected_max * Fraction(1, 1 + r)
            searched.append((weights, r, a_1, a_2))
            if not a_2 > a_1:
                violations.append((weights, r, a_1, a_2))

    assert len(searched) == 4
    assert violations
    assert violations[0] == ((0, 2, 0), 0, Fraction(0, 1), Fraction(0, 1))

    result = {
        "record_id": RECORD_ID,
        "outcome": OUTCOME,
        "witness_description": WITNESS_DESCRIPTION,
        "refutation_explanation": REFUTATION_EXPLANATION,
        "search_space": SEARCH_SPACE,
    }
    print(json.dumps(result))


if __name__ == "__main__":
    main()
