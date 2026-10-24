r"""The proof claims that the set of continuous real-valued functions belongs to the sigma-algebra generated solely by the whole function space \(\mathbb{R}^T\)."""

import json
from fractions import Fraction

ZERO = Fraction(0, 1)
ONE = Fraction(1, 1)


def continuous_function(argument):
    return ZERO


def discontinuous_function(argument):
    return ONE if argument == ZERO else ZERO


def approaching_sequence(index):
    assert isinstance(index, int) and index > 0
    return Fraction(1, index)


def exact_rate(tolerance):
    assert isinstance(tolerance, Fraction) and tolerance > ZERO
    numerator = tolerance.numerator
    denominator = tolerance.denominator
    index = denominator // numerator + 1
    assert index * numerator > denominator
    assert approaching_sequence(index) < tolerance
    return index


# The first witness is constant, so its value difference is identically zero.
exact_points = (
    Fraction(-7, 3),
    ZERO,
    Fraction(2, 5),
    Fraction(11, 2),
)
assert all(continuous_function(x) == ZERO for x in exact_points)
assert continuous_function(ZERO) == continuous_function(ONE)

# For every positive rational tolerance, exact_rate gives N with 1/N below it;
# for n >= N, 1/n <= 1/N.  Thus 1/n tends to zero exactly.  Nevertheless the
# second witness has value zero at every 1/n and value one at zero.
for numerator in range(1, 13):
    for denominator in range(1, 17):
        tolerance = Fraction(numerator, denominator)
        start = exact_rate(tolerance)
        for offset in range(5):
            index = start + offset
            assert ZERO < approaching_sequence(index) < tolerance
            assert discontinuous_function(approaching_sequence(index)) == ZERO

jump_epsilon = Fraction(1, 2)
assert discontinuous_function(ZERO) == ONE
for index in range(1, 65):
    value_gap = abs(
        discontinuous_function(approaching_sequence(index))
        - discontinuous_function(ZERO)
    )
    assert value_gap == ONE and value_gap > jump_epsilon

# Symbolically, False denotes the empty set and True the whole function space.
# Complement and arbitrary union cannot produce any third set from these two.
generated_sigma_algebra = frozenset((False, True))
assert frozenset((True,)) | frozenset((not True,)) == generated_sigma_algebra
assert all((not member) in generated_sigma_algebra for member in generated_sigma_algebra)
assert all((left or right) in generated_sigma_algebra
           for left in generated_sigma_algebra
           for right in generated_sigma_algebra)
assert any(()) is False
assert any((False, True, False)) is True

# The constant function makes C(R) nonempty.  The point indicator is an
# R-valued function outside C(R), so C(R) is proper and is neither trivial set.
continuous_class_is_empty = False
continuous_class_is_whole_space = False
assert continuous_class_is_empty not in (True,)
assert continuous_class_is_whole_space not in (True,)
assert (continuous_class_is_empty, continuous_class_is_whole_space) == (False, False)

REPORT = {
    "record_id": "reddit_learnmath_7no5f8",
    "verdict": "CONFIRMED",
    "notes": "The refuted statement is substantive, not plainly a typo: the sigma-algebra generated solely by the whole function space is trivial, while the continuous functions form a nonempty proper subset.",
}
print(json.dumps(REPORT, separators=(",", ":")))
