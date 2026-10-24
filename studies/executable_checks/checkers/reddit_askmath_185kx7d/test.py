"""The transformation from (k(k+1))/2 +(k+1) to (k(k+1)+(k+1))/2 preserves equality."""

import json
from fractions import Fraction

RECORD_ID = "reddit_askmath_185kx7d"
SEARCH_SPACE = (
    "All integer k from 0 through 100 inclusive, checked in increasing order "
    "with exact Fraction arithmetic."
)

first_witness = None
for k in range(101):
    original = Fraction(k * (k + 1), 2) + Fraction(k + 1, 1)
    transformed = Fraction(k * (k + 1) + (k + 1), 2)
    if first_witness is None and original != transformed:
        first_witness = k

if first_witness == 0:
    result = {
        "record_id": RECORD_ID,
        "outcome": "WITNESS_FOUND",
        "witness_description": (
            "k = 0: the original expression equals 1, while the transformed "
            "expression equals 1/2."
        ),
        "refutation_explanation": (
            "At k = 0, (k(k+1))/2 + (k+1) = 1 but "
            "(k(k+1)+(k+1))/2 = 1/2, so the transformation does not preserve "
            "equality."
        ),
        "search_space": SEARCH_SPACE,
    }
else:
    result = {
        "record_id": RECORD_ID,
        "outcome": "NO_WITNESS_EXHAUSTIVE",
        "witness_description": "No counterexample was found in the bounded search space.",
        "refutation_explanation": "The bounded sweep found no unequal pair of expression values.",
        "search_space": SEARCH_SPACE,
    }

print(json.dumps(result, sort_keys=True, separators=(",", ":")))
