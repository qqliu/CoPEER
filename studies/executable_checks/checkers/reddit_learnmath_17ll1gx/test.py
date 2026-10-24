"""Continuous functions map open sets to open sets."""

import json
from fractions import Fraction

RECORD_ID = "reddit_learnmath_17ll1gx"
OUTCOME = "WITNESS_FOUND"
WITNESS_DESCRIPTION = (
    "Let f: R -> R be the constant function f(x)=0, and let U=(0,1). "
    "The function f is continuous and U is open, but f(U)={0}."
)
REFUTATION_EXPLANATION = (
    "The singleton {0} is not open in R: for every positive radius, the "
    "interval about 0 contains a nonzero point. Thus this continuous function "
    "maps the open set (0,1) to a set that is not open, contradicting the claim."
)
SEARCH_SPACE = (
    "All pairs consisting of the single constant function f(x)=0 and the "
    "single rational-endpoint open interval U=(0,1); exactly 1 pair was "
    "exhaustively checked."
)

constants = (Fraction(0),)
open_intervals = ((Fraction(0), Fraction(1)),)
witness_found = False
pairs_checked = 0

for constant_value in constants:
    for left_endpoint, right_endpoint in open_intervals:
        pairs_checked += 1
        interval_is_nonempty_and_open = left_endpoint < right_endpoint
        function_is_continuous = True  # Every constant real function is continuous.

        # A nonempty interval has singleton image under a constant function.
        image_is_singleton = interval_is_nonempty_and_open

        # Radius 1 witnesses failure of openness: constant_value + 1/2 lies
        # within that radius but is not in the singleton image.
        radius = Fraction(1)
        nearby_point = constant_value + Fraction(1, 2)
        singleton_is_not_open = (
            nearby_point != constant_value
            and abs(nearby_point - constant_value) < radius
        )

        if (
            function_is_continuous
            and interval_is_nonempty_and_open
            and image_is_singleton
            and singleton_is_not_open
        ):
            witness_found = True

assert pairs_checked == 1
assert witness_found

result = {
    "record_id": RECORD_ID,
    "outcome": OUTCOME,
    "witness_description": WITNESS_DESCRIPTION,
    "refutation_explanation": REFUTATION_EXPLANATION,
    "search_space": SEARCH_SPACE,
}
print(json.dumps(result, separators=(",", ":")))
