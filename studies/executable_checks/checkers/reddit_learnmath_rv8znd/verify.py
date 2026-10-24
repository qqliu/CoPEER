r"""The product of two quotients with nonzero integer denominators is always nonzero."""

import json

REPORT = {
    "record_id": "reddit_learnmath_rv8znd",
    "verdict": "CONFIRMED",
    "notes": "Exact recomputation gives (-1)/(-1) = 1 and 0/(-1) = 0, so their product is 0 despite both integer denominators being nonzero. The refuted statement is substantive, not plainly a typo: a nonzero denominator ensures a quotient is defined, but does not ensure it is nonzero.",
}

def common_divisor(x, y):
    x = abs(x)
    y = abs(y)
    while y != 0:
        x, y = y, x % y
    return x

def reduced(numerator, denominator):
    assert type(numerator) is int
    assert type(denominator) is int
    assert denominator != 0
    if numerator == 0:
        return (0, 1)
    divisor = common_divisor(numerator, denominator)
    numerator //= divisor
    denominator //= divisor
    if denominator < 0:
        numerator = -numerator
        denominator = -denominator
    return (numerator, denominator)

left_written = (-1, -1)
right_written = (0, -1)

assert left_written[1] != 0 and right_written[1] != 0
left_exact = reduced(left_written[0], left_written[1])
right_exact = reduced(right_written[0], right_written[1])
assert left_exact == (1, 1)
assert right_exact == (0, 1)
product_exact = reduced(
    left_exact[0] * right_exact[0],
    left_exact[1] * right_exact[1],
)
assert product_exact == (0, 1)
assert REPORT["verdict"] == "CONFIRMED"

print(json.dumps(REPORT, separators=(",", ":")))
