r"""The proposed condition δ < min(1,(√3+√2)ε) guarantees |√x−√2| < ε whenever |x−2| < δ."""

import json
from fractions import Fraction

REPORT = {
    "record_id": "reddit_learnmath_1bbke99",
    "verdict": "CONFIRMED",
    "notes": "Independently confirmed with exact rational certificates: the witness satisfies δ<1, δ<(√3+√2)ε, and |x−2|<δ, while √2−√x>ε. The refuted statement is substantive, not plainly a typo.",
}

epsilon = Fraction(1, 20)
delta = Fraction(3, 20)
x = Fraction(93, 50)
one = Fraction(1, 1)
two = Fraction(2, 1)

assert epsilon > 0
assert x >= 0
assert delta < one
assert abs(x - two) == Fraction(7, 50)
assert abs(x - two) < delta

# Since (√3+√2)^2 = 5+2√6, it exceeds 3^2 exactly when
# √6>2; for nonnegative square roots that follows from 6>4.
root_sum_exceeds_three = Fraction(6, 1) > Fraction(4, 1)
assert root_sum_exceeds_three
assert delta == Fraction(3, 1) * epsilon
scaled_delta_condition = (
    epsilon > 0
    and delta == Fraction(3, 1) * epsilon
    and root_sum_exceeds_three
)
assert scaled_delta_condition

# Here x<2, so the radical distance is √2-√x. With
# 0<epsilon<√2, that distance exceeds epsilon exactly when
# (2+epsilon^2-x)^2 > 8 epsilon^2, provided the left side's
# unsquared term is positive. Every quantity below is rational.
epsilon_squared = epsilon * epsilon
term = two + epsilon_squared - x
assert x < two
assert epsilon_squared < two
assert term == Fraction(57, 400)
assert term > 0
assert term * term == Fraction(3249, 160000)
assert Fraction(8, 1) * epsilon_squared == Fraction(3200, 160000)
radical_gap_exceeds_epsilon = (
    term > 0
    and term * term > Fraction(8, 1) * epsilon_squared
)
assert radical_gap_exceeds_epsilon

print(json.dumps(REPORT, ensure_ascii=False, separators=(",", ":")))
