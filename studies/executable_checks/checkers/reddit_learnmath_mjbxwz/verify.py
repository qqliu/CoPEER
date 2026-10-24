r"""Every strictly increasing function f: R → R has an inverse f⁻¹: R → R."""

import json
from fractions import Fraction

REPORT = {
    "record_id": "reddit_learnmath_mjbxwz",
    "verdict": "CONFIRMED",
    "notes": "The witness is valid. The refuted statement is substantive, not plainly a typo: strict increase guarantees injectivity but not surjectivity onto R.",
}


def main():
    zero = Fraction(0, 1)
    left_shift = Fraction(-2, 1)
    right_shift = Fraction(-1, 1)
    omitted = Fraction(-2, 1)

    # Each branch has positive unit slope. Across the breakpoint, every left
    # value is below left_shift and every right value is at least right_shift.
    assert left_shift < right_shift
    assert left_shift < right_shift + zero

    # Solving f(x) = omitted on each affine branch gives its unique possible
    # preimage. Neither candidate belongs to the branch whose formula produced it.
    left_candidate = omitted - left_shift
    right_candidate = omitted - right_shift
    assert left_candidate == zero
    assert not left_candidate < zero
    assert right_candidate == Fraction(-1, 1)
    assert not right_candidate >= zero

    # Thus the reported function is strictly increasing but omits -2, so it
    # cannot possess an inverse with all of R as its domain.
    assert REPORT["verdict"] == "CONFIRMED"
    print(json.dumps(REPORT, separators=(",", ":")))


if __name__ == "__main__":
    main()
