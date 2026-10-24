"""The proof claims that λx + (1-λ)y equals (1-λ)x + λy for arbitrary x, y, and λ."""

import itertools
import json

RECORD_ID = "reddit_askmath_11qocq8"
VALUES = (0, 1, -1, 2, -2)
WITNESS_DESCRIPTION = "x = 0, y = 1, λ = 0."
REFUTATION_EXPLANATION = (
    "For x = 0, y = 1, and λ = 0, λx + (1-λ)y = 1, while "
    "(1-λ)x + λy = 0. Since 1 != 0, the claimed equality does not hold "
    "for arbitrary x, y, and λ."
)
SEARCH_SPACE = (
    "All 125 ordered triples (x, y, λ) with each coordinate in the fixed "
    "ordered integer set (0, 1, -1, 2, -2) were evaluated using exact "
    "integer arithmetic."
)


def main():
    first_witness = None
    checked = 0

    for x, y, lam in itertools.product(VALUES, repeat=3):
        checked += 1
        left = lam * x + (1 - lam) * y
        right = (1 - lam) * x + lam * y
        if left != right and first_witness is None:
            first_witness = (x, y, lam, left, right)

    assert checked == 125
    assert first_witness == (0, 1, 0, 1, 0)

    result = {
        "record_id": RECORD_ID,
        "outcome": "WITNESS_FOUND",
        "witness_description": WITNESS_DESCRIPTION,
        "refutation_explanation": REFUTATION_EXPLANATION,
        "search_space": SEARCH_SPACE,
    }
    print(json.dumps(result, ensure_ascii=False, separators=(",", ":")))


if __name__ == "__main__":
    main()
