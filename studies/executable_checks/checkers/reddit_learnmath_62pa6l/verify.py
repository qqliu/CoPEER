"""The transition from 4/3 - (4/3)(-2)^n to 4/3 - (2/3)(-2)^(n+1) is an equality."""

import json
from fractions import Fraction


def main():
    witness_n = 0
    four_thirds = Fraction(4, 3)
    two_thirds = Fraction(2, 3)
    base = -2

    first_value = four_thirds - four_thirds * (base ** witness_n)
    shifted_exponent = witness_n + 1
    second_value = four_thirds - two_thirds * (base ** shifted_exponent)

    expected_first = Fraction(0, 1)
    expected_second = Fraction(8, 3)
    if first_value != expected_first or second_value != expected_second:
        raise AssertionError("exact witness recomputation failed")
    if first_value == second_value:
        raise AssertionError("witness does not refute the equality")

    result = {
        "record_id": "reddit_learnmath_62pa6l",
        "verdict": "CONFIRMED",
        "notes": "Exact recomputation at n = 0 gives 0 for the first expression and 8/3 for the second, so the claimed equality fails. The refuted statement is plainly a sign typo, not a substantive mathematical claim."
    }
    print(json.dumps(result, separators=(",", ":")))


if __name__ == "__main__":
    main()
