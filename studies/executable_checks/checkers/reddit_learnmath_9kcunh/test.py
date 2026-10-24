"""The proof claims that 4/(sqrt(n)+2) < 1/n for the relevant natural numbers n."""

import json
from fractions import Fraction


def claimed_inequality_holds(n):
    # For n >= 1, multiplying by the positive denominators gives
    # 4*n < sqrt(n) + 2. Since 4*n - 2 is positive, squaring yields
    # the exact equivalent integer comparison below.
    term = 4 * n - 2
    return term * term < n


search_values = tuple(range(1, 101))
violations = tuple(n for n in search_values if not claimed_inequality_holds(n))
witness = violations[0] if violations else None

assert witness == 1
assert Fraction(4, 1 + 2) > Fraction(1, 1)

result = {
    "record_id": "reddit_learnmath_9kcunh",
    "outcome": "WITNESS_FOUND",
    "witness_description": "n = 1 is a concrete natural-number witness.",
    "refutation_explanation": "For n = 1, sqrt(1) = 1, so 4/(sqrt(1)+2) = 4/3, while 1/n = 1. Since 4/3 is greater than 1, the claimed strict inequality is false.",
    "search_space": "All integers n from 1 through 100 inclusive were checked in increasing order using the exact equivalent comparison (4n-2)^2 < n."
}

print(json.dumps(result, separators=(",", ":")))
