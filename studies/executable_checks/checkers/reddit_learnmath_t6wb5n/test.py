"""The final equality |(x-2)(x+2)|/(4x^2) = |x-2||x+2|/(x^2) in line 0013 is valid."""

import json
from fractions import Fraction


def evaluate(x):
    left = Fraction(abs((x - 2) * (x + 2)), 4 * x * x)
    right = Fraction(abs(x - 2) * abs(x + 2), x * x)
    return left, right


def main():
    search_values = tuple(x for x in range(-2, 3) if x != 0)
    violations = []
    for x in search_values:
        left, right = evaluate(x)
        if left != right:
            violations.append((x, left, right))

    first_x, first_left, first_right = violations[0]
    assert first_x == -1
    assert first_left == Fraction(3, 4)
    assert first_right == Fraction(3, 1)

    result = {
        "record_id": "reddit_learnmath_t6wb5n",
        "outcome": "WITNESS_FOUND",
        "witness_description": "x = -1, for which both denominators are nonzero.",
        "refutation_explanation": "At x = -1, the left side is 3/4 while the right side is 3, so the claimed equality is false.",
        "search_space": "All four integers x in {-2, -1, 1, 2}, evaluated in ascending order using fractions.Fraction exact arithmetic."
    }
    print(json.dumps(result))


if __name__ == "__main__":
    main()
