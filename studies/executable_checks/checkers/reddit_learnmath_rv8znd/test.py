"""The product of two quotients with nonzero integer denominators is always nonzero."""

import json
from fractions import Fraction
from itertools import product

numerators = (-1, 0, 1)
denominators = (-1, 1)
quotients = tuple((n, d) for n in numerators for d in denominators)
first_witness = None
checked = 0

for left, right in product(quotients, repeat=2):
    checked += 1
    left_value = Fraction(left[0], left[1])
    right_value = Fraction(right[0], right[1])
    if left_value * right_value == 0 and first_witness is None:
        first_witness = (left, right)

assert checked == 36
assert first_witness == ((-1, -1), (0, -1))

result = {
    "record_id": "reddit_learnmath_rv8znd",
    "outcome": "WITNESS_FOUND",
    "witness_description": "The ordered pair (-1)/(-1) and 0/(-1) has exact quotient values 1 and 0, whose product is 0.",
    "refutation_explanation": "Both denominators are -1, hence are nonzero integers, but the exact product is 0; therefore the claimed universal nonzero conclusion is false.",
    "search_space": "All 36 ordered pairs of written quotients n/d, where n is in {-1, 0, 1} and d is in {-1, 1}, swept in fixed nested-product order."
}
print(json.dumps(result, separators=(",", ":")))
