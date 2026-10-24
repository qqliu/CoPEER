"""The proof claims that tan(x/2) ≠ 0 implies, for every integer n, 2πn < x < 2πn + π."""

import json
from fractions import Fraction

RECORD_ID = "proofwiki_92100__codex_expansion"
VERDICT = "CONFIRMED"
NOTES = "Independent exact arithmetic confirms the witness: x/2 = π/4, whose tangent is exactly 1 by the equal-leg right-triangle definition, while for n = 1 the lower inequality reduces (because π > 0) to 2 < 1/2, which is false. The refuted statement is plainly a quantifier typo—likely “there exists an integer n”—rather than a substantive failure of the likely intended theorem."


def halve(value):
    return Fraction(value.numerator, value.denominator * 2)


def exact_ratio(numerator, denominator):
    if denominator == 0:
        raise ZeroDivisionError("undefined ratio")
    return Fraction(
        numerator.numerator * denominator.denominator,
        numerator.denominator * denominator.numerator,
    )


def main():
    one = Fraction(1, 1)
    pi_coefficient = one
    right_angle = Fraction(1, 2)

    # In an isosceles right triangle, the two acute angles are equal and
    # together fill the angle left after subtracting the right angle from π.
    acute_angle = halve(pi_coefficient - right_angle)
    opposite_leg = one
    adjacent_leg = one
    tangent = exact_ratio(opposite_leg, adjacent_leg)

    x_coefficient = Fraction(1, 2)
    argument_of_tangent = halve(x_coefficient)
    premise = argument_of_tangent == acute_angle and tangent != 0

    n = 1
    lower_coefficient = Fraction(2 * n, 1)
    upper_coefficient = Fraction(2 * n + 1, 1)

    # Multiplication by positive π preserves the order of these coefficients.
    lower_inequality = lower_coefficient < x_coefficient
    upper_inequality = x_coefficient < upper_coefficient
    conclusion_at_n = lower_inequality and upper_inequality

    if tangent != one:
        raise AssertionError("the exact tangent identity was not established")
    if not premise or conclusion_at_n or lower_inequality or not upper_inequality:
        raise AssertionError("the reported witness was not independently verified")

    print(json.dumps(
        {"record_id": RECORD_ID, "verdict": VERDICT, "notes": NOTES},
        ensure_ascii=False,
        separators=(",", ":"),
    ))


if __name__ == "__main__":
    main()
