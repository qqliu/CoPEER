"""The proposed expression equals the nth derivative of f(x)=1/(1-x)^2."""

import json
from fractions import Fraction


def factorial_nonnegative(value):
    assert isinstance(value, int)
    assert value >= 0
    result = 1
    factor = 2
    while factor <= value:
        result *= factor
        factor += 1
    return result


def integer_power(base, exponent):
    assert isinstance(exponent, int)
    assert exponent >= 0
    result = Fraction(1, 1)
    factor = base
    remaining = exponent
    while remaining:
        if remaining % 2:
            result *= factor
        factor *= factor
        remaining //= 2
    return result


def dual_sub(left, right):
    return (left[0] - right[0], left[1] - right[1])


def dual_mul(left, right):
    return (
        left[0] * right[0],
        left[1] * right[0] + left[0] * right[1],
    )


def dual_reciprocal(value):
    assert value[0] != 0
    inverse_value = Fraction(value[0].denominator, value[0].numerator)
    return (
        inverse_value,
        -value[1] * inverse_value * inverse_value,
    )


n = 1
x = Fraction(0, 1)
x_with_derivative = (x, Fraction(1, 1))
one = (Fraction(1, 1), Fraction(0, 1))
one_minus_x = dual_sub(one, x_with_derivative)
denominator = dual_mul(one_minus_x, one_minus_x)
function_value_and_derivative = dual_reciprocal(denominator)
actual_derivative = function_value_and_derivative[1]

sign = -1 if n % 2 else 1
base = Fraction(1, 1) - x
positive_power = integer_power(base, n + 2)
reciprocal_power = Fraction(
    positive_power.denominator,
    positive_power.numerator,
)
proposed_value = factorial_nonnegative(n + 1) * sign * reciprocal_power

assert function_value_and_derivative[0] == Fraction(1, 1)
assert actual_derivative == Fraction(2, 1)
assert proposed_value == Fraction(-2, 1)
assert proposed_value != actual_derivative

REPORT = {
    "record_id": "reddit_askmath_eq9wtw",
    "verdict": "CONFIRMED",
    "notes": "Exact dual-number differentiation gives f'(0)=2, while independent integer-power evaluation gives the proposed value -2. The refuted statement contains a substantive mathematical sign error (the extraneous (-1)^n factor), not a plainly typographical discrepancy.",
}

print(json.dumps(REPORT, separators=(",", ":")))
