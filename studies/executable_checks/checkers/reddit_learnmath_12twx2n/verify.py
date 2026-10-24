"""Continuity of f and g on X implies the existence of positive radii depending only on ε that work uniformly for every s in X."""

import json
from fractions import Fraction

RECORD_ID = "reddit_learnmath_12twx2n"
VERDICT = "CONFIRMED"
NOTES = (
    "The refuted statement is substantive, not a typo. On X=Q, both f(x)=x^2 "
    "and g(x)=0 are continuous, but the exact family s=n, u=n+1/(2n) "
    "defeats every positive uniform radius for ε=1."
)


def square_map(value):
    return value * value


def zero_map(value):
    del value
    return Fraction(0, 1)


def counterexample_below(rational_radius):
    if rational_radius <= 0:
        raise ValueError("radius must be positive")

    numerator = rational_radius.numerator
    denominator = rational_radius.denominator
    n = denominator // numerator + 1
    s = Fraction(n, 1)
    u = s + Fraction(1, 2 * n)

    distance = abs(u - s)
    variation = abs(square_map(u) - square_map(s))
    expected_variation = Fraction(1, 1) + Fraction(1, 4 * n * n)

    assert n > 0
    assert distance == Fraction(1, 2 * n)
    assert distance < rational_radius
    assert variation == expected_variation
    assert variation > Fraction(1, 1)
    assert variation > Fraction(1, 2)
    assert zero_map(u) == zero_map(s)


# This formula supplies the usual point-dependent continuity certificate for
# x -> x*x on Q. If |h| < delta <= 1, then
# |(x+h)*(x+h)-x*x| = |h|*|2*x+h| < delta*(2*|x|+1) <= tolerance.
def continuity_certificate(x, tolerance):
    if tolerance <= 0:
        raise ValueError("tolerance must be positive")
    scale = 2 * abs(x) + Fraction(1, 1)
    reciprocal_scale = Fraction(scale.denominator, scale.numerator)
    delta = min(Fraction(1, 1), tolerance * reciprocal_scale)
    assert delta > 0
    assert delta <= Fraction(1, 1)
    assert delta * scale <= tolerance


def main():
    for x, tolerance in (
        (Fraction(0, 1), Fraction(1, 2)),
        (Fraction(7, 3), Fraction(5, 11)),
        (Fraction(-19, 4), Fraction(2, 9)),
    ):
        continuity_certificate(x, tolerance)

    # Refuting every positive rational radius refutes every positive real
    # radius: below any positive real radius lies a positive rational one.
    for radius in (
        Fraction(1, 1),
        Fraction(2, 3),
        Fraction(1, 1000),
        Fraction(123, 4567),
    ):
        counterexample_below(radius)

    result = {
        "record_id": RECORD_ID,
        "verdict": VERDICT,
        "notes": NOTES,
    }
    print(json.dumps(result, ensure_ascii=False, separators=(",", ":")))


if __name__ == "__main__":
    main()
