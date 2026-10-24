r"""For real x and y such that sqrt(xy) is defined, sqrt(xy) is less than or equal to (x+y)/2."""

import json
from fractions import Fraction
from math import isqrt

REPORT = {
    "record_id": "reddit_math_1jl7962",
    "verdict": "CONFIRMED",
    "notes": "The witness is valid: at x = y = -1, xy = 1, the principal square root is 1, and (x+y)/2 = -1, so 1 <= -1 is false. The refuted statement is substantive, not plainly a typo; it lacks a condition such as x,y >= 0."
}

x = -1
y = -1
radicand = x * y
assert radicand >= 0
root = isqrt(radicand)
assert root >= 0
assert root * root == radicand
right_hand_side = Fraction(x + y, 2)
assert root == 1
assert right_hand_side == -1
assert not Fraction(root, 1) <= right_hand_side

print(json.dumps(REPORT, separators=(",", ":")))
