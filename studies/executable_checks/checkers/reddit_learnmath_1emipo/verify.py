"""The linear map sending the given orthonormal basis to an arbitrary orthonormal extension of v necessarily belongs to SU(n)."""

import json


def inner_product(x, y):
    return x[0] * y[0] + x[1] * y[1]


def gram_pair(vectors):
    return tuple(
        tuple(inner_product(x, y) for y in vectors)
        for x in vectors
    )


def apply_matrix(matrix, vector):
    return (
        matrix[0][0] * vector[0] + matrix[0][1] * vector[1],
        matrix[1][0] * vector[0] + matrix[1][1] * vector[1],
    )


def main():
    source_basis = ((1, 0), (0, 1))
    v = (1, 0)
    extension = (v, (0, -1))
    identity = ((1, 0), (0, 1))

    matrix = (
        (extension[0][0], extension[1][0]),
        (extension[0][1], extension[1][1]),
    )
    determinant = matrix[0][0] * matrix[1][1] - matrix[0][1] * matrix[1][0]

    source_is_orthonormal = gram_pair(source_basis) == identity
    extension_is_orthonormal = gram_pair(extension) == identity
    sends_basis_as_stated = (
        apply_matrix(matrix, source_basis[0]) == v
        and apply_matrix(matrix, source_basis[1]) == extension[1]
    )
    is_unitary = extension_is_orthonormal
    is_not_special_unitary = is_unitary and determinant != 1
    counterexample = (
        source_is_orthonormal
        and extension_is_orthonormal
        and extension[0] == v
        and sends_basis_as_stated
        and is_not_special_unitary
        and determinant == -1
    )

    if counterexample:
        verdict = "CONFIRMED"
        notes = "The refuted statement is substantive, not plainly a typo: an arbitrary orthonormal extension guarantees a unitary map, but its determinant need not be 1."
    else:
        verdict = "REFUTED_WITNESS_INVALID"
        notes = "The proposed witness does not establish the claimed counterexample."

    print(json.dumps({
        "record_id": "reddit_learnmath_1emipo",
        "verdict": verdict,
        "notes": notes,
    }, separators=(",", ":")))


if __name__ == "__main__":
    main()
