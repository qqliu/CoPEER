"""Every reducible quadratic over F can be written exactly as (x-a)(x-b) with a,b in F.

This program performs a fixed finite search over explicitly factored quadratics
in Q[x] and uses the exact leading coefficient invariant to test the claimed
monic factorization.
"""

import json
from fractions import Fraction

RECORD_ID = "reddit_learnmath_bp2nbn"
OUTCOME = "WITNESS_FOUND"
WITNESS_DESCRIPTION = (
    "Take F=Q and f(x)=2x^2. It is reducible because f(x)=(2x)(x), "
    "a product of two degree-one polynomials in Q[x]."
)
REFUTATION_EXPLANATION = (
    "For every a,b in Q, (x-a)(x-b)=x^2-(a+b)x+ab has leading "
    "coefficient 1, whereas 2x^2 has leading coefficient 2. Therefore "
    "2x^2 cannot equal (x-a)(x-b) for any a,b in Q."
)
SEARCH_SPACE = (
    "All 100 parameter triples (c,r,s) with c in (2,-2,-1,1) and r,s "
    "in (0,-2,-1,1,2), each representing the reducible quadratic "
    "c(x-r)(x-s) over Q, were swept in the stated fixed nested-loop "
    "order using exact Fraction arithmetic."
)

scalars = (2, -2, -1, 1)
roots = (0, -2, -1, 1, 2)
first_witness = None
examined = 0

for c_integer in scalars:
    for r_integer in roots:
        for s_integer in roots:
            c = Fraction(c_integer)
            r = Fraction(r_integer)
            s = Fraction(s_integer)
            examined += 1

            # Coefficients of c(x-r)(x-s), from x^2 down to the constant.
            polynomial = (c, -c * (r + s), c * r * s)

            # The displayed factors (c*x-c*r) and (x-s) both have degree one.
            left_factor = (c, -c * r)
            right_factor = (Fraction(1), -s)
            product = (
                left_factor[0] * right_factor[0],
                left_factor[0] * right_factor[1]
                + left_factor[1] * right_factor[0],
                left_factor[1] * right_factor[1],
            )
            assert product == polynomial

            # Every (x-a)(x-b) has leading coefficient exactly one.
            obstructed = polynomial[0] != Fraction(1)
            if obstructed and first_witness is None:
                first_witness = (c, r, s, polynomial)

assert examined == 100
assert first_witness == (
    Fraction(2),
    Fraction(0),
    Fraction(0),
    (Fraction(2), Fraction(0), Fraction(0)),
)

result = {
    "record_id": RECORD_ID,
    "outcome": OUTCOME,
    "witness_description": WITNESS_DESCRIPTION,
    "refutation_explanation": REFUTATION_EXPLANATION,
    "search_space": SEARCH_SPACE,
}
print(json.dumps(result, separators=(",", ":")))
