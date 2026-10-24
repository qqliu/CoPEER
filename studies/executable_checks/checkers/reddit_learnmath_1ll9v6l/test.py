"""The rank of any matrix with at least two prime-valued entries per row and per column is at least 2."""

import itertools
import json

RECORD_ID = "reddit_learnmath_1ll9v6l"
OUTCOME = "WITNESS_FOUND"
WITNESS_DESCRIPTION = "The 2x2 integer matrix [[2, 2], [2, 2]] has two prime-valued entries in every row and every column, but its rank over the rationals is 1."
REFUTATION_EXPLANATION = "Both rows are the same nonzero row, so the matrix has rank 1, which is less than 2 and directly contradicts the universal claim."
SEARCH_SPACE = "All 16 ordered 2x2 matrices whose entries belong to {2, 3}, enumerated lexicographically by the row-major entry tuple; every matrix was checked."


def is_prime(value):
    if value < 2:
        return False
    divisor = 2
    while divisor * divisor <= value:
        if value % divisor == 0:
            return False
        divisor += 1
    return True


def qualifies(matrix):
    rows_ok = all(sum(is_prime(value) for value in row) >= 2 for row in matrix)
    columns_ok = all(
        sum(is_prime(matrix[row][column]) for row in range(2)) >= 2
        for column in range(2)
    )
    return rows_ok and columns_ok


def exact_rank_2_by_2(matrix):
    a, b = matrix[0]
    c, d = matrix[1]
    if a == 0 and b == 0 and c == 0 and d == 0:
        return 0
    if a * d - b * c == 0:
        return 1
    return 2


def main():
    first_witness = None
    checked = 0
    for entries in itertools.product((2, 3), repeat=4):
        matrix = (entries[:2], entries[2:])
        checked += 1
        if qualifies(matrix) and exact_rank_2_by_2(matrix) < 2 and first_witness is None:
            first_witness = matrix

    assert checked == 16
    assert first_witness == ((2, 2), (2, 2))

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
