"""The proof claims that the function F(x)=∫₁ˣ(1/t)dt is identically equal to e^x."""

import json
from fractions import Fraction
from math import factorial

RECORD_ID = "proofwiki_116604__codex_expansion"
OUTCOME = "WITNESS_FOUND"
WITNESS_DESCRIPTION = (
    "x = 1. The degenerate definite integral gives F(1) = 0, "
    "whereas e^1 = e is positive."
)
REFUTATION_EXPLANATION = (
    "The exact exponential series for e has first two terms 1 and 1, "
    "so e >= 2 > 0. Thus F(1) = 0 is not equal to e^1, "
    "disproving the claimed identity."
)
SEARCH_SPACE = (
    "Exactly the singleton integer input space {1}; its sole point is "
    "checked in fixed tuple order."
)


def search():
    candidates = (1,)
    for x in candidates:
        if x == 1:
            integral_value = Fraction(0, 1)
            exponential_lower_bound = sum(
                (Fraction(1, factorial(k)) for k in range(2)),
                Fraction(0, 1),
            )
            if integral_value == Fraction(0, 1) and exponential_lower_bound > 0:
                return True
    return False


def main():
    if not search():
        raise AssertionError("The singleton search must find x = 1")
    result = {
        "record_id": RECORD_ID,
        "outcome": OUTCOME,
        "witness_description": WITNESS_DESCRIPTION,
        "refutation_explanation": REFUTATION_EXPLANATION,
        "search_space": SEARCH_SPACE,
    }
    print(json.dumps(result, sort_keys=False))


if __name__ == "__main__":
    main()
