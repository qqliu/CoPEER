"""The displayed magnitude bound on an error term implies that its derivative is O(z^{-1})."""

import json

RECORD_ID = "proofwiki_9436__codex_expansion"
VERDICT = "CONFIRMED"
NOTES = (
    "Exact symbolic recomputation confirms the witness: for e(z)=z and c=2, "
    "the displayed bound reduces to -2|z|<|z|<2|z|, while e'(z)=1 is not "
    "O(z^{-1}). The failure is plainly a reciprocal typo in the displayed "
    "bound (division by |z^{-1}| instead of multiplication), rather than a "
    "substantive asymptotic result."
)


def differentiate_monomial(coefficient, exponent):
    if not isinstance(coefficient, int) or not isinstance(exponent, int):
        raise AssertionError("the witness must use exact integer data")
    if exponent < 0:
        raise AssertionError("this checker only needs the reported polynomial")
    if exponent == 0:
        return 0, 0
    return coefficient * exponent, exponent - 1


def main():
    # Independently instantiate the reported witness e(z) = z and c = 2.
    coefficient = 1
    exponent = 1
    bound_constant = 2

    # Put r=|z|. For |z|>1, r is positive and
    # c/|z^{-1}| = c*r. Both strict inequalities therefore have a common
    # positive factor r and reduce to exact integer coefficient comparisons.
    if exponent != 1 or bound_constant <= 0:
        raise AssertionError("unexpected witness")
    lower_bound_holds_for_every_r = -bound_constant < abs(coefficient)
    upper_bound_holds_for_every_r = abs(coefficient) < bound_constant
    if not (lower_bound_holds_for_every_r and upper_bound_holds_for_every_r):
        raise AssertionError("the displayed bound was not established")

    derivative_coefficient, derivative_exponent = differentiate_monomial(
        coefficient, exponent
    )
    if (derivative_coefficient, derivative_exponent) != (1, 0):
        raise AssertionError("incorrect formal derivative")

    # If this derivative were O(r^{-1}), then after multiplying its bound by
    # r we would have r <= C for all sufficiently large positive real r.
    # Its exact comparison monomial is 1*r^1, whose positive coefficient and
    # positive integer exponent certify unbounded growth.
    comparison_coefficient = abs(derivative_coefficient)
    comparison_exponent = derivative_exponent + 1
    derivative_is_not_inverse_big_o = (
        comparison_coefficient > 0 and comparison_exponent > 0
    )
    if not derivative_is_not_inverse_big_o:
        raise AssertionError("the claimed asymptotic failure was not established")

    result = {
        "record_id": RECORD_ID,
        "verdict": VERDICT,
        "notes": NOTES,
    }
    print(json.dumps(result, separators=(",", ":")))


if __name__ == "__main__":
    main()
