"""For every positive integer n, 1^2 + 2^2 + … + n^2 = n(n + 1)(2n + 1)."""

import json

witnesses = []
for n in range(1, 101):
    left = sum(k * k for k in range(1, n + 1))
    right = n * (n + 1) * (2 * n + 1)
    if left != right:
        witnesses.append((n, left, right))

assert witnesses
assert witnesses[0] == (1, 1, 6)

result = {
    "record_id": "reddit_learnmath_1rh5gct",
    "outcome": "WITNESS_FOUND",
    "witness_description": "n = 1: the left-hand side is 1, while the right-hand side is 6.",
    "refutation_explanation": "The claim asserts equality for every positive integer n, but at n = 1, 1^2 = 1 whereas 1(1 + 1)(2(1) + 1) = 6, so the equality fails.",
    "search_space": "Every positive integer n in {1, 2, ..., 100}; all 100 values are checked in increasing order."
}
print(json.dumps(result, separators=(",", ":")))
