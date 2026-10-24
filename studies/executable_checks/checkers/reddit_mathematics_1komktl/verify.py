"""The AM-GM inequality holds for arbitrary real numbers, including the two-variable base case, without requiring nonnegativity."""

import json
from fractions import Fraction
from math import isqrt

REPORT = {
    "record_id": "reddit_mathematics_1komktl",
    "verdict": "CONFIRMED",
    "notes": "The refuted statement is substantive, not plainly a typo. For the real inputs a = b = -2, the principal real geometric mean is exactly sqrt(4) = 2, while the arithmetic mean is exactly -2, so AM >= GM is false.",
}

a = -2
b = -2
assert isinstance(a, int) and isinstance(b, int)
assert a < 0 and b < 0

product = a * b
assert product >= 0
geometric_mean_integer = isqrt(product)
assert geometric_mean_integer * geometric_mean_integer == product

arithmetic_mean = Fraction(a + b, 2)
geometric_mean = Fraction(geometric_mean_integer, 1)
assert arithmetic_mean == Fraction(-2, 1)
assert geometric_mean == Fraction(2, 1)
assert arithmetic_mean < geometric_mean
assert not arithmetic_mean >= geometric_mean

print(json.dumps(REPORT, separators=(",", ":")))
