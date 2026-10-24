"""In the split local case, the reductions modulo the maximal ideal of all regular-representation matrices associated with the order basis can be simultaneously diagonalized."""

import itertools
import json

RECORD_ID = "arxiv_2511.21137v2__source_enriched_codex"
OUTCOME = "NO_WITNESS_INCONCLUSIVE"
WITNESS_DESCRIPTION = (
    "No counterexample was found among commuting ordered pairs of 2-by-2 "
    "matrices over F_2 for which each matrix is individually diagonalizable "
    "over F_2."
)
REFUTATION_EXPLANATION = (
    "The bounded sweep verifies only a finite matrix proxy. The quote supplies "
    "no bounds on the residue field, matrix dimension, order, or number of "
    "order-basis matrices, so this sweep cannot exhaust the stated claim."
)
SEARCH_SPACE = (
    "All 256 ordered pairs of 2-by-2 matrices over F_2, in lexicographic entry "
    "order; every commuting pair whose two matrices each have an eigenbasis "
    "over F_2 is tested for a common eigenbasis."
)


def mat_vec(matrix, vector):
    a, b, c, d = matrix
    x, y = vector
    return ((a * x + b * y) % 2, (c * x + d * y) % 2)


def mat_mul(left, right):
    a, b, c, d = left
    e, f, g, h = right
    return (
        (a * e + b * g) % 2,
        (a * f + b * h) % 2,
        (c * e + d * g) % 2,
        (c * f + d * h) % 2,
    )


def independent(first, second):
    return (first[0] * second[1] - first[1] * second[0]) % 2 == 1


def is_eigenvector(matrix, vector):
    image = mat_vec(matrix, vector)
    return image == (0, 0) or image == vector


VECTORS = ((0, 1), (1, 0), (1, 1))
BASES = tuple(
    (first, second)
    for first in VECTORS
    for second in VECTORS
    if independent(first, second)
)


def diagonalizable(matrix):
    return any(
        is_eigenvector(matrix, first) and is_eigenvector(matrix, second)
        for first, second in BASES
    )


def simultaneously_diagonalizable(first_matrix, second_matrix):
    return any(
        is_eigenvector(first_matrix, first)
        and is_eigenvector(first_matrix, second)
        and is_eigenvector(second_matrix, first)
        and is_eigenvector(second_matrix, second)
        for first, second in BASES
    )


def main():
    matrices = tuple(itertools.product(range(2), repeat=4))
    first_counterexample = None

    for first_matrix in matrices:
        for second_matrix in matrices:
            commute = mat_mul(first_matrix, second_matrix) == mat_mul(
                second_matrix, first_matrix
            )
            individually_diagonalizable = (
                diagonalizable(first_matrix) and diagonalizable(second_matrix)
            )
            if (
                commute
                and individually_diagonalizable
                and not simultaneously_diagonalizable(first_matrix, second_matrix)
                and first_counterexample is None
            ):
                first_counterexample = (first_matrix, second_matrix)

    if first_counterexample is not None:
        first_matrix, second_matrix = first_counterexample
        result = {
            "record_id": RECORD_ID,
            "outcome": "WITNESS_FOUND",
            "witness_description": (
                "The matrices %s and %s form the first bounded proxy witness."
                % (first_matrix, second_matrix)
            ),
            "refutation_explanation": (
                "They commute and are individually diagonalizable over F_2, "
                "but have no common eigenbasis over F_2."
            ),
            "search_space": SEARCH_SPACE,
        }
    else:
        result = {
            "record_id": RECORD_ID,
            "outcome": OUTCOME,
            "witness_description": WITNESS_DESCRIPTION,
            "refutation_explanation": REFUTATION_EXPLANATION,
            "search_space": SEARCH_SPACE,
        }

    print(json.dumps(result, sort_keys=False))


if __name__ == "__main__":
    main()
