r"""For every vector space V of dimension n ≤ 5 and every Zariski-closed subgroup H ⊆ GL(V) satisfying the stated irreducibility and fixed-vector hypotheses, H equals PSL(2)."""

import json
from fractions import Fraction

RECORD_ID = "arxiv_1104.4827v2__source_enriched_codex"
VERDICT = "CONFIRMED"
NOTES = (
    "Exact recomputation validates the n=1 singleton-identity witness. It "
    "satisfies every stated hypothesis, while PSL(2) has at least two "
    "distinct classes. The refutation is substantive as written: this is "
    "a genuine omitted boundary case, not plainly a typographical slip."
)


def matrix_product(left, right):
    rows = len(left)
    middle = len(right)
    columns = len(right[0])
    return tuple(
        tuple(
            sum(left[i][k] * right[k][j] for k in range(middle))
            for j in range(columns)
        )
        for i in range(rows)
    )


def matrix_action(matrix, vector):
    return tuple(
        sum(row[j] * vector[j] for j in range(len(vector)))
        for row in matrix
    )


def negative(matrix):
    return tuple(tuple(-entry for entry in row) for row in matrix)


def determinant_2_by_2(matrix):
    return matrix[0][0] * matrix[1][1] - matrix[0][1] * matrix[1][0]


dimension = 1
identity_1 = ((Fraction(1),),)
group = (identity_1,)
nonzero_vector = (Fraction(1),)

within_dimension_bound = 0 < dimension <= 5
in_general_linear_group = identity_1[0][0] != 0
is_singleton_subgroup = (
    len(group) == 1
    and matrix_product(group[0], group[0]) == group[0]
)

# The linear polynomial X - 1 has the displayed unique root over every
# characteristic-zero field, so its zero set in GL(1) is exactly this group.
linear_coefficient = 1
linear_constant = -1
unique_root = Fraction(-linear_constant, linear_coefficient)
is_zariski_closed = (
    linear_coefficient != 0
    and unique_root == identity_1[0][0]
    and linear_coefficient * identity_1[0][0] + linear_constant == 0
)

# A singleton topological group is connected, hence is its own identity
# component. A one-dimensional space has no nonzero proper subspace.
identity_component_is_group = len(group) == 1
possible_subspace_dimensions = tuple(range(dimension + 1))
identity_component_action_is_irreducible = all(
    subdimension == 0 or subdimension == dimension
    for subdimension in possible_subspace_dimensions
)

every_element_has_fixed_nonzero_vector = (
    any(coordinate != 0 for coordinate in nonzero_vector)
    and all(
        matrix_action(element, nonzero_vector) == nonzero_vector
        for element in group
    )
)

identity_2 = (
    (Fraction(1), Fraction(0)),
    (Fraction(0), Fraction(1)),
)
second_sl2_element = (
    (Fraction(2), Fraction(0)),
    (Fraction(0), Fraction(1, 2)),
)
second_element_has_determinant_one = determinant_2_by_2(second_sl2_element) == 1
second_class_differs_from_identity_class = (
    second_sl2_element != identity_2
    and second_sl2_element != negative(identity_2)
)
psl2_has_at_least_two_elements = (
    second_element_has_determinant_one
    and second_class_differs_from_identity_class
)
not_equal_to_psl2 = len(group) == 1 and psl2_has_at_least_two_elements

witness_is_counterexample = all((
    within_dimension_bound,
    in_general_linear_group,
    is_singleton_subgroup,
    is_zariski_closed,
    identity_component_is_group,
    identity_component_action_is_irreducible,
    every_element_has_fixed_nonzero_vector,
    not_equal_to_psl2,
))

if not witness_is_counterexample:
    raise RuntimeError("the exact witness certificate failed")

print(json.dumps({
    "record_id": RECORD_ID,
    "verdict": VERDICT,
    "notes": NOTES,
}, separators=(",", ":")))
