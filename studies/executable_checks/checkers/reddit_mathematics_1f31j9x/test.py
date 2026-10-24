"""After offsetting each horizontal cross section of y²−x²=1 horizontally by y, the resulting curve is y=(1+1/x)/2."""

import json
from fractions import Fraction

RECORD_ID = "reddit_mathematics_1f31j9x"
OUTCOME = "WITNESS_FOUND"
WITNESS_DESCRIPTION = "For t=1/2, the original point is (3/4, 5/4). The horizontal offset map (x,y)->(x+y,y) sends it to (2, 5/4)."
REFUTATION_EXPLANATION = "The original point satisfies 25/16-9/16=1. At transformed x=2, the claimed formula gives y=(1+1/2)/2=3/4, not 5/4, so the transformed point is absent from the claimed curve."
SEARCH_SPACE = "All 16 ordered pairs (p,q) with 1 <= p <= 4 and 1 <= q <= 4, using t=p/q and the exact rational hyperbola point ((1-t^2)/(2t),(1+t^2)/(2t)); each was tested after (x,y)->(x+y,y)."

one = Fraction(1, 1)
half = Fraction(1, 2)
first_witness = None
checked = 0

for p in range(1, 5):
    for q in range(1, 5):
        checked += 1
        t = Fraction(p, q)
        inverse_two_t = Fraction(q, 2 * p)
        old_x = (one - t * t) * inverse_two_t
        old_y = (one + t * t) * inverse_two_t
        assert old_y * old_y - old_x * old_x == one

        new_x = old_x + old_y
        new_y = old_y
        claimed_y = (one + Fraction(new_x.denominator, new_x.numerator)) * half
        if new_y != claimed_y and first_witness is None:
            first_witness = (p, q, old_x, old_y, new_x, claimed_y)

assert checked == 16
assert first_witness == (
    1,
    2,
    Fraction(3, 4),
    Fraction(5, 4),
    Fraction(2, 1),
    Fraction(3, 4),
)

result = {
    "record_id": RECORD_ID,
    "outcome": OUTCOME,
    "witness_description": WITNESS_DESCRIPTION,
    "refutation_explanation": REFUTATION_EXPLANATION,
    "search_space": SEARCH_SPACE,
}
print(json.dumps(result, ensure_ascii=False, separators=(",", ":")))
