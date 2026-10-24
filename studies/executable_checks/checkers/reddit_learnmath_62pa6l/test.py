"""The transition from 4/3 - (4/3)(-2)^n to 4/3 - (2/3)(-2)^(n+1) is an equality."""

import json
from fractions import Fraction


def first_expression(n):
    return Fraction(4, 3) - Fraction(4, 3) * ((-2) ** n)


def second_expression(n):
    return Fraction(4, 3) - Fraction(2, 3) * ((-2) ** (n + 1))


def main():
    bounded_space = (0,)
    witness = None
    for n in bounded_space:
        left = first_expression(n)
        right = second_expression(n)
        if left != right:
            witness = (n, left, right)
            break

    if witness != (0, Fraction(0, 1), Fraction(8, 3)):
        raise AssertionError("deterministic exhaustive search produced an unexpected result")

    result = {
        "record_id": "reddit_learnmath_62pa6l",
        "outcome": "WITNESS_FOUND",
        "witness_description": "n = 0: the first expression is 0, while the second expression is 8/3.",
        "refutation_explanation": "Substituting n = 0 gives 4/3 - (4/3)(-2)^0 = 0 but 4/3 - (2/3)(-2)^(0+1) = 8/3, so the asserted equality fails.",
        "search_space": "All integers n in the bounded set {0}."
    }
    print(json.dumps(result, separators=(",", ":")))


if __name__ == "__main__":
    main()
