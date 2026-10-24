r"""The formula sgn(x) = (abs(x)-x)/x + 1 defines the sign of a number without excluding zero."""

import json
from fractions import Fraction

witness = 0
numerator = abs(witness) - witness
denominator = witness

assert witness == 0
assert numerator == 0
assert denominator == 0

is_undefined = False
try:
    value = Fraction(numerator, denominator) + 1
except ZeroDivisionError:
    is_undefined = True

assert is_undefined

REPORT = {
    "record_id": "reddit_math_9x1ecs",
    "verdict": "CONFIRMED",
    "notes": "The witness x = 0 is valid: exact integer recomputation gives numerator 0 and denominator 0, and the resulting rational expression is undefined. The refuted statement has a substantive domain error, not a typo.",
}

assert REPORT["record_id"] == "reddit_math_9x1ecs"
assert REPORT["verdict"] == "CONFIRMED"
assert "substantive domain error, not a typo" in REPORT["notes"]
print(json.dumps(REPORT, separators=(",", ":")))
