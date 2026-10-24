"""The proof claims that the function F(x)=∫₁ˣ(1/t)dt is identically equal to e^x."""

import json
from fractions import Fraction

RECORD_ID = "proofwiki_116604__codex_expansion"
VERDICT = "CONFIRMED"
NOTES = (
    "At x = 1, the equal-endpoint integral is exactly 0, while the "
    "exponential series gives e^1 >= 1 + 1 = 2 > 0. Thus the claimed "
    "identity fails on the reported witness. The refuted statement is "
    "substantive as written, not plainly a typo."
)


def integral_at_equal_endpoints(lower, upper):
    if lower != upper:
        raise ValueError("This certificate only evaluates an equal-endpoint integral")
    return Fraction(0, 1)


def verify_witness():
    witness = 1
    integral_value = integral_at_equal_endpoints(witness, witness)

    # For e^1 = sum_{n>=0} 1/n!, every term is positive. Its first two
    # terms therefore give the exact rational lower bound 1 + 1 = 2.
    first_series_terms = (Fraction(1, 1), Fraction(1, 1))
    exponential_lower_bound = sum(first_series_terms, Fraction(0, 1))

    return (
        integral_value == Fraction(0, 1)
        and exponential_lower_bound == Fraction(2, 1)
        and exponential_lower_bound > integral_value
    )


def main():
    if not verify_witness():
        raise AssertionError("Exact witness verification failed")
    result = {
        "record_id": RECORD_ID,
        "verdict": VERDICT,
        "notes": NOTES,
    }
    print(json.dumps(result, ensure_ascii=False, separators=(",", ":")))


if __name__ == "__main__":
    main()
