"""The polynomial L^(n+1)-2L^n+1=0 has a unique positive real solution that determines the ratio."""

import json
from fractions import Fraction

RECORD_ID = "reddit_learnmath_1mv93ew"
VERDICT = "CONFIRMED"
NOTES = "Exact arithmetic confirms that for n=2 both L=1 and L=(1+sqrt(5))/2 are distinct positive roots. The uniqueness claim therefore fails substantively as stated; this is not plainly a typo, though an omitted restriction such as L>1 could repair it."

# Each pair (a, b) denotes a + b*sqrt(5), with sqrt(5) the positive root.
def add(x, y):
    return (x[0] + y[0], x[1] + y[1])


def multiply(x, y):
    return (x[0] * y[0] + 5 * x[1] * y[1],
            x[0] * y[1] + x[1] * y[0])


def scale(k, x):
    return (k * x[0], k * x[1])


def nonnegative_integer_power(x, exponent):
    assert isinstance(exponent, int) and exponent >= 0
    result = (Fraction(1), Fraction(0))
    factor = x
    remaining = exponent
    while remaining:
        if remaining % 2:
            result = multiply(result, factor)
        factor = multiply(factor, factor)
        remaining //= 2
    return result


def polynomial_at(x, n):
    leading = nonnegative_integer_power(x, n + 1)
    middle = scale(-2, nonnegative_integer_power(x, n))
    return add(add(leading, middle), (Fraction(1), Fraction(0)))


n = 2
one = (Fraction(1), Fraction(0))
golden_ratio = (Fraction(1, 2), Fraction(1, 2))
zero = (Fraction(0), Fraction(0))

assert polynomial_at(one, n) == zero
assert polynomial_at(golden_ratio, n) == zero
assert golden_ratio != one

# sqrt(5) > 1 because both are positive and 5 > 1 squared; hence
# (1 + sqrt(5))/2 > 1, so the second root is positive and distinct.
assert 5 > 1 * 1
assert golden_ratio[0] > 0 and golden_ratio[1] > 0

result = {"record_id": RECORD_ID, "verdict": VERDICT, "notes": NOTES}
print(json.dumps(result, separators=(",", ":")))
