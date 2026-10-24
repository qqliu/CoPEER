"""A column stochastic matrix A can't have an eigenvalue equal to -1."""

import itertools
import json

RECORD_ID = "reddit_learnmath_13czp8u"
OUTCOME = "WITNESS_FOUND"
WITNESS_DESCRIPTION = (
    "A = [[0, 1], [1, 0]] is column stochastic: all entries are "
    "nonnegative and each column sums to 1. The nonzero vector v = (1, -1) "
    "satisfies A v = (-1, 1) = -v."
)
REFUTATION_EXPLANATION = (
    "Thus -1 is an eigenvalue of the column stochastic matrix A, directly "
    "contradicting the claim."
)
SEARCH_SPACE = (
    "All 16 row-major 2-by-2 matrices whose entries lie in {0, 1}, in "
    "lexicographic product order; each matrix was tested for nonnegative "
    "entries, column sums equal to 1, and det(A + I) = 0."
)


def is_column_stochastic(matrix):
    return (
        all(entry >= 0 for row in matrix for entry in row)
        and matrix[0][0] + matrix[1][0] == 1
        and matrix[0][1] + matrix[1][1] == 1
    )


def has_eigenvalue_minus_one(matrix):
    a, b = matrix[0]
    c, d = matrix[1]
    return (a + 1) * (d + 1) - b * c == 0


def main():
    witness = None
    for entries in itertools.product((0, 1), repeat=4):
        matrix = (entries[:2], entries[2:])
        if is_column_stochastic(matrix) and has_eigenvalue_minus_one(matrix):
            witness = matrix
            break

    expected = ((0, 1), (1, 0))
    if witness != expected:
        raise AssertionError("deterministic exhaustive search did not find the expected witness")

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
