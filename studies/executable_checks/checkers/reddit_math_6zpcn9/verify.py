r"""If a_n/b_n tends to 0 and the series of b_n converges, then the series of a_n converges."""

from fractions import Fraction
import json

REPORT = {
    "record_id": "reddit_math_6zpcn9",
    "verdict": "CONFIRMED",
    "notes": "The witness is valid. The refuted statement is substantive, not a typo: convergence of the comparison series is only conditional, so a ratio tending to zero does not force convergence of the other series.",
}


def inv(x):
    assert x != 0
    return Fraction(x.denominator, x.numerator)


def h(m):
    assert isinstance(m, int) and m >= 1
    s = Fraction(0, 1)
    for j in range(1, m + 1):
        s += Fraction(1, j)
    return s


def sign(n):
    assert isinstance(n, int) and n >= 0
    return 1 if n % 2 == 0 else -1


def b(n):
    return Fraction(sign(n), n + 1)


def a(n):
    return Fraction(1, n + 1) * inv(h(n + 1))


# Recompute the displayed witness and its ratio using rational arithmetic.
assert b(0) == Fraction(1, 1)
assert b(1) == Fraction(-1, 2)
assert a(0) == Fraction(1, 1)
assert a(1) == Fraction(1, 3)
for n in range(64):
    assert a(n) * inv(b(n)) == Fraction(sign(n), 1) * inv(h(n + 1))

# For every r >= 0, the two consecutive b terms have the exact form
# 1/(2r+1) - 1/(2r+2), and the alternating-series remainder is bounded by
# 1/(N+2). That bound tends to zero, proving convergence of sum b_n.
for r in range(32):
    pair = b(2 * r) + b(2 * r + 1)
    expected_pair = Fraction(1, 2 * r + 1) - Fraction(1, 2 * r + 2)
    assert pair == expected_pair and pair > 0
for n in range(63):
    assert abs(b(n + 1)) < abs(b(n))

# Partition H_(2^k) into dyadic blocks. In block j, every denominator is at
# most 2^j, giving a contribution at least 1/2; it is greater than 2^(j-1),
# giving a contribution at most 1. Hence, for every k >= 1,
# 1+k/2 <= H_(2^k) <= 1+k. The lower bound tends to infinity, so the exact
# ratio sign(n)/H_(n+1) tends to zero.
for k in range(1, 13):
    endpoint = 1 << k
    assert Fraction(k + 2, 2) <= h(endpoint)
    assert h(endpoint) <= Fraction(k + 1, 1)

# If 2^(k-1) < m <= 2^k, then m <= 2^k and H_m <= H_(2^k) <= k+1.
# Thus the corresponding block of sum 1/(m H_m) has 2^(k-1) terms and is
# at least 1/(2(k+1)). The sum of these lower bounds diverges: grouping the
# indices k+1 dyadically gives a fixed positive lower bound per group.
for k in range(1, 11):
    left = (1 << (k - 1)) + 1
    right = 1 << k
    block = Fraction(0, 1)
    for m in range(left, right + 1):
        block += a(m - 1)
    assert block >= Fraction(1, 2 * (k + 1))

for r in range(1, 9):
    first_k = (1 << (r - 1)) - 1
    last_k = (1 << r) - 2
    comparison_group = Fraction(0, 1)
    for k in range(first_k, last_k + 1):
        comparison_group += Fraction(1, 2 * (k + 1))
    assert comparison_group >= Fraction(1, 4)

# The exact identities and universal dyadic estimates establish all three
# facts: sum b_n converges, a_n/b_n tends to zero, and sum a_n diverges.
assert REPORT["verdict"] == "CONFIRMED"
print(json.dumps(REPORT, separators=(",", ":")))
