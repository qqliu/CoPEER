"""The displayed equality for the n = k + 1 step holds."""

import json
from fractions import Fraction

RECORD_ID = "reddit_learnmath_4yb83h"
WITNESS_DESCRIPTION = (
    "With outer k = 1 and the summation index alpha-renamed to i, the left "
    "side is sum_{i=1}^{2} (i+1)/(2*2^i) = 7/8, while the right side is 1."
)
REFUTATION_EXPLANATION = (
    "The exact values 7/8 and 1 are unequal, so k = 1 is a counterexample "
    "to the displayed equality under the conventional interpretation of the "
    "summation variable as a dummy index."
)
SEARCH_SPACE = (
    "All integer outer parameters k from 1 through 32 inclusive were evaluated "
    "in fixed increasing order, with summation index i ranging from 1 through "
    "k+1 inclusive and all quantities computed as fractions.Fraction values."
)

first_witness = None
for outer_k in range(1, 33):
    left = sum(
        (Fraction(i + 1, 2 * (2 ** i)) for i in range(1, outer_k + 2)),
        Fraction(0, 1),
    )
    right = Fraction(2, 1) - Fraction(
        (4 * (2 ** outer_k)) - (outer_k + 3),
        2 * (2 ** outer_k),
    )
    if left != right and first_witness is None:
        first_witness = (outer_k, left, right)

assert first_witness == (1, Fraction(7, 8), Fraction(1, 1))

result = {
    "record_id": RECORD_ID,
    "outcome": "WITNESS_FOUND",
    "witness_description": WITNESS_DESCRIPTION,
    "refutation_explanation": REFUTATION_EXPLANATION,
    "search_space": SEARCH_SPACE,
}
print(json.dumps(result, separators=(",", ":")))
