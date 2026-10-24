r"""For every positive integer a, the fraction 2a/(a+1) is not reducible."""

import json


def euclidean_gcd(left, right):
    while right != 0:
        left, right = right, left % right
    return left


candidate = 1
numerator = 2 * candidate
denominator = candidate + 1
common_divisor = euclidean_gcd(numerator, denominator)

if candidate > 0 and numerator == 2 and denominator == 2 and common_divisor == 2 and common_divisor > 1:
    verdict = "CONFIRMED"
    notes = "At the positive integer a = 1, the fraction is 2/2 and the independently computed gcd is 2, so it is reducible. The refuted universal statement is substantive, not plainly a typo."
else:
    verdict = "REFUTED_WITNESS_INVALID"
    notes = "The proposed witness did not independently verify. The refuted statement would be substantive, not plainly a typo."

print(json.dumps({
    "record_id": "reddit_mathematics_16ovrt9",
    "verdict": verdict,
    "notes": notes,
}, separators=(",", ":")))
