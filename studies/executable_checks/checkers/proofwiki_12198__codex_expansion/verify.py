"""The formula sqrt(a_1^2+a_2^2) defines a norm on C^2, in particular satisfying norm(x)=0 iff x=0."""

import json
from math import isqrt

RECORD_ID = "proofwiki_12198__codex_expansion"
VERDICT = "CONFIRMED"
NOTES = "The refuted statement is substantive as written: the nonzero vector (1, i) has 1^2 + i^2 = 0, so the proposed formula is zero there. The likely intended use of absolute-value squares would be a mathematical correction, not merely a plainly identifiable textual typo."


def multiply_gaussian(left, right):
    left_real, left_imag = left
    right_real, right_imag = right
    return (
        left_real * right_real - left_imag * right_imag,
        left_real * right_imag + left_imag * right_real,
    )


def main():
    one = (1, 0)
    imaginary_unit = (0, 1)
    zero = (0, 0)
    vector = (one, imaginary_unit)

    first_square = multiply_gaussian(vector[0], vector[0])
    second_square = multiply_gaussian(vector[1], vector[1])
    radicand = (
        first_square[0] + second_square[0],
        first_square[1] + second_square[1],
    )

    vector_is_nonzero = vector != (zero, zero)
    if not vector_is_nonzero:
        raise AssertionError("the proposed witness is the zero vector")
    if first_square != (1, 0):
        raise AssertionError("incorrect exact square of 1")
    if second_square != (-1, 0):
        raise AssertionError("incorrect exact square of i")
    if radicand != zero:
        raise AssertionError("the exact radicand is not zero")

    square_root_of_zero = isqrt(radicand[0])
    if square_root_of_zero != 0 or (square_root_of_zero, 0) != zero:
        raise AssertionError("the square root of zero was not zero")

    result = {
        "record_id": RECORD_ID,
        "verdict": VERDICT,
        "notes": NOTES,
    }
    print(json.dumps(result, separators=(",", ":")))


if __name__ == "__main__":
    main()
