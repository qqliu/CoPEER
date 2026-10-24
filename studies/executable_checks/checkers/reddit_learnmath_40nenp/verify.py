r"""A rational number a/b in [0,1] must satisfy digits(a) < digits(b)."""

import json


def count_decimal_digits(value):
    if value < 0:
        value = -value
    count = 1
    while value >= 10:
        value //= 10
        count += 1
    return count


a = 1
b = 2
in_unit_interval = b > 0 and 0 <= a and a <= b
claimed_inequality = count_decimal_digits(a) < count_decimal_digits(b)
witness_refutes_claim = in_unit_interval and not claimed_inequality

if witness_refutes_claim:
    verdict = "CONFIRMED"
    notes = "The witness is valid: with a = 1 and b = 2, exact integer comparisons establish 0 <= a/b <= 1, while both integers have one decimal digit, so digits(a) < digits(b) is false. The refuted statement is a substantive mathematical error, not plainly a typo."
else:
    verdict = "REFUTED_WITNESS_INVALID"
    notes = "The proposed witness does not establish the claimed refutation. The statement appears substantive rather than plainly a typo."

print(json.dumps({
    "record_id": "reddit_learnmath_40nenp",
    "verdict": verdict,
    "notes": notes,
}, separators=(",", ":")))
