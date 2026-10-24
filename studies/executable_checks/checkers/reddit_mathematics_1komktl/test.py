"""The AM-GM inequality holds for arbitrary real numbers, including the two-variable base case, without requiring nonnegativity."""

import json
from fractions import Fraction
from itertools import product
from math import isqrt

RECORD_ID = "reddit_mathematics_1komktl"
OUTCOME = "WITNESS_FOUND"
WITNESS_DESCRIPTION = "The ordered pair (a, b) = (-2, -2)."
REFUTATION_EXPLANATION = (
    "Its arithmetic mean is (-2 + -2)/2 = -2, while its real geometric "
    "mean is sqrt((-2)(-2)) = sqrt(4) = 2. Thus AM >= GM becomes "
    "-2 >= 2, which is false."
)
SEARCH_SPACE = (
    "Exhaustively swept the 13 ordered integer pairs (a, b) in "
    "{-2, -1, 0, 1, 2}^2 for which ab is a nonnegative perfect square, "
    "checking the standard two-variable inequality (a+b)/2 >= sqrt(ab) "
    "in fixed lexicographic order."
)

values = range(-2, 3)
checked = []
violations = []

for a, b in product(values, repeat=2):
    radicand = a * b
    if radicand < 0:
        continue
    root = isqrt(radicand)
    if root * root != radicand:
        continue
    arithmetic_mean = Fraction(a + b, 2)
    checked.append((a, b))
    if arithmetic_mean < root:
        violations.append((a, b, arithmetic_mean, root))

assert len(checked) == 13
assert violations
assert violations[0] == (-2, -2, Fraction(-2, 1), 2)

result = {
    "record_id": RECORD_ID,
    "outcome": OUTCOME,
    "witness_description": WITNESS_DESCRIPTION,
    "refutation_explanation": REFUTATION_EXPLANATION,
    "search_space": SEARCH_SPACE,
}
print(json.dumps(result, separators=(",", ":")))
