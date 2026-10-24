"""For a fixed irrational number, division by irrational numbers can produce only one possible rational result."""

import json
from fractions import Fraction

RECORD_ID = "reddit_mathematics_1dz93wr"
OUTCOME = "WITNESS_FOUND"
WITNESS_DESCRIPTION = (
    "Fix alpha = sqrt(2). The irrational divisors beta_1 = sqrt(2) and "
    "beta_2 = sqrt(2)/2 give alpha/beta_1 = 1 and alpha/beta_2 = 2."
)
REFUTATION_EXPLANATION = (
    "The same fixed irrational numerator therefore has two distinct rational "
    "quotient results, 1 and 2, contradicting the assertion that only one is possible."
)
SEARCH_SPACE = (
    "All seven distinct coefficients c = p/q generated in fixed order by "
    "1 <= p <= 3 and 1 <= q <= 3, representing the irrational divisors "
    "c*sqrt(2), and all 21 unordered pairs of those divisors."
)


def coefficient_space():
    coefficients = []
    for numerator in range(1, 4):
        for denominator in range(1, 4):
            coefficient = Fraction(numerator, denominator)
            if coefficient not in coefficients:
                coefficients.append(coefficient)
    return coefficients


def exact_quotient(divisor_coefficient):
    # sqrt(2) divided by c*sqrt(2) is the exact rational reciprocal of c.
    return Fraction(divisor_coefficient.denominator, divisor_coefficient.numerator)


def main():
    coefficients = coefficient_space()
    quotients = [exact_quotient(coefficient) for coefficient in coefficients]

    first_witness = None
    pairs_checked = 0
    for left in range(len(coefficients)):
        for right in range(left + 1, len(coefficients)):
            pairs_checked += 1
            if quotients[left] != quotients[right] and first_witness is None:
                first_witness = (
                    coefficients[left],
                    coefficients[right],
                    quotients[left],
                    quotients[right],
                )

    expected = (Fraction(1, 1), Fraction(1, 2), Fraction(1, 1), Fraction(2, 1))
    if len(coefficients) != 7 or pairs_checked != 21 or first_witness != expected:
        raise AssertionError("exact bounded search did not produce the expected witness")

    payload = {
        "record_id": RECORD_ID,
        "outcome": OUTCOME,
        "witness_description": WITNESS_DESCRIPTION,
        "refutation_explanation": REFUTATION_EXPLANATION,
        "search_space": SEARCH_SPACE,
    }
    print(json.dumps(payload, sort_keys=False, separators=(",", ":")))


if __name__ == "__main__":
    main()
