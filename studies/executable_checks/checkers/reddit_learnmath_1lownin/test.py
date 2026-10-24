"""If A has r independent columns and B has r independent rows, then AB is invertible for general dimensions A∈R^{m×r} and B∈R^{r×n}."""

import json
from itertools import product

RECORD_ID = "reddit_learnmath_1lownin"
OUTCOME = "WITNESS_FOUND"
WITNESS_DESCRIPTION = "m=1, r=1, n=2, A=[[1]], and B=[[0,1]]."
REFUTATION_EXPLANATION = (
    "A has one nonzero column, so its r=1 column is independent. "
    "B has one nonzero row, so its r=1 row is independent. "
    "But AB=[[0,1]] is a 1×2 matrix, hence is not square and is not invertible."
)
SEARCH_SPACE = (
    "All 8 pairs A∈{0,1}^{1×1} and B∈{0,1}^{1×2}, enumerated in "
    "itertools.product lexicographic order; every pair was swept."
)


def multiply(a, b):
    return tuple(
        tuple(sum(a[i][k] * b[k][j] for k in range(1)) for j in range(2))
        for i in range(1)
    )


def main():
    values = (0, 1)
    first_witness = None
    swept = 0

    for a_entries in product(values, repeat=1):
        a = (a_entries,)
        for b_entries in product(values, repeat=2):
            b = (b_entries,)
            swept += 1
            a_has_independent_column = a[0][0] != 0
            b_has_independent_row = any(entry != 0 for entry in b[0])
            ab = multiply(a, b)
            ab_is_square = len(ab) == len(ab[0])
            if (
                a_has_independent_column
                and b_has_independent_row
                and not ab_is_square
                and first_witness is None
            ):
                first_witness = (a, b, ab)

    assert swept == 8
    assert first_witness == (((1,),), ((0, 1),), ((0, 1),))

    print(json.dumps({
        "record_id": RECORD_ID,
        "outcome": OUTCOME,
        "witness_description": WITNESS_DESCRIPTION,
        "refutation_explanation": REFUTATION_EXPLANATION,
        "search_space": SEARCH_SPACE,
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
