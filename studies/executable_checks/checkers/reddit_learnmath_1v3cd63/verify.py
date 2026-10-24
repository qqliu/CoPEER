"""For positive a and b, √(a/b) equals |(a/b)^(-1)|."""

import json
from fractions import Fraction

a = 1
b = 2
assert a > 0 and b > 0

ratio = Fraction(a, b)
reciprocal = Fraction(b, a)
absolute_reciprocal = reciprocal if reciprocal >= 0 else -reciprocal

assert ratio == Fraction(1, 2)
assert ratio * reciprocal == 1
assert absolute_reciprocal == 2
assert absolute_reciprocal >= 0

# For x >= 0 and y >= 0, sqrt(x) = y exactly when y*y = x.
claimed_equality_holds = absolute_reciprocal * absolute_reciprocal == ratio
assert absolute_reciprocal * absolute_reciprocal == 4
assert not claimed_equality_holds

REPORT = {
    "record_id": "reddit_learnmath_1v3cd63",
    "verdict": "CONFIRMED",
    "notes": "At a = 1 and b = 2, the ratio is exactly 1/2 and the absolute reciprocal is exactly 2. Since 2 squared is 4, not 1/2, it cannot equal the positive square root of 1/2. The refuted statement is substantive as written; the permitted evidence does not establish that it is plainly a typo.",
}
print(json.dumps(REPORT, ensure_ascii=False, separators=(",", ":")))
