r"""If an integer g divides both c and b, then g ≤ d, where d = gcd(ac,b)."""

import json


def nonnegative_gcd(left, right):
    left = abs(left)
    right = abs(right)
    while right != 0:
        left, right = right, left % right
    return left


def divides(divisor, value):
    assert divisor != 0
    return value % divisor == 0


a = -1
b = 0
c = 0
g = 1
product = a * c
d = nonnegative_gcd(product, b)

assert all(isinstance(value, int) for value in (a, b, c, g, product, d))
assert product == 0
assert d == 0
assert divides(g, c)
assert divides(g, b)
assert not (g <= d)

REPORT = {
    "record_id": "reddit_learnmath_lya4pm",
    "verdict": "CONFIRMED",
    "notes": "Exact recomputation confirms the witness: 1 divides both 0 and 0, while gcd((-1)·0,0)=0, so 1 ≤ 0 is false. The refuted statement is substantive, not plainly a typo; it omits the degenerate gcd(0,0) case (or an equivalent nonzero condition).",
}

assert REPORT["verdict"] == "CONFIRMED"
print(json.dumps(REPORT, ensure_ascii=False, separators=(",", ":")))
