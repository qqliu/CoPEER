r"""If φ is an automorphism of a finitely generated group Γ and a nonzero character χ satisfies χ∘φ=rχ for some r≠0, then r=±1."""

import json
from fractions import Fraction

record_id = "arxiv_1312.2167v2__source_enriched_codex"
verdict = "CONFIRMED"
notes = "Exact arithmetic validates the Z^2 witness: the unimodular matrix defines an automorphism, the character is nonzero, χ∘φ=rχ, and r is nonzero and not ±1. The refuted statement is substantive, not plainly a typo."


def add(left, right):
    return (left[0] + right[0], left[1] + right[1])


def times_integer(value, integer):
    return (value[0] * integer, value[1] * integer)


def product(left, right):
    rational = left[0] * right[0] + Fraction(5, 1) * left[1] * right[1]
    radical = left[0] * right[1] + left[1] * right[0]
    return (rational, radical)


zero = (Fraction(0, 1), Fraction(0, 1))
one = (Fraction(1, 1), Fraction(0, 1))
minus_one = (Fraction(-1, 1), Fraction(0, 1))
alpha = (Fraction(-1, 2), Fraction(1, 2))
rate = (Fraction(3, 2), Fraction(1, 2))

# The matrix sends (x,y) to (2x+y,x+y). Its displayed integer
# inverse proves that it is an automorphism of the rank-two group Z^2.
matrix = ((2, 1), (1, 1))
inverse = ((1, -1), (-1, 2))
determinant = matrix[0][0] * matrix[1][1] - matrix[0][1] * matrix[1][0]
left_identity = (
    (matrix[0][0] * inverse[0][0] + matrix[0][1] * inverse[1][0],
     matrix[0][0] * inverse[0][1] + matrix[0][1] * inverse[1][1]),
    (matrix[1][0] * inverse[0][0] + matrix[1][1] * inverse[1][0],
     matrix[1][0] * inverse[0][1] + matrix[1][1] * inverse[1][1]),
)
right_identity = (
    (inverse[0][0] * matrix[0][0] + inverse[0][1] * matrix[1][0],
     inverse[0][0] * matrix[0][1] + inverse[0][1] * matrix[1][1]),
    (inverse[1][0] * matrix[0][0] + inverse[1][1] * matrix[1][0],
     inverse[1][0] * matrix[0][1] + inverse[1][1] * matrix[1][1]),
)
identity = ((1, 0), (0, 1))

# A linear character on Z^2 is determined by its values 1 and alpha on
# the standard generators. Equality on those generators proves equality
# of the two characters everywhere.
composed_first = add(times_integer(one, 2), alpha)
composed_second = add(one, alpha)
scaled_first = product(rate, one)
scaled_second = product(rate, alpha)

checks = (
    determinant == 1,
    left_identity == identity,
    right_identity == identity,
    one != zero,
    composed_first == scaled_first,
    composed_second == scaled_second,
    rate != zero,
    rate != one,
    rate != minus_one,
)
if not all(checks):
    raise AssertionError("the reported witness failed exact verification")

print(json.dumps({
    "record_id": record_id,
    "verdict": verdict,
    "notes": notes,
}, separators=(",", ":")))
