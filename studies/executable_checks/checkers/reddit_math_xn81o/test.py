"""For arbitrary vectors x and y, the normalized vectors x/||x|| and y/||y|| are unit vectors."""

import json
from fractions import Fraction

RECORD_ID = "reddit_math_xn81o"
OUTCOME = "WITNESS_FOUND"
WITNESS_DESCRIPTION = "Take x=0 and y=0. Both are included among arbitrary vectors."
REFUTATION_EXPLANATION = (
    "Every norm satisfies ||0||=0, so x/||x|| and y/||y|| both require "
    "division by zero for this witness. They are undefined and therefore are "
    "not unit vectors, contradicting the claim as stated without a nonzero-vector restriction."
)
SEARCH_SPACE = (
    "All 9 ordered pairs (x,y) in the one-dimensional rational normed space Q "
    "with x,y in {-1,0,1} and norm ||a||=|a|; every pair is checked in the "
    "fixed coordinate order (-1,0,1)."
)

coordinates = (-1, 0, 1)
violations = []
checked = 0

for x in coordinates:
    for y in coordinates:
        checked += 1
        norm_x = abs(x)
        norm_y = abs(y)

        normalized_x = None if norm_x == 0 else Fraction(x, norm_x)
        normalized_y = None if norm_y == 0 else Fraction(y, norm_y)

        x_is_unit = normalized_x is not None and abs(normalized_x) == 1
        y_is_unit = normalized_y is not None and abs(normalized_y) == 1

        if not (x_is_unit and y_is_unit):
            violations.append((x, y))

assert checked == 9
assert (0, 0) in violations

print(json.dumps({
    "record_id": RECORD_ID,
    "outcome": OUTCOME,
    "witness_description": WITNESS_DESCRIPTION,
    "refutation_explanation": REFUTATION_EXPLANATION,
    "search_space": SEARCH_SPACE,
}, separators=(",", ":")))
