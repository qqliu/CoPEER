"""An invertible complex matrix must have determinant 1."""

import json
from fractions import Fraction

RECORD_ID = "reddit_learnmath_fhzr9u"
OUTCOME = "WITNESS_FOUND"
WITNESS_DESCRIPTION = "The 1x1 complex matrix A = [[2]]."
REFUTATION_EXPLANATION = (
    "Its inverse is [[1/2]], so A is invertible, while det(A) = 2 != 1."
)
SEARCH_SPACE = (
    "All 1x1 complex matrices A = [[a]] with a in {0, 1, 2}, "
    "checked in that order."
)

witnesses = []
for a in (0, 1, 2):
    determinant = a
    if a != 0:
        inverse_entry = Fraction(1, a)
        if determinant != 1 and a * inverse_entry == 1:
            witnesses.append(a)

assert witnesses == [2]

result = {
    "record_id": RECORD_ID,
    "outcome": OUTCOME,
    "witness_description": WITNESS_DESCRIPTION,
    "refutation_explanation": REFUTATION_EXPLANATION,
    "search_space": SEARCH_SPACE,
}
print(json.dumps(result, sort_keys=False, separators=(",", ":")))
