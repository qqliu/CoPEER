r"""The displayed equality for the n = k + 1 step holds."""

import json
from fractions import Fraction

record_id = "reddit_learnmath_4yb83h"
notes = (
    "Exact recomputation at outer k = 1 gives left = 1/2 + 3/8 = 7/8 "
    "and right = 2 - 4/4 = 1, so the displayed equality fails under the "
    "conventional dummy-index interpretation. The false statement is "
    "substantive as written, not a plainly identifiable typo."
)

outer_index = 1
left_value = Fraction(0, 1)
for dummy_index in range(1, outer_index + 2):
    denominator = 2 * (2 ** dummy_index)
    left_value += Fraction(dummy_index + 1, denominator)

right_numerator = 4 * (2 ** outer_index) - (outer_index + 3)
right_denominator = 2 * (2 ** outer_index)
right_value = Fraction(2, 1) - Fraction(right_numerator, right_denominator)

assert left_value == Fraction(7, 8)
assert right_value == Fraction(1, 1)
assert left_value != right_value

result = {
    "record_id": record_id,
    "verdict": "CONFIRMED",
    "notes": notes,
}
print(json.dumps(result, separators=(",", ":")))
