"""If an integer g divides both c and b, then g ≤ d, where d = gcd(ac,b)."""

import itertools
import json
import math

values = (-1, 0, 1)
divisors = (-1, 1)
violations = []

for a, b, c, g in itertools.product(values, values, values, divisors):
    d = math.gcd(a * c, b)
    if c % g == 0 and b % g == 0 and not (g <= d):
        violations.append((a, b, c, g, d))

assert violations
assert violations[0] == (-1, 0, 0, 1, 0)

result = {
    "record_id": "reddit_learnmath_lya4pm",
    "outcome": "WITNESS_FOUND",
    "witness_description": "a = -1, b = 0, c = 0, g = 1, and d = gcd(ac,b) = gcd(0,0) = 0.",
    "refutation_explanation": "Here g divides c and b since 1 divides 0, but g ≤ d is false because 1 ≤ 0 is false.",
    "search_space": "All 54 tuples (a,b,c,g) in {-1,0,1} × {-1,0,1} × {-1,0,1} × {-1,1}, in lexicographic product order; d is computed as the nonnegative gcd(ac,b), and every tuple is checked."
}

print(json.dumps(result, ensure_ascii=False, separators=(",", ":")))
