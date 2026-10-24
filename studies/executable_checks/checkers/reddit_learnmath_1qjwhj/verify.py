r"""If |x-a|<1 and the sign in 2a±1 is selected according to the sign of x, then |x²-a²|≤|2a±1||x-a|."""

import json
from fractions import Fraction


def main():
    a = Fraction(-3, 4)
    x = Fraction(1, 10)

    distance = abs(x - a)
    coefficient = 2 * a + 1 if x > 0 else 2 * a - 1
    left_side = abs(x * x - a * a)
    right_side = abs(coefficient) * distance

    established = (
        x > 0
        and distance == Fraction(17, 20)
        and distance < 1
        and coefficient == Fraction(-1, 2)
        and left_side == Fraction(221, 400)
        and right_side == Fraction(17, 40)
        and left_side - right_side == Fraction(51, 400)
        and left_side > right_side
    )
    if not established:
        raise RuntimeError("exact witness verification failed")

    result = {
        "record_id": "reddit_learnmath_1qjwhj",
        "verdict": "CONFIRMED",
        "notes": "Exact recomputation confirms the premise and violation: |x-a|=17/20<1, the positive x selects 2a+1, and 221/400>17/40 by 51/400. The refuted statement is substantive as formulated, not plainly a typo.",
    }
    print(json.dumps(result, ensure_ascii=False, separators=(",", ":")))


if __name__ == "__main__":
    main()
