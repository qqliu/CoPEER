"""The proposed expression equals the nth derivative of f(x)=1/(1-x)^2."""

import json
from fractions import Fraction
from math import factorial

RECORD_ID = "reddit_askmath_eq9wtw"
WITNESS_DESCRIPTION = (
    "At n=1 and x=0, the proposed expression is -2, while the first "
    "derivative of f is 2."
)
REFUTATION_EXPLANATION = (
    "For f(x)=(1-x)^-2, the coefficient of x^1 at 0 is 2, so "
    "f'(0)=1!*2=2. The proposed expression gives "
    "2!*(-1)*(1)^-3=-2. Since -2 != 2, the claimed equality fails."
)
SEARCH_SPACE = (
    "All 7 pairs (n,x) with n in {0,1,2,3,4,5,6} and x=0; every pair "
    "was evaluated using exact Fraction arithmetic."
)

search_ns = tuple(range(7))
search_xs = (Fraction(0, 1),)
first_witness = None
swept = []

for n in search_ns:
    for x in search_xs:
        swept.append((n, x))

        # At x=0, coefficients of (1-x)^-1 are all 1. Convolving that
        # series with itself gives the coefficients of f(x)=(1-x)^-2.
        unit_coefficients = (Fraction(1, 1),) * (n + 1)
        coefficient = sum(
            (
                unit_coefficients[k] * unit_coefficients[n - k]
                for k in range(n + 1)
            ),
            Fraction(0, 1),
        )
        actual_derivative = Fraction(factorial(n), 1) * coefficient

        sign = Fraction(-1 if n % 2 else 1, 1)
        base = Fraction(1, 1) - x
        positive_power = base ** (n + 2)
        negative_power = Fraction(
            positive_power.denominator, positive_power.numerator
        )
        proposed = Fraction(factorial(n + 1), 1) * sign * negative_power

        if proposed != actual_derivative and first_witness is None:
            first_witness = (n, x, proposed, actual_derivative)

assert len(swept) == 7

if first_witness == (1, Fraction(0, 1), Fraction(-2, 1), Fraction(2, 1)):
    result = {
        "record_id": RECORD_ID,
        "outcome": "WITNESS_FOUND",
        "witness_description": WITNESS_DESCRIPTION,
        "refutation_explanation": REFUTATION_EXPLANATION,
        "search_space": SEARCH_SPACE,
    }
else:
    result = {
        "record_id": RECORD_ID,
        "outcome": "NO_WITNESS_EXHAUSTIVE",
        "witness_description": "No counterexample was found in the bounded space.",
        "refutation_explanation": "The finite sweep found no unequal values.",
        "search_space": SEARCH_SPACE,
    }

print(json.dumps(result, separators=(",", ":")))
