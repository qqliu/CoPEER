"""The submitted calculation concludes that (t+1/t)(t-1/t) equals 0."""

import json
from fractions import Fraction

record_id = "reddit_askmath_1qujy46"
search_space = (
    "The singleton exact-rational space {t = 2}, exhaustively checked in its "
    "sole fixed-order iteration."
)
candidates = (Fraction(2, 1),)

outcome = "NO_WITNESS_EXHAUSTIVE"
witness_description = ""
refutation_explanation = ""

for t in candidates:
    reciprocal = Fraction(t.denominator, t.numerator)
    value = (t + reciprocal) * (t - reciprocal)
    if value != Fraction(0, 1):
        outcome = "WITNESS_FOUND"
        witness_description = (
            "In the bounded space {t = 2}, t = 2 gives "
            "(t + 1/t)(t - 1/t) = 15/4."
        )
        refutation_explanation = (
            "Because 15/4 is not 0, t = 2 is a counterexample to the asserted equality."
        )
        break

result = {
    "record_id": record_id,
    "outcome": outcome,
    "witness_description": witness_description,
    "refutation_explanation": refutation_explanation,
    "search_space": search_space,
}
print(json.dumps(result, separators=(",", ":")))
