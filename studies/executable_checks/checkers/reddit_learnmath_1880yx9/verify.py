r"""From a_n > k and b_n > k, it follows that a_n + b_n > k for every real k."""

import json


def greater(left, right):
    left_numerator, left_denominator = left
    right_numerator, right_denominator = right
    if left_denominator <= 0 or right_denominator <= 0:
        raise ValueError("denominators must be positive")
    return left_numerator * right_denominator > right_numerator * left_denominator


def add(left, right):
    left_numerator, left_denominator = left
    right_numerator, right_denominator = right
    return (
        left_numerator * right_denominator + right_numerator * left_denominator,
        left_denominator * right_denominator,
    )


def equal(left, right):
    return left[0] * right[1] == right[0] * left[1]


def main():
    k = (-1, 1)
    a_n = (-3, 4)
    b_n = (-3, 4)
    total = add(a_n, b_n)

    verified = (
        greater(a_n, k)
        and greater(b_n, k)
        and not greater(total, k)
        and equal(total, (-3, 2))
    )
    if not verified:
        raise AssertionError("the reported witness did not verify")

    result = {
        "record_id": "reddit_learnmath_1880yx9",
        "verdict": "CONFIRMED",
        "notes": "The statement is substantively false, not plainly a typo: exact rational arithmetic verifies that -3/4 > -1 for both terms while their sum -3/2 is not greater than -1.",
    }
    print(json.dumps(result, separators=(",", ":")))


if __name__ == "__main__":
    main()
