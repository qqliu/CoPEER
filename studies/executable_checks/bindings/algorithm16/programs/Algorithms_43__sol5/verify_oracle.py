#!/usr/bin/env python3
from fractions import Fraction

# Reported scalar instance: S = {x: a*x <= b} and candidate y.
a = -2
b = 1
y = -2

# The solution's displayed alternative formula says that, when b > 0,
# membership is decided by y*a <= b.
claimed_left_side = y * a
formula_accepts = claimed_left_side <= b

# Here a is negative, so a*x <= b is exactly x >= b/a.  Fraction keeps
# that endpoint exact.  Since y is negative, y*x is maximized at the least
# feasible x.
least_feasible_x = Fraction(-1, 2)
assert a * least_feasible_x == b
assert a < 0 and y < 0
exact_supremum = y * least_feasible_x
oracle_accepts = exact_supremum <= 1

# On this input the polar inequality y*x <= 1 is also literally the sole
# defining inequality a*x <= b, which independently certifies the universal
# condition for every feasible x.
same_universal_inequality = y == a and b == 1
assert same_universal_inequality
assert not formula_accepts
assert oracle_accepts

print("CONFIRMED: the explicit alternative polar formula rejects y=-2")
print("claimed test: y*a =", claimed_left_side, "<= b =", b, "is", formula_accepts)
print("exact oracle: sup(y*x over S) =", exact_supremum, "<= 1 is", oracle_accepts)
