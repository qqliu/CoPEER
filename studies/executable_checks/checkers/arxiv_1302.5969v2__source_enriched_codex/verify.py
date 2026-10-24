r"""Theorem 23septt3aa asserts that the set S is precompact even though its definition requires only that each individual u have some Hölder constant C, rather than imposing one uniform constant for the family."""

import json
from fractions import Fraction

RECORD_ID = "arxiv_1302.5969v2__source_enriched_codex"
VERDICT = "CONFIRMED"
NOTES = "Exact rational integration gives ||u_n||_1=1/2 and, with an algebraic certificate for every even scale 2^(n-m), ||u_n-u_m||_1=1/3; the individual Hölder bounds therefore produce an infinite separated subset of S. The refuted statement has a substantive missing uniformity hypothesis, not a plain typo."


def tent(x):
    integer_part = x.numerator // x.denominator
    remainder = x - integer_part
    reflected = Fraction(1, 1) - remainder
    if remainder <= reflected:
        return 2 * remainder
    return 2 * reflected


def affine_absolute_area(left_value, right_value, width):
    left_size = abs(left_value)
    right_size = abs(right_value)
    if left_value * right_value >= 0:
        return width * Fraction(left_size + right_size, 2)
    return width * Fraction(
        left_size * left_size + right_size * right_size,
        2 * (left_size + right_size),
    )


def tent_integral():
    half = Fraction(1, 2)
    return (
        affine_absolute_area(tent(Fraction(0, 1)), tent(half), half)
        + affine_absolute_area(tent(half), tent(Fraction(1, 1)), half)
    )


def exact_distance(scale):
    assert isinstance(scale, int) and scale > 0
    denominator = 2 * scale
    width = Fraction(1, denominator)
    total = Fraction(0, 1)
    for index in range(denominator):
        left = Fraction(index, denominator)
        right = Fraction(index + 1, denominator)
        left_difference = tent(left) - tent(scale * left)
        right_difference = tent(right) - tent(scale * right)
        total += affine_absolute_area(
            left_difference, right_difference, width
        )
    return total


# Polynomials in an indeterminate h, stored from constant coefficient upward.
def normalized(poly):
    result = list(poly)
    while len(result) > 1 and result[-1] == 0:
        result.pop()
    return tuple(result)


def poly_add(first, second):
    size = max(len(first), len(second))
    values = []
    for index in range(size):
        a = first[index] if index < len(first) else Fraction(0, 1)
        b = second[index] if index < len(second) else Fraction(0, 1)
        values.append(a + b)
    return normalized(values)


def poly_neg(poly):
    return tuple(-coefficient for coefficient in poly)


def poly_sub(first, second):
    return poly_add(first, poly_neg(second))


def poly_mul(first, second):
    values = [Fraction(0, 1)] * (len(first) + len(second) - 1)
    for first_index, first_value in enumerate(first):
        for second_index, second_value in enumerate(second):
            values[first_index + second_index] += first_value * second_value
    return normalized(values)


def poly_scale(poly, factor):
    return normalized(tuple(factor * coefficient for coefficient in poly))


def product(*polys):
    result = (Fraction(1, 1),)
    for poly in polys:
        result = poly_mul(result, poly)
    return result


one = (Fraction(1, 1),)
h = (Fraction(0, 1), Fraction(1, 1))
h_minus_one = (Fraction(-1, 1), Fraction(1, 1))
h_plus_one = (Fraction(1, 1), Fraction(1, 1))
two_h_minus_one = (Fraction(-1, 1), Fraction(2, 1))
two_h_plus_one = (Fraction(1, 1), Fraction(2, 1))
two_h_plus_three = (Fraction(3, 1), Fraction(2, 1))
four_h_minus_one = (Fraction(-1, 1), Fraction(4, 1))
four_h_plus_one = (Fraction(1, 1), Fraction(4, 1))

# These finite-difference identities prove the square-sum formulas by induction.
squares_before_h = poly_scale(
    product(h, h_minus_one, two_h_minus_one), Fraction(1, 6)
)
squares_through_h = poly_scale(
    product(h, h_plus_one, two_h_plus_one), Fraction(1, 6)
)
assert poly_sub(squares_through_h, squares_before_h) == poly_mul(h, h)
assert squares_before_h[0] == 0

odd_squares_through_h = poly_scale(
    product(h, two_h_minus_one, two_h_plus_one), Fraction(1, 3)
)
next_odd_sum = poly_scale(
    product(h_plus_one, two_h_plus_one, two_h_plus_three), Fraction(1, 3)
)
assert poly_sub(next_odd_sum, odd_squares_through_h) == poly_mul(
    two_h_plus_one, two_h_plus_one
)
assert odd_squares_through_h[0] == 0

# For scale N=2h, exact integration on its affine pieces splits into these
# two numerator sums. The identities hold as polynomials, hence for every h.
even_numerator_sum = poly_add(
    poly_scale(squares_before_h, Fraction(4, 1)),
    odd_squares_through_h,
)
odd_numerator_sum = poly_add(
    odd_squares_through_h,
    poly_scale(squares_through_h, Fraction(4, 1)),
)
assert even_numerator_sum == poly_scale(
    product(h, two_h_minus_one, four_h_minus_one), Fraction(1, 3)
)
assert odd_numerator_sum == poly_scale(
    product(h, two_h_plus_one, four_h_plus_one), Fraction(1, 3)
)

# Cancelling the positive factors in the two area sums leaves
# (4h-1)/(24h) + (4h+1)/(24h) = 1/3.
assert poly_add(four_h_minus_one, four_h_plus_one) == poly_scale(
    h, Fraction(8, 1)
)


def certified_even_distance(half_scale):
    assert isinstance(half_scale, int) and half_scale > 0
    scale = 2 * half_scale
    first_sum = Fraction(
        half_scale * (2 * half_scale - 1) * (4 * half_scale - 1), 3
    )
    second_sum = Fraction(
        half_scale * (2 * half_scale + 1) * (4 * half_scale + 1), 3
    )
    first_denominator = 2 * scale * scale * (scale - 1)
    second_denominator = 2 * scale * scale * (scale + 1)
    return (
        first_sum * Fraction(1, first_denominator)
        + second_sum * Fraction(1, second_denominator)
    )


assert tent_integral() == Fraction(1, 2)
for half_scale in range(1, 65):
    scale = 2 * half_scale
    assert certified_even_distance(half_scale) == Fraction(1, 3)
    assert exact_distance(scale) == certified_even_distance(half_scale)

# u_n is Lipschitz with constant 2 times 2^n. On an interval of length one,
# d <= sqrt(d) follows for 0 <= d <= 1 by squaring, so the same constant is
# an admissible individual Holder-1/2 constant. Integer periodicity changes
# every pairwise integral to exact_distance(2^(n-m)), an even scale.
assert Fraction(1, 2) <= Fraction(1, 1)
assert certified_even_distance(1) > 0

print(json.dumps({
    "record_id": RECORD_ID,
    "verdict": VERDICT,
    "notes": NOTES,
}, separators=(",", ":")))
