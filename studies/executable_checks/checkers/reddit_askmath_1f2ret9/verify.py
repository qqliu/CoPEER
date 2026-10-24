r"""The proof of theorem 1 applies its ε/|C| argument to every constant C, including C=0."""

from fractions import Fraction
import json


def verify_zero_witness():
    constant = int("0")
    epsilon = int("1")
    magnitude = abs(constant)
    if magnitude != 0:
        raise AssertionError("The proposed constant did not have zero magnitude")
    try:
        Fraction(epsilon, magnitude)
    except ZeroDivisionError:
        return
    raise AssertionError("An exact quotient with denominator zero was accepted")


def main():
    verify_zero_witness()
    result = {
        "record_id": "reddit_askmath_1f2ret9",
        "verdict": "CONFIRMED",
        "notes": "Exact recomputation at C=0 gives |C|=0, and the exact quantity ε/|C| is undefined. Thus the argument cannot apply to every constant as claimed. This is a substantive zero-denominator flaw, not plainly a typo.",
    }
    print(json.dumps(result, ensure_ascii=False, separators=(",", ":")))


if __name__ == "__main__":
    main()
