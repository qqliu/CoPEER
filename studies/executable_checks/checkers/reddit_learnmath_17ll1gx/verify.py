r"""Continuous functions map open sets to open sets."""

import json
from fractions import Fraction

RECORD_ID = "reddit_learnmath_17ll1gx"
ZERO = Fraction(0, 1)
ONE = Fraction(1, 1)
HALF = Fraction(1, 2)


def constant_map(_x):
    return ZERO


def in_domain(x):
    return ZERO < x and x < ONE


def continuity_certificate(a, x, epsilon):
    """Check the epsilon-delta construction delta=epsilon for this map."""
    if epsilon <= ZERO:
        return False
    delta = epsilon
    if abs(x - a) >= delta:
        return True
    return abs(constant_map(x) - constant_map(a)) < epsilon


def singleton_outsider(radius):
    """For every supplied positive radius, construct a point outside {0}."""
    if radius <= ZERO:
        raise ValueError("radius must be positive")
    point = ZERO + radius * HALF
    assert point != ZERO
    assert abs(point - ZERO) < radius
    return point


# (0,1) is a nonempty open interval; HALF supplies exact nonemptiness.
domain_is_open = ZERO < ONE
domain_is_nonempty = in_domain(HALF)

# The map is structurally constant.  Its output difference is identically zero,
# so delta=epsilon proves continuity for every positive epsilon.  These exact
# calls independently exercise that general construction at distinct points.
continuity_checks = (
    continuity_certificate(ZERO, HALF, ONE),
    continuity_certificate(Fraction(-3, 2), Fraction(7, 3), Fraction(1, 11)),
    continuity_certificate(Fraction(5, 4), Fraction(5, 4), Fraction(13, 9)),
)
function_is_continuous = all(continuity_checks)

# Constancy plus a nonempty domain makes the image exactly the singleton {0}.
image_contains_zero = in_domain(HALF) and constant_map(HALF) == ZERO
image_has_only_zero = all(
    constant_map(x) == ZERO
    for x in (Fraction(1, 4), HALF, Fraction(3, 4))
)
image_is_singleton_zero = image_contains_zero and image_has_only_zero

# The formula radius/2 (implemented by multiplication) works for every
# positive radius.  Exact instances also guard the certificate implementation.
radii = (ONE, Fraction(1, 7), Fraction(19, 5))
outsiders = tuple(singleton_outsider(radius) for radius in radii)
singleton_is_not_open = all(
    point != ZERO and abs(point - ZERO) < radius
    for point, radius in zip(outsiders, radii)
)

witness_valid = (
    domain_is_open
    and domain_is_nonempty
    and function_is_continuous
    and image_is_singleton_zero
    and singleton_is_not_open
)

if witness_valid:
    verdict = "CONFIRMED"
    notes = (
        "The constant real function maps the nonempty open interval (0,1) to "
        "{0}, which is not open in R. The refuted statement is substantive, "
        "not a typo."
    )
else:
    verdict = "CANNOT_REPRODUCE"
    notes = "The reported witness could not be established by exact recomputation."

print(json.dumps({
    "record_id": RECORD_ID,
    "verdict": verdict,
    "notes": notes,
}, separators=(",", ":")))
