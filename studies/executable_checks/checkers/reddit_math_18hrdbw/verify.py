r"""For every positive integer n, the sum 1^2+2^2+...+n^2 equals n(n+1)/2."""

import json
from fractions import Fraction

REPORT = {
    "record_id": "reddit_math_18hrdbw",
    "verdict": "CONFIRMED",
    "notes": "Exact independent arithmetic confirms the positive-integer witness n = 2: the sum of squares is 5, whereas n(n+1)/2 is 3. The refuted statement is substantive, not plainly a typo: it asserts the triangular-number formula for a sum of squares."
}

n = 2
assert isinstance(n, int) and n > 0
sum_of_squares = 0
for term in range(1, n + 1):
    sum_of_squares += term * term
claimed_value = Fraction(n * (n + 1), 2)
assert sum_of_squares == 5
assert claimed_value == 3
assert sum_of_squares != claimed_value

print(json.dumps(REPORT))
