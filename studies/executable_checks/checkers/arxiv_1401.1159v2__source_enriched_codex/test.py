"""The product of any two unimodal polynomials is unimodal."""

import json
from itertools import combinations, product

RECORD_ID = "arxiv_1401.1159v2__source_enriched_codex"
OUTCOME = "WITNESS_FOUND"
WITNESS_DESCRIPTION = (
    "P(x)=Q(x)=1+4x+5x^2+11x^3; each coefficient sequence "
    "(1,4,5,11) is strictly increasing and hence unimodal."
)
REFUTATION_EXPLANATION = (
    "P(x)Q(x)=1+8x+26x^2+62x^3+113x^4+110x^5+121x^6. "
    "Its coefficients rise to 113, fall to 110, and then rise to 121, "
    "so they are not unimodal."
)
SEARCH_SPACE = (
    "All 108900 ordered pairs of degree-3 polynomials whose coefficient "
    "tuples are strictly increasing 4-element combinations from "
    "{1,2,...,11}, in lexicographic order; every product was checked using "
    "exact integer convolution."
)


def is_unimodal(values):
    return any(
        all(values[index] <= values[index + 1] for index in range(peak))
        and all(
            values[index] >= values[index + 1]
            for index in range(peak, len(values) - 1)
        )
        for peak in range(len(values))
    )


def multiply(left, right):
    coefficients = [0] * (len(left) + len(right) - 1)
    for left_index, left_value in enumerate(left):
        for right_index, right_value in enumerate(right):
            coefficients[left_index + right_index] += left_value * right_value
    return tuple(coefficients)


def main():
    polynomials = tuple(combinations(range(1, 12), 4))
    target = (1, 4, 5, 11)
    checked = 0
    target_verified = False

    for left, right in product(polynomials, repeat=2):
        checked += 1
        product_coefficients = multiply(left, right)
        product_is_unimodal = is_unimodal(product_coefficients)
        if left == target and right == target:
            target_verified = (
                is_unimodal(left)
                and is_unimodal(right)
                and not product_is_unimodal
                and product_coefficients == (1, 8, 26, 62, 113, 110, 121)
            )

    assert len(polynomials) == 330
    assert checked == 108900
    assert target_verified

    result = {
        "record_id": RECORD_ID,
        "outcome": OUTCOME,
        "witness_description": WITNESS_DESCRIPTION,
        "refutation_explanation": REFUTATION_EXPLANATION,
        "search_space": SEARCH_SPACE,
    }
    print(json.dumps(result, separators=(",", ":")))


if __name__ == "__main__":
    main()
