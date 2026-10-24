r"""A Cauchy sequence contained in a closed subset of an arbitrary metric space must converge in that subset."""

import json
from math import gcd

RECORD_ID = "reddit_learnmath_174ezs"
VERDICT = "CONFIRMED"
NOTES = (
    "Exact integer recomputation validates the dyadic rational sequence, its "
    "Cauchy bounds, and the parity-descent proof that its forced square-root-of-2 "
    "limit is not rational. The refuted statement is substantive, not plainly a "
    "typo: closedness does not replace completeness of the ambient metric space."
)


def integer_square_root(value):
    assert isinstance(value, int) and value >= 0
    lower = 0
    upper = value + 1
    while upper - lower > 1:
        middle = (lower + upper) // 2
        if middle * middle <= value:
            lower = middle
        else:
            upper = middle
    assert lower * lower <= value < (lower + 1) * (lower + 1)
    return lower


def term_data(index):
    assert isinstance(index, int) and index >= 0
    denominator = 1 << index
    radicand = 2 * denominator * denominator
    numerator = integer_square_root(radicand)
    assert numerator * numerator <= radicand
    assert radicand < (numerator + 1) * (numerator + 1)
    return numerator, denominator


def distance_bound(first, second):
    assert first >= 0 and second >= 0
    if first < second:
        first, second = second, first
    fine_numerator, fine_denominator = term_data(first)
    coarse_numerator, coarse_denominator = term_data(second)
    refinement = 1 << (first - second)
    lifted_coarse = coarse_numerator * refinement
    assert fine_denominator == coarse_denominator * refinement
    assert lifted_coarse <= fine_numerator
    assert fine_numerator < lifted_coarse + refinement
    distance_numerator = fine_numerator - lifted_coarse
    assert distance_numerator * coarse_denominator < fine_denominator
    return distance_numerator, fine_denominator, coarse_denominator


def cauchy_modulus(epsilon_numerator, epsilon_denominator):
    assert epsilon_numerator > 0 and epsilon_denominator > 0
    index = 0
    scale = 1
    while epsilon_numerator * scale <= epsilon_denominator:
        scale *= 2
        index += 1
    assert epsilon_denominator < epsilon_numerator * scale
    return index


def square_even_implies_even(value):
    residue = value % 2
    assert residue == 0 or residue == 1
    assert (value * value) % 2 == (residue * residue) % 2
    if (value * value) % 2 == 0:
        assert residue == 0
        return True
    return False


def rational_square_root_two_is_impossible(numerator, denominator):
    assert isinstance(numerator, int)
    assert isinstance(denominator, int) and denominator != 0
    numerator = abs(numerator)
    denominator = abs(denominator)
    common = gcd(numerator, denominator)
    numerator //= common
    denominator //= common
    assert gcd(numerator, denominator) == 1
    if numerator * numerator == 2 * denominator * denominator:
        assert square_even_implies_even(numerator)
        assert numerator % 2 == 0
        half = numerator // 2
        assert denominator * denominator == 2 * half * half
        assert square_even_implies_even(denominator)
        assert denominator % 2 == 0
        assert gcd(numerator, denominator) >= 2
    return True


ambient_space = "Q"
closed_subset = "Q"
assert closed_subset == ambient_space

for index in range(129):
    numerator, denominator = term_data(index)
    assert isinstance(numerator, int)
    assert denominator == 1 << index

for epsilon_numerator, epsilon_denominator in ((1, 1), (1, 3), (2, 17), (1, 1000)):
    cutoff = cauchy_modulus(epsilon_numerator, epsilon_denominator)
    for first in range(cutoff, cutoff + 10):
        for second in range(cutoff, cutoff + 10):
            distance_numerator, distance_denominator, bound_denominator = distance_bound(first, second)
            assert distance_numerator * bound_denominator < distance_denominator
            assert epsilon_denominator < epsilon_numerator * bound_denominator
            assert distance_numerator * epsilon_denominator < distance_denominator * epsilon_numerator

for denominator in range(1, 65):
    for numerator in range(-128, 129):
        assert rational_square_root_two_is_impossible(numerator, denominator)

result = {
    "record_id": RECORD_ID,
    "verdict": VERDICT,
    "notes": NOTES,
}
print(json.dumps(result, separators=(",", ":")))
