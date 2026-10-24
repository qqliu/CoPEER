"""Choosing each rational a_n from (pi - 1/n, pi) implies a_n < a_{n+1} for all n."""

import json
from fractions import Fraction


def alternating_atan_enclosure(argument, term_count):
    total = Fraction(0, 1)
    term_power = argument
    sign = 1
    square = argument * argument
    for index in range(term_count):
        total += term_power * Fraction(sign, 2 * index + 1)
        term_power *= square
        sign = -sign
    adjacent = total + term_power * Fraction(sign, 2 * term_count + 1)
    if total < adjacent:
        return total, adjacent
    return adjacent, total


# If u=atan(1/3), tan(2u)=3/4. Adding atan(1/7) gives
# tangent one because 3/4+1/7 = 1-(3/4)(1/7). All angles involved
# are positive and below pi/2, hence pi=8*atan(1/3)+4*atan(1/7).
assert Fraction(3, 4) + Fraction(1, 7) == 1 - Fraction(3, 28)
third_lo, third_hi = alternating_atan_enclosure(Fraction(1, 3), 20)
seventh_lo, seventh_hi = alternating_atan_enclosure(Fraction(1, 7), 20)
pi_lower = 8 * third_lo + 4 * seventh_lo
pi_upper = 8 * third_hi + 4 * seventh_hi
assert pi_lower < pi_upper

first = Fraction(8, 3)
second = Fraction(8, 3)
assert first < pi_lower
assert pi_upper < first + Fraction(1, 1)
assert second < pi_lower
assert pi_upper < second + Fraction(1, 2)
assert not first < second

# Independently recover an initial exact segment of the reported truncation
# tail. Each enclosure lies strictly inside one decimal cell, fixing the floor.
for index in range(3, 13):
    scale = 10 ** index
    cell = (pi_lower.numerator * scale) // pi_lower.denominator
    truncated = Fraction(cell, scale)
    assert truncated < pi_lower
    assert pi_upper < Fraction(cell + 1, scale)
    assert Fraction(1, scale) < Fraction(1, index)

# For every k>=3, irrationality of pi makes 10**k*pi nonintegral. Thus the
# floor definition gives 0 < pi-a_k < 1/10**k. The final inequality below
# holds for all such k by induction: 10**3>3, and 10**k>k implies
# 10**(k+1)=10*10**k>k+1.
def induction_step(index, ten_power):
    assert index >= 3
    assert ten_power > index
    following = 10 * ten_power
    assert following > index + 1
    return following


ten_power = 10 ** 3
assert ten_power > 3
for index in range(3, 13):
    ten_power = induction_step(index, ten_power)

REPORT = {
    "record_id": "reddit_learnmath_9hk957",
    "verdict": "CONFIRMED",
    "notes": "Exact rational bounds independently verify that 8/3 lies in both required intervals, so a_1=a_2 violates strict increase; the decimal-truncation tail is valid by the floor property and irrationality of pi. The refuted statement is substantive, not a typo.",
}
print(json.dumps(REPORT, separators=(",", ":")))
