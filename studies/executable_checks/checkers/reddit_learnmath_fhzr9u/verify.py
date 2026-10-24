r"""An invertible complex matrix must have determinant 1."""

import json
from fractions import Fraction

REPORT = {
    "record_id": "reddit_learnmath_fhzr9u",
    "verdict": "CONFIRMED",
    "notes": "The witness is valid: [[2]] has the exact inverse [[1/2]] and determinant 2, not 1. The refuted statement is substantive, not plainly a typo.",
}


def complex_multiply(left, right):
    left_real, left_imaginary = left
    right_real, right_imaginary = right
    return (
        left_real * right_real - left_imaginary * right_imaginary,
        left_real * right_imaginary + left_imaginary * right_real,
    )


entry = (Fraction(2), Fraction(0))
inverse_entry = (Fraction(1, 2), Fraction(0))
identity_entry = (Fraction(1), Fraction(0))
determinant = entry

assert complex_multiply(entry, inverse_entry) == identity_entry
assert complex_multiply(inverse_entry, entry) == identity_entry
assert determinant != identity_entry
assert REPORT["verdict"] == "CONFIRMED"

print(json.dumps(REPORT, separators=(",", ":")))
