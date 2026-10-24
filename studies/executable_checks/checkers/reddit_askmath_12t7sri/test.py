"""The displayed formula for the remainder r(x) makes the asserted equality f(x)=(a_n/b_n)g(x)+r(x) hold when deg(f)=deg(g)."""

import json
from fractions import Fraction
from itertools import product

VALUES = (-1, 0, 1)
first_witness = None
checked = 0

for a in product(VALUES, repeat=3):
    if a[2] == 0:
        continue
    for b in product(VALUES, repeat=3):
        if b[2] == 0:
            continue
        checked += 1
        quotient = Fraction(a[2], b[2])
        remainder = (
            Fraction(a[0], 1) - quotient * Fraction(a[0], 1),
            Fraction(a[1], 1) - quotient * Fraction(b[1], 1),
            Fraction(0, 1),
        )
        right_hand_side = tuple(
            quotient * Fraction(b[index], 1) + remainder[index]
            for index in range(3)
        )
        left_hand_side = tuple(Fraction(value, 1) for value in a)
        if right_hand_side != left_hand_side and first_witness is None:
            first_witness = (a, b)

expected_witness = ((-1, -1, -1), (0, -1, -1))
if checked != 324 or first_witness != expected_witness:
    raise AssertionError("deterministic exhaustive search produced an unexpected result")

result = {
    "record_id": "reddit_askmath_12t7sri",
    "outcome": "WITNESS_FOUND",
    "witness_description": "For n=2, take f(x)=-x^2-x-1 and g(x)=-x^2-x, so (a0,a1,a2)=(-1,-1,-1) and (b0,b1,b2)=(0,-1,-1).",
    "refutation_explanation": "Here a2/b2=1. The displayed formula gives r(x)=(a1-b1)x+a0-a0=0, so its right-hand side is g(x)=-x^2-x, which differs from f(x)=-x^2-x-1 in the constant coefficient.",
    "search_space": "All 324 ordered pairs (f,g) of degree-exactly-2 polynomials whose coefficients a0,a1,a2,b0,b1,b2 lie in {-1,0,1}, with a2 and b2 nonzero, in lexicographic itertools.product order; every pair was checked using Fraction arithmetic.",
}
print(json.dumps(result, separators=(",", ":")))
