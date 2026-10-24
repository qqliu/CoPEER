r"""The left-hand expression in line 0009 equals the squared expression asserted in line 0011."""

import json
from fractions import Fraction

RECORD_ID = "reddit_learnmath_14nukd2"
CONFIRMED_NOTES = "Substantive algebraic error, not plainly a typo: at x = 1, exact recomputation gives 7/4 for line 0009's left side and 1/4 for line 0011's square."


def main():
    x = Fraction(1, 1)
    three_halves = Fraction(3, 2)

    line_0009_left = (x * x) - (three_halves * x) + (three_halves * three_halves)
    displacement = x - three_halves
    line_0011_square = displacement * displacement

    established = (
        line_0009_left == Fraction(7, 4)
        and line_0011_square == Fraction(1, 4)
        and line_0009_left != line_0011_square
    )

    if established:
        verdict = "CONFIRMED"
        notes = CONFIRMED_NOTES
    else:
        verdict = "CANNOT_REPRODUCE"
        notes = "Exact recomputation did not establish the reported counterexample."

    print(json.dumps({
        "record_id": RECORD_ID,
        "verdict": verdict,
        "notes": notes,
    }, separators=(",", ":")))


if __name__ == "__main__":
    main()
