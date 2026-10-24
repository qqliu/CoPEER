r"""For all positive integers n, 1/(2n-1) is less than 1/(8n-6)+1/(8n-4)+1/(8n-2)+1/(8n)."""

import json
from math import gcd

RECORD_ID = "reddit_learnmath_31qeyw"
VERDICT = "CONFIRMED"
NOTES = "The refuted statement is substantive, not plainly a typo. At the positive-integer witness n=2, exact integer arithmetic gives left = 1/3 = 560/1680 and right = 533/1680, so the required strict inequality fails by 9/560."


def normalized(numerator, denominator):
    if denominator <= 0:
        raise ValueError("denominator must be positive")
    divisor = gcd(abs(numerator), denominator)
    return numerator // divisor, denominator // divisor


def add(first, second):
    numerator = first[0] * second[1] + second[0] * first[1]
    denominator = first[1] * second[1]
    return normalized(numerator, denominator)


def subtract(first, second):
    numerator = first[0] * second[1] - second[0] * first[1]
    denominator = first[1] * second[1]
    return normalized(numerator, denominator)


n = 2
left = normalized(1, 2 * n - 1)
right = normalized(0, 1)
for denominator in (8 * n - 6, 8 * n - 4, 8 * n - 2, 8 * n):
    right = add(right, normalized(1, denominator))

gap = subtract(left, right)
claim_fails = (
    n > 0
    and left == (1, 3)
    and right == (533, 1680)
    and gap == (9, 560)
    and left[0] * right[1] >= right[0] * left[1]
)
if not claim_fails:
    raise RuntimeError("the reported witness was not independently verified")

result = {
    "record_id": RECORD_ID,
    "verdict": VERDICT,
    "notes": NOTES,
}
print(json.dumps(result, separators=(",", ":")))
