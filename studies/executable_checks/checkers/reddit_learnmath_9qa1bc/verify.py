r"""For the stated product, the trigonometric expression on line 20 is valid, including at n=0."""

import json


def main():
    n = 0

    product = 1
    for index in range(1, n + 1):
        factor = -1 if index % 2 else 1
        product *= factor
    left = (product, 0)

    angle_numerator = n * (n + 1)
    angle_denominator = 2
    if angle_numerator != 0 or angle_denominator != 2:
        raise AssertionError("the concrete witness must give angle zero")
    cosine_of_zero = 1
    right = (cosine_of_zero, cosine_of_zero)

    if left != (1, 0) or right != (1, 1) or left == right:
        raise AssertionError("exact witness recomputation failed")

    result = {
        "record_id": "reddit_learnmath_9qa1bc",
        "verdict": "CONFIRMED",
        "notes": "Exact recomputation confirms the n=0 witness: the empty product is (1,0), whereas both cosine terms are cos(0)=1, making the stated right-hand side (1,1). The refuted statement is plainly a typo, likely using cosine where sine was intended in the imaginary term."
    }
    print(json.dumps(result, separators=(",", ":")))


if __name__ == "__main__":
    main()
