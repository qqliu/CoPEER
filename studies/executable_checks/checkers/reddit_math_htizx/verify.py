"""For every positive integer n and k, x^(n-k)y^k is among the expanded terms of (x+y)^n, without requiring k≤n."""

import json

REPORT = {
    "record_id": "reddit_math_htizx",
    "verdict": "CONFIRMED",
    "notes": "Exact polynomial expansion at the positive-integer witness n=1, k=2 gives exponent pairs (1,0) and (0,1), so the claimed pair (-1,2) is absent. The refuted statement is substantive, not plainly a typo, because it explicitly says no k≤n restriction is required.",
}


def expand_binomial(exponent):
    coefficients = {(0, 0): 1}
    for _ in range(exponent):
        next_coefficients = {}
        for (x_degree, y_degree), coefficient in coefficients.items():
            x_term = (x_degree + 1, y_degree)
            y_term = (x_degree, y_degree + 1)
            next_coefficients[x_term] = next_coefficients.get(x_term, 0) + coefficient
            next_coefficients[y_term] = next_coefficients.get(y_term, 0) + coefficient
        coefficients = next_coefficients
    return coefficients


n = 1
k = 2
assert n > 0 and k > 0
expanded = expand_binomial(n)
claimed_pair = (n - k, k)
assert expanded == {(1, 0): 1, (0, 1): 1}
assert claimed_pair == (-1, 2)
assert claimed_pair not in expanded
assert REPORT["verdict"] == "CONFIRMED"
print(json.dumps(REPORT, separators=(",", ":")))
