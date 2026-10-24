r"""For every natural number n, the stated finite-sum identity equals 3/2 - 1/n."""

import json
from math import gcd


def rational(numerator, denominator):
    if denominator == 0:
        raise ValueError("zero denominator")
    if denominator < 0:
        numerator = -numerator
        denominator = -denominator
    common = gcd(abs(numerator), denominator)
    return numerator // common, denominator // common


def add(first, second):
    return rational(
        first[0] * second[1] + second[0] * first[1],
        first[1] * second[1],
    )


def subtract(first, second):
    return rational(
        first[0] * second[1] - second[0] * first[1],
        first[1] * second[1],
    )


n = 2
left = rational(0, 1)
for k in range(1, n):
    left = add(left, rational(1, k * (k + 1)))
right = subtract(rational(3, 2), rational(1, n))

valid = n >= 1 and left == rational(1, 2) and right == rational(1, 1) and left != right
if valid:
    verdict = "CONFIRMED"
    notes = (
        "Exact rational recomputation at n = 2 gives sum_{k=1}^{n-1} "
        "1/(k(k+1)) = 1/2 and 3/2 - 1/n = 1, so the witness genuinely "
        "refutes the universal claim. The refuted statement is plainly a typo: "
        "the telescoping sum equals 1 - 1/n, not 3/2 - 1/n."
    )
else:
    verdict = "REFUTED_WITNESS_INVALID"
    notes = "The reported witness did not survive exact independent recomputation."

print(json.dumps({
    "record_id": "reddit_askmath_chxjkr",
    "verdict": verdict,
    "notes": notes,
}, separators=(",", ":")))
