"""The expression x arcsec(x) - ln|x + √(x^2 - 1)| is an antiderivative of arcsec(x) throughout its real domain."""

import json
from fractions import Fraction

RECORD_ID = "reddit_askmath_1gtr92f"
X_VALUES = (-2,)
BRANCH_SIGNS = (-1, 1)

# If the local derivative of arcsec is encoded as
# branch_sign / (abs(x) * sqrt(x^2 - 1)), then after subtracting
# arcsec(x), the derivative defect is the following exact coefficient
# of 1 / sqrt(x^2 - 1).
def defect_coefficient(x, branch_sign):
    x_sign = -1 if x < 0 else 1
    return Fraction(branch_sign * x_sign - 1, 1)

results = tuple(
    (x, branch_sign, defect_coefficient(x, branch_sign))
    for x in X_VALUES
    for branch_sign in BRANCH_SIGNS
)

assert results == (
    (-2, -1, Fraction(0, 1)),
    (-2, 1, Fraction(-2, 1)),
)

output = {
    "record_id": RECORD_ID,
    "outcome": "NO_WITNESS_INCONCLUSIVE",
    "witness_description": "No unconditional witness: at x = -2 the derivative result depends on the unspecified real branch of arcsec.",
    "refutation_explanation": "The supplied text does not define a branch for arcsec. Exhausting the two possible local inverse-branch derivative signs at x = -2 gives derivative defect coefficients -2 and 0 in units of 1/sqrt(3), so one completion violates the claim while the other does not. Selecting one would invent a definition absent from the quote.",
    "search_space": "Exactly x in {-2} and local arcsec derivative sign in {-1, +1}, with the defect represented exactly as a rational coefficient of 1/sqrt(x^2-1).",
}
print(json.dumps(output, ensure_ascii=False, separators=(",", ":")))
