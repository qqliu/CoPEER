r"""For a fixed irrational number, division by irrational numbers can produce only one possible rational result."""

import json
from fractions import Fraction

REPORT = {
    "record_id": "reddit_mathematics_1dz93wr",
    "verdict": "CONFIRMED",
    "notes": "Exact symbolic arithmetic verifies that the fixed irrational sqrt(2) divided by the distinct irrational divisors sqrt(2) and sqrt(2)/2 yields the distinct rational values 1 and 2. The refuted statement is substantive, not plainly a typo.",
}

ZERO = Fraction(0, 1)
ONE = Fraction(1, 1)
TWO = Fraction(2, 1)
HALF = Fraction(1, 2)

# By the rational-root theorem, these are all possible rational roots of
# the monic polynomial x*x - 2. None is a root, so it is irreducible over Q.
root_candidates = (
    Fraction(-2, 1),
    Fraction(-1, 1),
    Fraction(1, 1),
    Fraction(2, 1),
)
assert all(value * value - TWO != ZERO for value in root_candidates)
sqrt_two_is_irrational = True
assert sqrt_two_is_irrational

# A pair (a, b) denotes a + b*sqrt(2) in Q(sqrt(2)).
def reciprocal(value):
    assert value != ZERO
    return Fraction(value.denominator, value.numerator)


def divide(left, right):
    a, b = left
    c, d = right
    norm = c * c - TWO * d * d
    assert norm != ZERO
    inverse_norm = reciprocal(norm)
    rational_part = (a * c - TWO * b * d) * inverse_norm
    radical_part = (b * c - a * d) * inverse_norm
    return (rational_part, radical_part)


def is_rational(value):
    return value[1] == ZERO


alpha = (ZERO, ONE)
beta_one = (ZERO, ONE)
beta_two = (ZERO, HALF)

assert alpha[1] != ZERO and sqrt_two_is_irrational
assert beta_one[1] != ZERO and sqrt_two_is_irrational
assert beta_two[1] != ZERO and sqrt_two_is_irrational
assert beta_one != beta_two

quotient_one = divide(alpha, beta_one)
quotient_two = divide(alpha, beta_two)

assert quotient_one == (ONE, ZERO)
assert quotient_two == (TWO, ZERO)
assert is_rational(quotient_one)
assert is_rational(quotient_two)
assert quotient_one != quotient_two

print(json.dumps(REPORT, separators=(",", ":")))
