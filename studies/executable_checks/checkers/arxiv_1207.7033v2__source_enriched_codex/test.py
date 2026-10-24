"""For arbitrary decompositions of the columns of M into n_j linear components, det(M) equals the displayed sum restricted to permutations σ in S_n, with the additional factor sgn(σ)."""

import json
from itertools import permutations, product

RECORD_ID = "arxiv_1207.7033v2__source_enriched_codex"
OUTCOME = "WITNESS_FOUND"
WITNESS_DESCRIPTION = "For n=2, let c_11=(1,0), c_12=(0,0), c_21=(0,1), c_22=(0,0), with a_11=1, a_12=0, a_21=1, a_22=0; hence the two columns of M are (1,0) and (0,1)."
REFUTATION_EXPLANATION = "The determinant of M is 1. In the displayed permutation-restricted sum, the identity term contains a_22=0 and the transposition term contains a_12=0, so both terms vanish (regardless of the sign factor), making the sum 0."
SEARCH_SPACE = "All n=2 decompositions with each a_ij in {0,1} and each c_ij in {(0,0),(0,1),(1,0)} for i,j in {1,2}: 2^4 * 3^4 = 1296 cases, checked in lexicographic product order using exact integer arithmetic."


def permutation_sign(perm):
    inversions = 0
    for left in range(len(perm)):
        for right in range(left + 1, len(perm)):
            if perm[left] > perm[right]:
                inversions += 1
    return -1 if inversions % 2 else 1


def determinant(columns):
    size = len(columns)
    total = 0
    for perm in permutations(range(size)):
        term = permutation_sign(perm)
        for column_index in range(size):
            term *= columns[column_index][perm[column_index]]
        total += term
    return total


def decomposed_column(coefficients, components):
    dimension = len(components[0])
    return tuple(
        sum(coefficients[index] * components[index][coordinate]
            for index in range(len(coefficients)))
        for coordinate in range(dimension)
    )


def restricted_sum(coefficients, components):
    size = len(coefficients)
    total = 0
    for perm in permutations(range(size)):
        scalar = permutation_sign(perm)
        selected_columns = []
        for column_index in range(size):
            component_index = perm[column_index]
            scalar *= coefficients[column_index][component_index]
            selected_columns.append(components[column_index][component_index])
        total += scalar * determinant(tuple(selected_columns))
    return total


def main():
    coefficient_values = (0, 1)
    vector_values = ((0, 0), (0, 1), (1, 0))
    canonical_coefficients = (1, 0, 1, 0)
    canonical_components = ((1, 0), (0, 0), (0, 1), (0, 0))
    canonical_found = False
    cases_checked = 0

    for flat_coefficients in product(coefficient_values, repeat=4):
        coefficients = (
            flat_coefficients[0:2],
            flat_coefficients[2:4],
        )
        for flat_components in product(vector_values, repeat=4):
            components = (
                flat_components[0:2],
                flat_components[2:4],
            )
            matrix_columns = tuple(
                decomposed_column(coefficients[index], components[index])
                for index in range(2)
            )
            left_side = determinant(matrix_columns)
            right_side = restricted_sum(coefficients, components)
            cases_checked += 1
            if (flat_coefficients == canonical_coefficients
                    and flat_components == canonical_components
                    and left_side == 1
                    and right_side == 0):
                canonical_found = True

    if cases_checked != 1296 or not canonical_found:
        raise AssertionError("The exhaustive bounded search did not verify the stated witness")

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
