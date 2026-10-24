r"""Lemma q-inv-bilin's asserted characterization of all tensors in V^{*\ot2} fixed by \SO(\cQ,U) is false when U=V has dimension two, because it omits the invariant alternating tensor."""

import json

RECORD_ID = "arxiv_1711.00411v2__source_enriched_codex"
CONFIRMED_NOTES = (
    "Exact integer polynomial algebra verifies the universal identity "
    "G^T A G = det(G) A for every 2-by-2 matrix G, so A is fixed by SO(2). "
    "An exact quarter-turn calculation shows that the fixed-covector space is zero, "
    "while A is nonzero, alternating, and outside the span of the Euclidean quadratic "
    "tensor. The refuted statement is substantive, not plainly a typo."
)


def polynomial_constant(number):
    if number == 0:
        return {}
    return {(0, 0, 0, 0): number}


def polynomial_variable(index):
    powers = [0, 0, 0, 0]
    powers[index] = 1
    return {tuple(powers): 1}


def polynomial_add(left, right):
    answer = dict(left)
    for monomial, coefficient in right.items():
        answer[monomial] = answer.get(monomial, 0) + coefficient
        if answer[monomial] == 0:
            del answer[monomial]
    return answer


def polynomial_negate(value):
    return {monomial: -coefficient for monomial, coefficient in value.items()}


def polynomial_multiply(left, right):
    answer = {}
    for left_monomial, left_coefficient in left.items():
        for right_monomial, right_coefficient in right.items():
            monomial = tuple(
                left_monomial[position] + right_monomial[position]
                for position in range(4)
            )
            answer[monomial] = (
                answer.get(monomial, 0)
                + left_coefficient * right_coefficient
            )
            if answer[monomial] == 0:
                del answer[monomial]
    return answer


def polynomial_matrix_transpose(matrix):
    return [[matrix[column][row] for column in range(2)] for row in range(2)]


def polynomial_matrix_multiply(left, right):
    return [
        [
            polynomial_add(
                polynomial_multiply(left[row][0], right[0][column]),
                polynomial_multiply(left[row][1], right[1][column]),
            )
            for column in range(2)
        ]
        for row in range(2)
    ]


def integer_matrix_transpose(matrix):
    return tuple(tuple(matrix[column][row] for column in range(2)) for row in range(2))


def integer_matrix_multiply(left, right):
    return tuple(
        tuple(
            left[row][0] * right[0][column]
            + left[row][1] * right[1][column]
            for column in range(2)
        )
        for row in range(2)
    )


def integer_determinant(matrix):
    return matrix[0][0] * matrix[1][1] - matrix[0][1] * matrix[1][0]


def integer_matrix_subtract(left, right):
    return tuple(
        tuple(left[row][column] - right[row][column] for column in range(2))
        for row in range(2)
    )


def main():
    zero = polynomial_constant(0)
    one = polynomial_constant(1)
    minus_one = polynomial_constant(-1)
    generic = [
        [polynomial_variable(0), polynomial_variable(1)],
        [polynomial_variable(2), polynomial_variable(3)],
    ]
    alternating_polynomial = [[zero, minus_one], [one, zero]]

    transformed = polynomial_matrix_multiply(
        polynomial_matrix_multiply(
            polynomial_matrix_transpose(generic), alternating_polynomial
        ),
        generic,
    )
    determinant_polynomial = polynomial_add(
        polynomial_multiply(generic[0][0], generic[1][1]),
        polynomial_negate(polynomial_multiply(generic[0][1], generic[1][0])),
    )
    expected = [
        [zero, polynomial_negate(determinant_polynomial)],
        [determinant_polynomial, zero],
    ]
    universal_area_identity = transformed == expected

    identity = ((1, 0), (0, 1))
    alternating = ((0, -1), (1, 0))
    quarter_turn = ((0, -1), (1, 0))
    quarter_turn_transpose = integer_matrix_transpose(quarter_turn)

    quarter_turn_is_special_orthogonal = (
        integer_matrix_multiply(
            integer_matrix_multiply(quarter_turn_transpose, identity),
            quarter_turn,
        )
        == identity
        and integer_determinant(quarter_turn) == 1
    )
    concrete_invariance = integer_matrix_multiply(
        integer_matrix_multiply(quarter_turn_transpose, alternating),
        quarter_turn,
    ) == alternating

    covector_test_left = integer_matrix_subtract(quarter_turn, identity)
    covector_test_right = integer_matrix_subtract(quarter_turn_transpose, identity)
    no_fixed_covector = (
        integer_determinant(covector_test_left) == 2
        and integer_determinant(covector_test_right) == 2
    )

    nondegenerate_quadratic_form = integer_determinant(identity) == 1
    nonzero_alternating = (
        alternating != ((0, 0), (0, 0))
        and integer_matrix_transpose(alternating)
        == tuple(tuple(-entry for entry in row) for row in alternating)
    )
    outside_quadratic_span = (
        alternating[0][1] != 0
        and identity[0][1] == 0
    )

    established = all(
        (
            universal_area_identity,
            quarter_turn_is_special_orthogonal,
            concrete_invariance,
            no_fixed_covector,
            nondegenerate_quadratic_form,
            nonzero_alternating,
            outside_quadratic_span,
        )
    )

    if established:
        verdict = "CONFIRMED"
        notes = CONFIRMED_NOTES
    else:
        verdict = "REFUTED_WITNESS_INVALID"
        notes = (
            "The independent exact checks did not establish the proposed witness. "
            "The alleged refutation would be substantive rather than plainly a typo."
        )

    print(json.dumps(
        {"record_id": RECORD_ID, "verdict": verdict, "notes": notes},
        separators=(",", ":"),
    ))


if __name__ == "__main__":
    main()
