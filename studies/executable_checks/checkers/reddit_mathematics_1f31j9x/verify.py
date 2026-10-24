r"""After offsetting each horizontal cross section of y²−x²=1 horizontally by y, the resulting curve is y=(1+1/x)/2."""

import json
from fractions import Fraction

REPORT = {
    "record_id": "reddit_mathematics_1f31j9x",
    "verdict": "CONFIRMED",
    "notes": "Exact rational arithmetic verifies the reported witness. The literal statement is false, but it is plainly a typo: the transformed locus is y=(x+1/x)/2, not y=(1+1/x)/2.",
}

one = Fraction(1, 1)
two = Fraction(2, 1)
t = Fraction(1, 2)
t_squared = t * t
reciprocal_two_t = Fraction((two * t).denominator, (two * t).numerator)
original_x = (one - t_squared) * reciprocal_two_t
original_y = (one + t_squared) * reciprocal_two_t

assert original_x == Fraction(3, 4)
assert original_y == Fraction(5, 4)
assert original_y * original_y - original_x * original_x == one

transformed_x = original_x + original_y
transformed_y = original_y
assert transformed_x == Fraction(2, 1)
assert transformed_y == Fraction(5, 4)

reciprocal_transformed_x = Fraction(
    transformed_x.denominator,
    transformed_x.numerator,
)
claimed_y = (one + reciprocal_transformed_x) * Fraction(1, 2)
assert claimed_y == Fraction(3, 4)
assert transformed_y != claimed_y

assert two * transformed_x * transformed_y == transformed_x * transformed_x + one
correct_locus_y = (
    transformed_x + reciprocal_transformed_x
) * Fraction(1, 2)
assert correct_locus_y == transformed_y

print(json.dumps(REPORT, ensure_ascii=False, separators=(",", ":")))
