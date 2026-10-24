"""From P = 2(L + W), the submitted Method 2 rearrangement yields L = W - (P/2)."""

import json
from fractions import Fraction
from itertools import product

RECORD_ID = "reddit_learnmath_17yc2bm"
OUTCOME = "WITNESS_FOUND"
WITNESS_DESCRIPTION = "L = 1, W = 1, P = 4 is a witness: P = 2(L + W), but W - (P/2) = -1, which is not L = 1."
REFUTATION_EXPLANATION = "Substitution gives 4 = 2(1 + 1), so the premise holds exactly. The submitted rearrangement gives 1 - 4/2 = -1 rather than 1, refuting the claimed rearrangement."
SEARCH_SPACE = "All 25 ordered pairs (L, W) in {1, 2, 3, 4, 5}^2, with P determined exactly as 2(L + W), were checked in lexicographic order."

first_witness = None
for length, width in product(range(1, 6), repeat=2):
    perimeter = 2 * (length + width)
    submitted_value = Fraction(width, 1) - Fraction(perimeter, 2)
    if submitted_value != length and first_witness is None:
        first_witness = (length, width, perimeter, submitted_value)

assert first_witness == (1, 1, 4, Fraction(-1, 1))

result = {
    "record_id": RECORD_ID,
    "outcome": OUTCOME,
    "witness_description": WITNESS_DESCRIPTION,
    "refutation_explanation": REFUTATION_EXPLANATION,
    "search_space": SEARCH_SPACE,
}
print(json.dumps(result, separators=(",", ":")))
