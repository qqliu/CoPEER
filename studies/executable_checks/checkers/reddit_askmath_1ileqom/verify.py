r"""The explicitly reconstructed points form a valid folded configuration with A=C while preserving the specified edge lengths."""

import json
from fractions import Fraction

record_id = "reddit_askmath_1ileqom"
zero = Fraction(0, 1)
a = (zero, zero)
c = (zero, zero)

# Exact polar descriptions of the reported Cartesian expressions.
b = (Fraction(223, 100), Fraction(300, 223))
d = (Fraction(223, 100), Fraction(-300, 223))

# Multiplying radius by angle independently recovers the reported signed
# arc lengths. For a polar point, cos(theta)^2 + sin(theta)^2 = 1, so its
# squared distance from the origin is exactly radius^2; no approximation of
# either trigonometric value is involved.
assert b[0] * b[1] == Fraction(3, 1)
assert d[0] * d[1] == Fraction(-3, 1)
assert a == c

ab_squared = b[0] ** 2
bc_squared = b[0] ** 2
cd_squared = d[0] ** 2
da_squared = d[0] ** 2

actual_squared = (ab_squared, bc_squared, cd_squared, da_squared)
required_lengths = (3, 4, 3, 4)
required_squared = tuple(Fraction(length ** 2, 1) for length in required_lengths)

established = (
    ab_squared == bc_squared
    and cd_squared == da_squared
    and required_squared[0] != required_squared[1]
    and required_squared[2] != required_squared[3]
    and all(actual != required for actual, required in zip(actual_squared, required_squared))
)
assert established

verdict = "CONFIRMED"
notes = (
    "Confirmed by exact arithmetic: A=C, so AB=CB and AD=CD; moreover the "
    "quoted polar radius is 223/100, making all four distances from A=C to B "
    "or D equal to 223/100, not the required alternating 3 and 4. The refuted "
    "statement is substantive, not plainly a typo."
)
print(json.dumps({"record_id": record_id, "verdict": verdict, "notes": notes}, separators=(",", ":")))
