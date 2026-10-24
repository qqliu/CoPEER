r"""Every reducible quadratic over F can be written exactly as (x-a)(x-b) with a,b in F."""

import json
from fractions import Fraction

REPORT = {
    "record_id": "reddit_learnmath_bp2nbn",
    "verdict": "CONFIRMED",
    "notes": "Exact coefficient arithmetic confirms that over Q, 2x^2 is reducible as (2x)(x), while every (x-a)(x-b) is monic and therefore cannot equal it. The refuted statement has a substantive missing-leading-coefficient/monicity hypothesis, not a plain typo.",
}


def multiply(left, right):
    result = [Fraction(0) for _ in range(len(left) + len(right) - 1)]
    for left_degree, left_coefficient in enumerate(left):
        for right_degree, right_coefficient in enumerate(right):
            result[left_degree + right_degree] += left_coefficient * right_coefficient
    return tuple(result)


def degree(polynomial):
    for index in range(len(polynomial) - 1, -1, -1):
        if polynomial[index] != 0:
            return index
    return -1


# Coefficients are stored from constant term upward.
f = (Fraction(0), Fraction(0), Fraction(2))
left_factor = (Fraction(0), Fraction(2))
right_factor = (Fraction(0), Fraction(1))

assert degree(f) == 2
assert degree(left_factor) == 1
assert degree(right_factor) == 1
assert multiply(left_factor, right_factor) == f

# For arbitrary a,b in Q, x-a and x-b both have leading coefficient 1.
# Hence their product always has leading coefficient 1, independently of a,b.
claimed_form_leading_coefficient = Fraction(1) * Fraction(1)
witness_leading_coefficient = f[2]
assert claimed_form_leading_coefficient == 1
assert witness_leading_coefficient == 2
assert claimed_form_leading_coefficient != witness_leading_coefficient
assert REPORT["verdict"] == "CONFIRMED"

print(json.dumps(REPORT, separators=(",", ":")))
