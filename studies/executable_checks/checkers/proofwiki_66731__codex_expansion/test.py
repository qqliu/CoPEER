"""Line 0035 equates the preceding sum of square roots of squared component errors with the sum of the squared absolute component errors."""

import json
from itertools import product
from math import isqrt


def preceding_sum(errors):
    total = 0
    for error in errors:
        square = error * error
        root = isqrt(square)
        assert root * root == square
        total += root
    return total


def line_0035_sum(errors):
    return sum(abs(error) * abs(error) for error in errors)


def main():
    values = tuple(range(-3, 4))
    first_witness = None
    vectors_checked = 0

    for length in range(1, 4):
        for errors in product(values, repeat=length):
            vectors_checked += 1
            if preceding_sum(errors) != line_0035_sum(errors):
                if first_witness is None:
                    first_witness = errors

    assert vectors_checked == 399
    assert first_witness == (-3,)

    result = {
        "record_id": "proofwiki_66731__codex_expansion",
        "outcome": "WITNESS_FOUND",
        "witness_description": "Take n = 1 with component error f_1(x) - L_1 = -3.",
        "refutation_explanation": "The preceding expression gives sqrt((-3)^2) = 3, whereas line 0035 gives |-3|^2 = 9. Since 3 != 9, the proposed equality fails.",
        "search_space": "All 399 nonempty integer component-error vectors of lengths 1, 2, and 3 with every entry in {-3, -2, -1, 0, 1, 2, 3}, enumerated first by length and then lexicographically.",
    }
    print(json.dumps(result, separators=(",", ":")))


if __name__ == "__main__":
    main()
