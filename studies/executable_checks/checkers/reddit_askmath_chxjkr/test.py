"""For every natural number n, the stated finite-sum identity equals 3/2 - 1/n."""

import json
from fractions import Fraction

RECORD_ID = "reddit_askmath_chxjkr"
SEARCH_SPACE = (
    "All integers n from 2 through 100 inclusive, evaluated in increasing "
    "order with fractions.Fraction exact arithmetic."
)

violations = []
for n in range(2, 101):
    left = sum(
        (Fraction(1, k * (k + 1)) for k in range(1, n)),
        Fraction(0, 1),
    )
    right = Fraction(3, 2) - Fraction(1, n)
    if left != right:
        violations.append((n, left, right))

if not violations:
    raise AssertionError("Expected a counterexample in the bounded search space")

n, left, right = violations[0]
if (n, left, right) != (2, Fraction(1, 2), Fraction(1, 1)):
    raise AssertionError("Unexpected first counterexample")

result = {
    "record_id": RECORD_ID,
    "outcome": "WITNESS_FOUND",
    "witness_description": (
        "n = 2: the left-hand side is 1/2, while 3/2 - 1/n is 1."
    ),
    "refutation_explanation": (
        "The universal claim is false because at n = 2 the stated sum contains "
        "the single term 1/(1*2) = 1/2, but the claimed right-hand side is "
        "3/2 - 1/2 = 1, and 1/2 != 1."
    ),
    "search_space": SEARCH_SPACE,
}
print(json.dumps(result, sort_keys=True, separators=(",", ":")))
