r"""The exponent-reassociation step (-1)^(2/2) = ((-1)^2)^(1/2) is valid."""

import json

REPORT = {
    "record_id": "reddit_learnmath_fuwmpf",
    "verdict": "CONFIRMED",
    "notes": "Exact integer arithmetic gives 2/2 = 1, so the left side is -1; the principal nonnegative square root of (-1)^2 = 1 is 1. Thus the witness genuinely refutes the reassociation. The refuted statement is substantive, not plainly a typo.",
}

def integer_power(base, exponent):
    assert isinstance(exponent, int) and exponent >= 0
    result = 1
    factor = base
    remaining = exponent
    while remaining:
        if remaining % 2:
            result *= factor
        factor *= factor
        remaining //= 2
    return result

def principal_square_root(value):
    assert isinstance(value, int) and value >= 0
    candidate = 0
    while candidate * candidate < value:
        candidate += 1
    assert candidate * candidate == value
    return candidate

base = -1
numerator = 2
denominator = 2
quotient, remainder = divmod(numerator, denominator)
assert remainder == 0
left = integer_power(base, quotient)
inner = integer_power(base, numerator)
right = principal_square_root(inner)
assert quotient == 1
assert left == -1
assert inner == 1
assert right == 1
assert left != right
assert REPORT["verdict"] == "CONFIRMED"
print(json.dumps(REPORT, separators=(",", ":")))
