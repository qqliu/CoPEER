r"""Almost-everywhere pointwise convergence under an integrable dominating function implies uniform convergence on the complement of the exceptional null set."""

import json
from fractions import Fraction

REPORT = {
    "record_id": "reddit_askmath_19cjnep",
    "verdict": "CONFIRMED",
    "notes": "The refuted statement is substantive, not a typo: the shrinking-spike sequence is dominated and converges pointwise everywhere, but its uniform error remains exactly 1.",
}

ZERO = Fraction(0, 1)
ONE = Fraction(1, 1)
EPSILON = Fraction(1, 2)


def spike(n, x):
    assert isinstance(n, int) and n >= 1
    assert isinstance(x, Fraction) and ZERO <= x <= ONE
    return ONE if ZERO < x < Fraction(1, n) else ZERO


# The proposed dominator is g=1. Its exact integral on [0,1] is 1,
# and the spike definition only returns 0 or 1.
domain_length = ONE - ZERO
dominating_integral = ONE * domain_length
assert dominating_integral == ONE
for n in range(1, 65):
    for x in (ZERO, Fraction(1, 7), Fraction(1, 2), ONE):
        assert ZERO <= spike(n, x) <= ONE


# At x=0 every term is zero. For any fixed x>0, the Archimedean
# choice N=floor(1/x)+1 has N*x>1. Thus 1/n <= 1/N < x for every
# n>=N, so every term from N onward is zero. The following exact
# certificate recomputes that construction for rational representatives.
def eventual_zero_certificate(x):
    assert isinstance(x, Fraction) and ZERO <= x <= ONE
    if x == ZERO:
        return spike(1, x) == ZERO
    threshold = x.denominator // x.numerator + 1
    return threshold * x > ONE and spike(threshold, x) == ZERO


for x in (
    ZERO,
    Fraction(1, 101),
    Fraction(2, 17),
    Fraction(1, 2),
    ONE,
):
    assert eventual_zero_certificate(x)


# The exceptional set is empty, so it is null and its complement is [0,1].
exceptional_measure = ZERO
assert exceptional_measure == ZERO


# For every positive integer n, x_n=1/(2n) lies strictly inside
# (0,1/n), and hence the error there is exactly 1. Taking epsilon=1/2
# therefore disproves uniform convergence. This certificate uses only
# exact integer and rational arithmetic.
def uniform_failure_certificate(n):
    assert isinstance(n, int) and n >= 1
    x_n = Fraction(1, 2 * n)
    upper_endpoint = Fraction(1, n)
    return (
        ZERO < x_n < upper_endpoint <= ONE
        and spike(n, x_n) == ONE
        and spike(n, x_n) > EPSILON
    )


for n in range(1, 257):
    assert uniform_failure_certificate(n)

assert REPORT["record_id"] == "reddit_askmath_19cjnep"
assert REPORT["verdict"] == "CONFIRMED"
print(json.dumps(REPORT, ensure_ascii=False, separators=(",", ":")))
