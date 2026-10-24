"""For arbitrary decompositions of the columns of M into n_j linear components, det(M) equals the displayed sum restricted to permutations σ in S_n, with the additional factor sgn(σ)."""

import json

RECORD_ID = "arxiv_1207.7033v2__source_enriched_codex"
VERDICT = "CONFIRMED"
NOTES = "Independent exact-integer recomputation gives det(M)=1 and the stated permutation-restricted signed sum=0. The refuted statement is substantive, not plainly a typo."


def det2(first_column, second_column):
    return first_column[0] * second_column[1] - first_column[1] * second_column[0]


def linear_combination(weights, vectors):
    return (
        weights[0] * vectors[0][0] + weights[1] * vectors[1][0],
        weights[0] * vectors[0][1] + weights[1] * vectors[1][1],
    )


def main():
    coefficients = ((1, 0), (1, 0))
    components = (
        ((1, 0), (0, 0)),
        ((0, 1), (0, 0)),
    )

    matrix_columns = (
        linear_combination(coefficients[0], components[0]),
        linear_combination(coefficients[1], components[1]),
    )
    left = det2(matrix_columns[0], matrix_columns[1])

    identity = (
        coefficients[0][0]
        * coefficients[1][1]
        * det2(components[0][0], components[1][1])
    )
    transposition = -(
        coefficients[0][1]
        * coefficients[1][0]
        * det2(components[0][1], components[1][0])
    )
    right = identity + transposition

    if matrix_columns != ((1, 0), (0, 1)) or left != 1 or right != 0:
        raise AssertionError("exact witness recomputation failed")

    print(json.dumps({
        "record_id": RECORD_ID,
        "verdict": VERDICT,
        "notes": NOTES,
    }, separators=(",", ":")))


if __name__ == "__main__":
    main()
