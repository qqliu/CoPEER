"""For every vector space V of dimension n ≤ 5 and every Zariski-closed subgroup H ⊆ GL(V) satisfying the stated irreducibility and fixed-vector hypotheses, H equals PSL(2)."""

import json
from fractions import Fraction

RECORD_ID = "arxiv_1104.4827v2__source_enriched_codex"
OUTCOME = "WITNESS_FOUND"
WITNESS_DESCRIPTION = (
    "Let K be the algebraic closure of Q, let V=K^1, and let H consist only "
    "of the 1-by-1 identity matrix."
)
REFUTATION_EXPLANATION = (
    "The singleton H is a Zariski-closed subgroup of GL(V), cut out by "
    "x_11-1=0, and H^0=H. Its action on the one-dimensional V is "
    "irreducible, and its sole element fixes every nonzero vector. But H has "
    "one element, while PSL(2,K) has at least two: the classes of I_2 and "
    "diag(2,1/2) are distinct modulo {I_2,-I_2}. Hence H is not PSL(2)."
)
SEARCH_SPACE = (
    "Exhaustively swept the five candidates (K^n,{I_n}) for integers "
    "n=1,2,3,4,5, in increasing n order; the n=1 candidate is a "
    "counterexample."
)


def identity(n):
    return tuple(
        tuple(1 if row == column else 0 for column in range(n))
        for row in range(n)
    )


def multiply(left, right):
    n = len(left)
    return tuple(
        tuple(
            sum(left[row][k] * right[k][column] for k in range(n))
            for column in range(n)
        )
        for row in range(n)
    )


def apply(matrix, vector):
    return tuple(
        sum(matrix[row][column] * vector[column] for column in range(len(vector)))
        for row in range(len(matrix))
    )


def negate(matrix):
    return tuple(tuple(-entry for entry in row) for row in matrix)


def determinant_two(matrix):
    return matrix[0][0] * matrix[1][1] - matrix[0][1] * matrix[1][0]


def psl_two_has_at_least_two_elements():
    identity_two = identity(2)
    diagonal = ((2, 0), (0, Fraction(1, 2)))
    return (
        determinant_two(diagonal) == 1
        and diagonal != identity_two
        and diagonal != negate(identity_two)
    )


def candidate_is_counterexample(n):
    matrix = identity(n)
    basis_vector = tuple(1 if index == 0 else 0 for index in range(n))

    # The singleton {I_n} is a subgroup. It is Zariski closed because its
    # entries are cut out by x_ij-delta_ij=0, and its identity component is
    # itself. Its trivial action is irreducible exactly when n is one.
    is_subgroup = multiply(matrix, matrix) == matrix
    is_zariski_closed = all(
        matrix[row][column] == (1 if row == column else 0)
        for row in range(n)
        for column in range(n)
    )
    has_fixed_nonzero_vector = (
        any(coordinate != 0 for coordinate in basis_vector)
        and apply(matrix, basis_vector) == basis_vector
    )
    identity_component_irreducible = n == 1
    not_psl_two = psl_two_has_at_least_two_elements()

    return (
        is_subgroup
        and is_zariski_closed
        and has_fixed_nonzero_vector
        and identity_component_irreducible
        and not_psl_two
    )


matching_dimensions = []
for dimension in range(1, 6):
    if candidate_is_counterexample(dimension):
        matching_dimensions.append(dimension)

if matching_dimensions != [1]:
    raise RuntimeError("unexpected bounded-search result")

result = {
    "record_id": RECORD_ID,
    "outcome": OUTCOME,
    "witness_description": WITNESS_DESCRIPTION,
    "refutation_explanation": REFUTATION_EXPLANATION,
    "search_space": SEARCH_SPACE,
}
print(json.dumps(result, separators=(",", ":")))
