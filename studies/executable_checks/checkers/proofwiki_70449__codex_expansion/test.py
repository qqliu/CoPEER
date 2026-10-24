"""For every nonzero rational x, the substitution n/x may be treated as tending to positive infinity as n tends to positive infinity."""

import json
from fractions import Fraction
from math import gcd

RECORD_ID = "proofwiki_70449__codex_expansion"
WITNESS_DESCRIPTION = "x = -1. For every positive integer n, n/x = -n < 0."
REFUTATION_EXPLANATION = (
    "A sequence tending to positive infinity must eventually exceed 0. "
    "For x = -1, n/x = -n never exceeds 0, so the substitution tends "
    "toward negative infinity instead and violates the universal claim."
)
SEARCH_SPACE = (
    "All 22 reduced nonzero rationals p/q with 1 <= |p| <= 4 and "
    "1 <= q <= 4, q positive, exhaustively visited in fixed order by "
    "increasing |p|, negative sign before positive sign, then increasing q."
)

counterexamples = []
visited = 0
for magnitude in range(1, 5):
    for sign in (-1, 1):
        numerator = sign * magnitude
        for denominator in range(1, 5):
            if gcd(magnitude, denominator) != 1:
                continue
            x = Fraction(numerator, denominator)
            visited += 1
            # If x is negative, then n/x is negative for every positive
            # integer n, so it cannot eventually exceed 0 and hence cannot
            # tend to positive infinity.
            if x < 0:
                counterexamples.append(x)

assert visited == 22
assert counterexamples
assert counterexamples[0] == Fraction(-1, 1)

result = {
    "record_id": RECORD_ID,
    "outcome": "WITNESS_FOUND",
    "witness_description": WITNESS_DESCRIPTION,
    "refutation_explanation": REFUTATION_EXPLANATION,
    "search_space": SEARCH_SPACE,
}
print(json.dumps(result, separators=(",", ":")))
