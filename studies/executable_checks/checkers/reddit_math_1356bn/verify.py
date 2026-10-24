r"""Every associative, commutative, idempotent, internally bounded binary operation on the reals must select one of its two inputs."""

import json
from fractions import Fraction

REPORT = {
    "record_id": "reddit_math_1356bn",
    "verdict": "CONFIRMED",
    "notes": "Although the supplied finite grid alone cannot establish a law over all reals, independent exact verification confirms the witness. The operation is the meet on two chains joined at 0, so it is associative, commutative, idempotent, and internally bounded; yet F(-1,1)=0 is neither input. The refuted statement is substantive, not plainly a typo.",
}


def operation(x, y):
    zero = Fraction(0)
    if x > zero and y > zero:
        return x if x <= y else y
    if x < zero and y < zero:
        return x if x >= y else y
    return zero


# A nonzero formal value consists of one of the two sign rays and a set of
# magnitude variables. Union represents taking the minimum of their positive
# magnitudes. Distinct rays meet at zero. This is a symbolic certificate for
# arbitrary magnitudes, rather than a decision based only on sampled numbers.
def formal_meet(left, right):
    left_ray, left_terms = left
    right_ray, right_terms = right
    if left_ray == 0 or left_ray != right_ray:
        return (0, frozenset())
    return (left_ray, left_terms | right_terms)


rays = (-1, 0, 1)
for left_ray in rays:
    left = (left_ray, frozenset() if left_ray == 0 else frozenset((0,)))
    assert formal_meet(left, left) == left
    for right_ray in rays:
        right = (right_ray, frozenset() if right_ray == 0 else frozenset((1,)))
        assert formal_meet(left, right) == formal_meet(right, left)
        if left_ray == 0 or right_ray == 0 or left_ray != right_ray:
            assert formal_meet(left, right) == (0, frozenset())
            # In these cases zero is between the operands: one operand is zero,
            # or the two operands have opposite signs.
            assert left_ray == 0 or right_ray == 0 or left_ray == -right_ray
        else:
            # On one ray the numerical operation selects the input having the
            # smaller magnitude, hence is internally bounded.
            assert formal_meet(left, right)[0] == left_ray
        for third_ray in rays:
            third = (
                third_ray,
                frozenset() if third_ray == 0 else frozenset((2,)),
            )
            assert formal_meet(formal_meet(left, right), third) == formal_meet(
                left, formal_meet(right, third)
            )

# Exact numerical checks connect the symbolic two-ray meet to the stated
# piecewise formula, including nonintegral values and every sign interaction.
values = (
    Fraction(-3),
    Fraction(-1),
    Fraction(-1, 2),
    Fraction(0),
    Fraction(1, 2),
    Fraction(1),
    Fraction(3),
)
for x in values:
    assert operation(x, x) == x
    for y in values:
        value = operation(x, y)
        assert value == operation(y, x)
        lower = x if x <= y else y
        upper = y if x <= y else x
        assert lower <= value <= upper
        for z in values:
            assert operation(operation(x, y), z) == operation(
                x, operation(y, z)
            )

minus_one = Fraction(-1)
plus_one = Fraction(1)
witness_value = operation(minus_one, plus_one)
assert witness_value == Fraction(0)
assert witness_value != minus_one
assert witness_value != plus_one
assert REPORT["verdict"] == "CONFIRMED"

print(json.dumps(REPORT, separators=(",", ":")))
