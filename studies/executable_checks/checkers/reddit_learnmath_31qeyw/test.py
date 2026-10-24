"""For all positive integers n, 1/(2n-1) is less than 1/(8n-6)+1/(8n-4)+1/(8n-2)+1/(8n)."""

import json
from fractions import Fraction

RECORD_ID = "reddit_learnmath_31qeyw"
LIMIT = 10000
WITNESS_DESCRIPTION = "n=2 is a counterexample."
REFUTATION_EXPLANATION = (
    "At n=2, the left side is 1/3 = 560/1680, while the right side is "
    "1/10+1/12+1/14+1/16 = 533/1680. Thus 1/3 is greater than, not "
    "less than, the right side (by 9/560)."
)
SEARCH_SPACE = (
    "All positive integers n with 1 <= n <= 10000, in increasing order "
    "(10,000 cases), using fractions.Fraction exact arithmetic."
)

first_counterexample = None
for n in range(1, LIMIT + 1):
    left = Fraction(1, 2 * n - 1)
    right = (
        Fraction(1, 8 * n - 6)
        + Fraction(1, 8 * n - 4)
        + Fraction(1, 8 * n - 2)
        + Fraction(1, 8 * n)
    )
    if left >= right and first_counterexample is None:
        first_counterexample = n

assert first_counterexample == 2
assert Fraction(1, 3) == Fraction(560, 1680)
assert Fraction(1, 10) + Fraction(1, 12) + Fraction(1, 14) + Fraction(1, 16) == Fraction(533, 1680)
assert Fraction(1, 3) - Fraction(533, 1680) == Fraction(9, 560)

result = {
    "record_id": RECORD_ID,
    "outcome": "WITNESS_FOUND",
    "witness_description": WITNESS_DESCRIPTION,
    "refutation_explanation": REFUTATION_EXPLANATION,
    "search_space": SEARCH_SPACE,
}
print(json.dumps(result, separators=(",", ":")))
