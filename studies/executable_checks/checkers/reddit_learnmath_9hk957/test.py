"""Choosing each rational a_n from (pi - 1/n, pi) implies a_n < a_{n+1} for all n."""

import json
from fractions import Fraction
from itertools import product


def arctan_bounds(x, term_count):
    """Exact alternating-series bounds for arctan(x), with 0 < x <= 1."""
    partial = Fraction(0, 1)
    for k in range(term_count):
        exponent = 2 * k + 1
        sign = 1 if k % 2 == 0 else -1
        partial += sign * (x ** exponent) * Fraction(1, exponent)

    k = term_count
    exponent = 2 * k + 1
    sign = 1 if k % 2 == 0 else -1
    next_partial = partial + sign * (x ** exponent) * Fraction(1, exponent)
    return min(partial, next_partial), max(partial, next_partial)


# Machin's identity: pi = 16*arctan(1/5) - 4*arctan(1/239).
a_lo, a_hi = arctan_bounds(Fraction(1, 5), 12)
b_lo, b_hi = arctan_bounds(Fraction(1, 239), 12)
pi_lo = 16 * a_lo - 4 * b_hi
pi_hi = 16 * a_hi - 4 * b_lo


def compare_with_pi(value):
    """Return -1 or 1 when exact bounds certify value < pi or value > pi."""
    if value < pi_lo:
        return -1
    if value > pi_hi:
        return 1
    raise AssertionError("The fixed exact enclosure did not decide a comparison")


def in_required_interval(value, n):
    # value < pi and value + 1/n > pi are equivalent to
    # pi - 1/n < value < pi.
    return (
        compare_with_pi(value) == -1
        and compare_with_pi(value + Fraction(1, n)) == 1
    )


candidates = sorted(
    {Fraction(p, q) for p in range(13) for q in range(1, 5)}
)
witnesses = []

# Sweep the complete stated finite product without early termination.
for n in range(1, 5):
    for left, right in product(candidates, repeat=2):
        if (
            in_required_interval(left, n)
            and in_required_interval(right, n + 1)
            and not left < right
        ):
            witnesses.append((n, left, right))

assert witnesses
assert witnesses[0] == (1, Fraction(8, 3), Fraction(8, 3))

result = {
    "record_id": "reddit_learnmath_9hk957",
    "outcome": "WITNESS_FOUND",
    "witness_description": "Take a_1=a_2=8/3, and for every k>=3 take a_k=floor(10^k*pi)/10^k. This is a rational sequence with every a_k in (pi-1/k, pi).",
    "refutation_explanation": "The exact search certifies that 8/3 lies in both (pi-1, pi) and (pi-1/2, pi). For k>=3, irrationality of pi gives a_k<pi, while 0<pi-a_k<1/10^k<1/k. At n=1 the claimed conclusion is 8/3<8/3, which is false.",
    "search_space": "All n in {1,2,3,4} and all ordered pairs (x,y) in C^2, where C is the set of distinct fractions p/q with 0<=p<=12 and 1<=q<=4. Candidates were visited in increasing Fraction order, and the entire finite product was swept. Membership was certified using exact 12-term alternating-series bounds with Machin's identity pi=16*arctan(1/5)-4*arctan(1/239).",
}
print(json.dumps(result, separators=(",", ":")))
