"""The expression 128 + 0x - 6x^2 - (1/2)x^3 equals 128 - (1/2)(12 - x)x^2."""

import json
from fractions import Fraction


def left_side(x):
    return 128 + 0 * x - 6 * x * x - Fraction(1, 2) * x * x * x


def right_side(x):
    return 128 - Fraction(1, 2) * (12 - x) * x * x


def main():
    search_values = (0, 1)
    witness = None
    for x in search_values:
        if left_side(x) != right_side(x):
            witness = x
            break

    if witness != 1:
        raise AssertionError("expected the unique searched counterexample x = 1")

    result = {
        "record_id": "reddit_math_17jli96",
        "outcome": "WITNESS_FOUND",
        "witness_description": "x = 1, for which the left-hand side is 243/2 and the right-hand side is 245/2.",
        "refutation_explanation": "At x = 1, 128 + 0x - 6x^2 - (1/2)x^3 = 243/2, while 128 - (1/2)(12 - x)x^2 = 245/2. Since 243/2 != 245/2, the claimed equality is false.",
        "search_space": "The ordered integer set {0, 1}; both values were checked in order, with the counterexample occurring at the final value x = 1."
    }
    print(json.dumps(result))


if __name__ == "__main__":
    main()
