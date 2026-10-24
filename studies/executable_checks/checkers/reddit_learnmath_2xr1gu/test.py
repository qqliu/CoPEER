"""The inductive transition for the sum of squares obtains P(n+1) from P(n) by adding (n+1)."""

import json

RECORD_ID = "reddit_learnmath_2xr1gu"
WITNESS_DESCRIPTION = (
    "At n=1, the sum of squares through n is 1. Adding n+1=2 gives 3, "
    "whereas the sum of squares through n+1 is 1^2+2^2=5."
)
REFUTATION_EXPLANATION = (
    "The claimed transition requires 1+(1+1)=5 at n=1, but its left side is 3. "
    "The missing increment is (n+1)^2, not n+1."
)
SEARCH_SPACE = (
    "All integers n from 0 through 100 inclusive, checked in increasing order "
    "using exact integer sums of k^2."
)

violations = []
for n in range(101):
    current_sum = sum(k * k for k in range(1, n + 1))
    claimed_next_sum = current_sum + (n + 1)
    actual_next_sum = sum(k * k for k in range(1, n + 2))
    if claimed_next_sum != actual_next_sum:
        violations.append((n, current_sum, claimed_next_sum, actual_next_sum))

if not violations or violations[0] != (1, 1, 3, 5):
    raise AssertionError("deterministic exhaustive search did not find the expected witness")

result = {
    "record_id": RECORD_ID,
    "outcome": "WITNESS_FOUND",
    "witness_description": WITNESS_DESCRIPTION,
    "refutation_explanation": REFUTATION_EXPLANATION,
    "search_space": SEARCH_SPACE,
}
print(json.dumps(result, separators=(",", ":")))
