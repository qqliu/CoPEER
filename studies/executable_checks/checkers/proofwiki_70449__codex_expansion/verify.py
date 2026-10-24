r"""For every nonzero rational x, the substitution n/x may be treated as tending to positive infinity as n tends to positive infinity."""

import json
from fractions import Fraction

record_id = "proofwiki_70449__codex_expansion"
notes = (
    "Exact recomputation confirms the substantive refutation (not a typo): "
    "x = -1 is a nonzero rational, and for every positive integer n, "
    "n/x = -n < 0. Thus the sequence cannot tend to positive infinity."
)

x = Fraction(-1, 1)
assert x != 0

# Compute the exact coefficient in n/x without using true division.
reciprocal_x = Fraction(x.denominator, x.numerator)
assert reciprocal_x == Fraction(-1, 1)

# For every positive integer n, multiplying n by this negative coefficient
# gives -n, which is strictly below zero. A sequence tending to positive
# infinity would eventually have to exceed zero.
def quotient_is_negative_for_every_positive_integer(coefficient):
    return coefficient.numerator < 0 and coefficient.denominator > 0

assert quotient_is_negative_for_every_positive_integer(reciprocal_x)
verdict = "CONFIRMED"

result = {
    "record_id": record_id,
    "verdict": verdict,
    "notes": notes,
}
print(json.dumps(result, separators=(",", ":")))
