"""The proof claims that odd a_0 forces both the leading coefficient a_n and the product q of all roots to be odd."""

import json
from fractions import Fraction
from itertools import product

RECORD_ID = "reddit_learnmath_6sz8ww"
OUTCOME = "WITNESS_FOUND"
WITNESS_DESCRIPTION = (
    "p(x) = -4x - 5 (degree 1): a_0 = -5, a_1 = -4, "
    "and its sole root (hence q) is -5/4."
)
REFUTATION_EXPLANATION = (
    "Here a_0 is odd, but the leading coefficient a_1 is even and "
    "q = -5/4 is not an odd integer. Thus odd a_0 alone does not "
    "force both claimed conclusions."
)
SEARCH_SPACE = (
    "All 87,840 integer coefficient vectors (a_0,...,a_n) of degrees "
    "1 through 4 with every coefficient in [-5,5], a_0 odd, and a_n "
    "nonzero, examined in increasing degree and lexicographic coefficient order."
)


def is_odd_integer(value):
    if isinstance(value, Fraction):
        return value.denominator == 1 and value.numerator % 2 != 0
    return value % 2 != 0


def main():
    coefficient_values = tuple(range(-5, 6))
    first_witness = None
    examined = 0

    for degree in range(1, 5):
        for coefficients in product(coefficient_values, repeat=degree + 1):
            a_0 = coefficients[0]
            a_n = coefficients[-1]
            if a_0 % 2 == 0 or a_n == 0:
                continue

            examined += 1
            sign = -1 if degree % 2 else 1
            q = Fraction(sign * a_0, a_n)
            violates = not (is_odd_integer(a_n) and is_odd_integer(q))
            if violates and first_witness is None:
                first_witness = (degree, coefficients, q)

    assert examined == 87840
    assert first_witness == (1, (-5, -4), Fraction(-5, 4))

    result = {
        "record_id": RECORD_ID,
        "outcome": OUTCOME,
        "witness_description": WITNESS_DESCRIPTION,
        "refutation_explanation": REFUTATION_EXPLANATION,
        "search_space": SEARCH_SPACE,
    }
    print(json.dumps(result, sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    main()
