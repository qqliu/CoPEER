r"""The expression 128 + 0x - 6x^2 - (1/2)x^3 equals 128 - (1/2)(12 - x)x^2."""

import json
from fractions import Fraction

REPORT = {
    "record_id": "reddit_math_17jli96",
    "verdict": "CONFIRMED",
    "notes": "Exact arithmetic at x = 1 gives 243/2 on the left and 245/2 on the right, so the witness genuinely refutes the equality. In the quoted context, the refuted statement is plainly a sign typo, not a substantive mathematical claim.",
}

x = 1
half = Fraction(1, 2)
x_squared = x * x
x_cubed = x_squared * x
left_value = 128 + 0 * x - 6 * x_squared - half * x_cubed
right_value = 128 - half * (12 - x) * x_squared

assert left_value == Fraction(243, 2)
assert right_value == Fraction(245, 2)
assert left_value != right_value
assert right_value - left_value == 1

print(json.dumps(REPORT))
