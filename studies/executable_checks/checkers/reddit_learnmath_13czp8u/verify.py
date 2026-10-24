r"""A column stochastic matrix A can't have an eigenvalue equal to -1."""

import json

RECORD_ID = "reddit_learnmath_13czp8u"
VERDICT = "CONFIRMED"
NOTES = (
    "The refuted statement is substantive, not plainly a typo. Exact integer "
    "checks confirm that [[0, 1], [1, 0]] is column stochastic and maps the "
    "nonzero vector (1, -1) to its negative, so -1 is an eigenvalue."
)


def main():
    matrix = ((0, 1), (1, 0))
    vector = (1, -1)

    rectangular = (
        len(matrix) == 2
        and all(len(row) == 2 for row in matrix)
    )
    entries_are_exact_integers = all(
        type(entry) is int for row in matrix for entry in row
    )
    nonnegative = all(entry >= 0 for row in matrix for entry in row)
    column_totals = tuple(
        sum(matrix[row_index][column_index] for row_index in range(2))
        for column_index in range(2)
    )
    column_stochastic = (
        rectangular
        and entries_are_exact_integers
        and nonnegative
        and column_totals == (1, 1)
    )

    image = tuple(
        sum(matrix[row_index][column_index] * vector[column_index]
            for column_index in range(2))
        for row_index in range(2)
    )
    vector_is_nonzero = any(component != 0 for component in vector)
    negative_vector = tuple(-component for component in vector)

    if not (column_stochastic and vector_is_nonzero and image == negative_vector):
        raise AssertionError("exact witness verification failed")

    result = {
        "record_id": RECORD_ID,
        "verdict": VERDICT,
        "notes": NOTES,
    }
    print(json.dumps(result, separators=(",", ":")))


if __name__ == "__main__":
    main()
