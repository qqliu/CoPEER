"""The linear map sending the given orthonormal basis to an arbitrary orthonormal extension of v necessarily belongs to SU(n)."""

import json


def dot(left, right):
    return sum(a * b for a, b in zip(left, right))


def determinant_2_by_2(matrix):
    return matrix[0][0] * matrix[1][1] - matrix[0][1] * matrix[1][0]


def main():
    e1 = (1, 0)
    e2 = (0, 1)
    v = e1
    witnesses = []

    # This exhausts the two signed standard-vector extensions of v in R^2.
    for sign in (-1, 1):
        e2_prime = (0, sign)
        images = (v, e2_prime)
        gram_matrix = tuple(
            tuple(dot(left, right) for right in images)
            for left in images
        )
        assert gram_matrix == ((1, 0), (0, 1))

        # The image vectors are the columns of this matrix.
        linear_map = (
            (images[0][0], images[1][0]),
            (images[0][1], images[1][1]),
        )
        determinant = determinant_2_by_2(linear_map)
        if determinant != 1:
            witnesses.append((sign, linear_map, determinant))

    assert witnesses == [(-1, ((1, 0), (0, -1)), -1)]

    result = {
        "record_id": "reddit_learnmath_1emipo",
        "outcome": "WITNESS_FOUND",
        "witness_description": "For n=2, use the standard orthonormal basis (e1,e2), set v=e1, and extend v by e2'=-e2. The resulting linear map is diag(1,-1).",
        "refutation_explanation": "The images (e1,-e2) form an orthonormal basis, so the map is unitary, but its determinant is -1 rather than 1. Hence it is not in SU(2), contradicting the claimed necessity.",
        "search_space": "Exhaustively swept both maps diag(1,s) for s in {-1,1}, corresponding to all signed standard-vector extensions (e1,s*e2) of v=e1 in dimension 2.",
    }
    print(json.dumps(result, separators=(",", ":")))


if __name__ == "__main__":
    main()
