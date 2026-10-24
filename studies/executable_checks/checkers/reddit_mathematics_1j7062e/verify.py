r"""Applying the displayed argument to √16 establishes a common factor of p and q and concludes that √16 is irrational."""

import json

REPORT = {
    "record_id": "reddit_mathematics_1j7062e",
    "verdict": "CONFIRMED",
    "notes": "Exact arithmetic verifies the witness p = 4, q = 1: it is nonnegative, satisfies p² = 16q², and has gcd(p, q) = 1. Thus √16 = 4 is rational and the alleged nontrivial common factor does not exist. The refuted statement is a substantive mathematical error, not plainly a typo."
}


def integer_gcd(a, b):
    a = abs(a)
    b = abs(b)
    while b != 0:
        a, b = b, a % b
    return a


p = 4
q = 1
radicand = 16

assert p >= 0
assert q > 0
assert p * p == radicand * q * q
assert integer_gcd(p, q) == 1
assert p == 4 * q
assert not (integer_gcd(p, q) > 1)

print(json.dumps(REPORT, separators=(",", ":")))
