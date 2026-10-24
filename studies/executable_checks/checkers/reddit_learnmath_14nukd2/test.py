"""The left-hand expression in line 0009 equals the squared expression asserted in line 0011."""

import json
from fractions import Fraction


def left_expression(x):
    three_halves = Fraction(3, 2)
    return x * x - three_halves * x + three_halves * three_halves


def squared_expression(x):
    three_halves = Fraction(3, 2)
    difference = x - three_halves
    return difference * difference


def main():
    witnesses = []
    for integer_x in range(-10, 11):
        x = Fraction(integer_x, 1)
        if left_expression(x) != squared_expression(x):
            witnesses.append(integer_x)

    if 1 in witnesses:
        result = {
            "record_id": "reddit_learnmath_14nukd2",
            "outcome": "WITNESS_FOUND",
            "witness_description": "x = 1: the line 0009 left-hand expression is 7/4, whereas (x - 3/2)^2 is 1/4.",
            "refutation_explanation": "Using exact arithmetic, 1^2 - (3/2)·1 + (3/2)^2 = 7/4, but (1 - 3/2)^2 = 1/4. Since 7/4 != 1/4, the asserted expression equality fails.",
            "search_space": "All 21 integer values x from -10 through 10 inclusive, swept in ascending order using fractions.Fraction exact arithmetic."
        }
    else:
        result = {
            "record_id": "reddit_learnmath_14nukd2",
            "outcome": "NO_WITNESS_EXHAUSTIVE",
            "witness_description": "No counterexample was found in the bounded search space.",
            "refutation_explanation": "Every tested value produced equal exact results.",
            "search_space": "All 21 integer values x from -10 through 10 inclusive, swept in ascending order using fractions.Fraction exact arithmetic."
        }

    print(json.dumps(result, ensure_ascii=False, separators=(",", ":")))


if __name__ == "__main__":
    main()
