r"""The proof claims that odd a_0 forces both the leading coefficient a_n and the product q of all roots to be odd."""

import json
from fractions import Fraction

record_id = "reddit_learnmath_6sz8ww"
verdict = "CONFIRMED"
notes = "The witness is valid: for p(x) = -4x - 5, a_0 = -5 is odd, while a_1 = -4 is even and the sole-root product is exactly -5/4, which is not an odd integer. The refuted statement is substantive, not plainly a typo; it lacks an integrality condition on q."

constant_coefficient = -5
leading_coefficient = -4
root = Fraction(-constant_coefficient, leading_coefficient)
root_product = root

constant_is_odd = constant_coefficient % 2 != 0
leading_is_odd = leading_coefficient % 2 != 0
product_is_odd_integer = (
    root_product.denominator == 1 and root_product.numerator % 2 != 0
)

assert leading_coefficient * root + constant_coefficient == 0
assert root_product == Fraction(-5, 4)
assert constant_is_odd
assert not leading_is_odd
assert not product_is_odd_integer
assert not (leading_is_odd and product_is_odd_integer)

print(json.dumps({
    "record_id": record_id,
    "verdict": verdict,
    "notes": notes,
}, separators=(",", ":")))
