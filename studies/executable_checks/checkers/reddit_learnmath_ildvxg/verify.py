r"""The proposed g is a function from [0,1) into P(N)."""

import json
from fractions import Fraction


def geometric_sum(first_term, ratio):
    assert first_term >= 0
    assert 0 <= ratio < 1
    remaining = ratio.denominator - ratio.numerator
    assert remaining > 0
    return first_term * Fraction(ratio.denominator, remaining)


def prefix_integer(digits):
    value = 0
    for digit in digits:
        assert 0 <= digit <= 9
        value = value * 10 + digit
    return value


terminating_value = Fraction(1, 10)
repeating_nines_value = geometric_sum(Fraction(9, 100), Fraction(1, 10))
assert terminating_value == repeating_nines_value
assert 0 <= terminating_value < 1

terminating_digits = (1, 0, 0, 0)
repeating_digits = (0, 9, 9, 9)

assert prefix_integer(terminating_digits[:1]) == 1
assert prefix_integer(terminating_digits[:3]) == 100
assert prefix_integer(terminating_digits[:4]) == 1000
assert prefix_integer(repeating_digits[:1]) == 0
assert prefix_integer(repeating_digits[:3]) == 99
assert prefix_integer(repeating_digits[:4]) == 999

separator = 1
assert prefix_integer(terminating_digits[:1]) == separator
assert prefix_integer(repeating_digits[:1]) != separator

# Under the displayed rule, the other admitted prefix lengths are 3, 4, ... .
# The length-three prefix of 0.0999... is 99. Each later one is obtained
# from its predecessor p by 10*p+9, which remains at least 99. Hence none is 1.
smallest_later_repeating_prefix = prefix_integer(repeating_digits[:3])
assert smallest_later_repeating_prefix == 99
assert smallest_later_repeating_prefix > separator
assert 10 * smallest_later_repeating_prefix + 9 > smallest_later_repeating_prefix
assert separator not in (prefix_integer(repeating_digits[:1]),)

REPORT = {
    "record_id": "reddit_learnmath_ildvxg",
    "verdict": "CONFIRMED",
    "notes": "Exact arithmetic confirms that 0.1000... and 0.0999... both represent 1/10, while the stated prefix rule includes 1 in the first image and excludes it from the second. This is a substantive well-definedness failure, not a typo.",
}

print(json.dumps(REPORT, separators=(",", ":")))
