r"""The exponent-reassociation step (-1)^(2/2) = ((-1)^2)^(1/2) is valid."""

import json
from fractions import Fraction
from math import isqrt

RECORD_ID = "reddit_learnmath_fuwmpf"
OUTCOME = "WITNESS_FOUND"
WITNESS_DESCRIPTION = (
    "For base -1 and exponent data (2, 2), the left side is "
    "(-1)^(2/2) = -1, while the reassociated right side is "
    "((-1)^2)^(1/2) = 1."
)
REFUTATION_EXPLANATION = (
    "The two sides have exact integer values -1 and 1, respectively, so they "
    "are unequal and the stated exponent-reassociation step is invalid."
)
SEARCH_SPACE = (
    "The singleton space containing base -1 and exponent data (2, 2), testing "
    "the stated reassociation using the nonnegative square root of 1; this "
    "one-element space was swept exhaustively."
)

candidates = ((-1, 2, 2),)
witness = None

for base, numerator, denominator in candidates:
    exponent = Fraction(numerator, denominator)
    if exponent.denominator != 1:
        continue
    left = base ** exponent.numerator
    inner = base ** numerator
    root = isqrt(inner)
    if root ** denominator != inner:
        continue
    right = root
    if left != right:
        witness = (base, numerator, denominator, left, right)
        break

if witness is None:
    raise AssertionError("The exhaustively searched singleton contained no witness")

result = {
    "record_id": RECORD_ID,
    "outcome": OUTCOME,
    "witness_description": WITNESS_DESCRIPTION,
    "refutation_explanation": REFUTATION_EXPLANATION,
    "search_space": SEARCH_SPACE,
}
print(json.dumps(result, separators=(",", ":")))
