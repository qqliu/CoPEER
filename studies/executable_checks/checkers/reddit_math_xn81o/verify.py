"""For arbitrary vectors x and y, the normalized vectors x/||x|| and y/||y|| are unit vectors."""

import json
from fractions import Fraction

REPORT = {
    "record_id": "reddit_math_xn81o",
    "verdict": "CONFIRMED",
    "notes": "Exact arithmetic at x=y=0 gives ||x||=||y||=0, so both purported normalizations require division by zero and are undefined, hence are not unit vectors. The refuted statement is substantive—a missing nonzero-vector hypothesis—not plainly a typo.",
}

def norm(coordinate):
    return abs(coordinate)

def divide_vector_by_scalar(coordinate, scalar):
    if scalar == 0:
        raise ZeroDivisionError("a vector cannot be divided by the zero scalar")
    return Fraction(coordinate, scalar)

x = Fraction(0, 1)
y = Fraction(0, 1)
assert norm(x) == Fraction(0, 1)
assert norm(y) == Fraction(0, 1)

undefined_count = 0
for vector in (x, y):
    try:
        divide_vector_by_scalar(vector, norm(vector))
    except ZeroDivisionError:
        undefined_count += 1
    else:
        raise AssertionError("the reported normalization unexpectedly existed")

assert undefined_count == 2
assert REPORT["verdict"] == "CONFIRMED"
print(json.dumps(REPORT, separators=(",", ":")))
