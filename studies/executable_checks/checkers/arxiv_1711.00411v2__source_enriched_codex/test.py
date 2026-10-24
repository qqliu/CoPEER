r"""Lemma q-inv-bilin's asserted characterization of all tensors in V^{*\ot2} fixed by \SO(\cQ,U) is false when U=V has dimension two, because it omits the invariant alternating tensor."""

import itertools
import json

RECORD_ID = "arxiv_1711.00411v2__source_enriched_codex"
OUTCOME = "WITNESS_FOUND"
WITNESS = "Take U=V=R^2, Q(x,y)=x^2+y^2, and the alternating tensor A with matrix [[0,-1],[1,0]]."
EXPLANATION = "Every element of SO(Q,U)=SO(2) has matrix R(a,b)=[[a,-b],[b,a]] with a^2+b^2=1, and exact symbolic multiplication gives R(a,b)^T A R(a,b)=A. The quarter-turn in SO(2) has no nonzero fixed covector, since its transpose minus the identity has determinant 2. Thus the displayed right-hand side reduces to span{I_Q}=span{I}, while A is not a scalar multiple of I, so A is fixed but omitted."
SPACE = "All 81 row-major 2x2 integer matrices with entries in {-1,0,1}, in itertools.product order; every candidate was tested symbolically for invariance under the full family R(a,b)=[[a,-b],[b,a]] with a^2+b^2=1, and for being nonzero alternating and outside span{I}."


def constant(value):
    return {} if value == 0 else {(0, 0): value}


def add(left, right, right_scale=1):
    result = dict(left)
    for monomial, coefficient in right.items():
        result[monomial] = result.get(monomial, 0) + right_scale * coefficient
        if result[monomial] == 0:
            del result[monomial]
    return result


def multiply(left, right):
    result = {}
    for (ai, bi), left_coefficient in sorted(left.items()):
        for (aj, bj), right_coefficient in sorted(right.items()):
            monomial = (ai + aj, bi + bj)
            result[monomial] = result.get(monomial, 0) + left_coefficient * right_coefficient
            if result[monomial] == 0:
                del result[monomial]
    return result


def reduce_circle(polynomial):
    """Reduce exactly modulo a^2+b^2-1 using a^2=1-b^2."""
    result = dict(polynomial)
    while True:
        reducible = None
        for monomial in sorted(result):
            if monomial[0] >= 2 and result[monomial] != 0:
                reducible = monomial
                break
        if reducible is None:
            break
        coefficient = result.pop(reducible)
        a_power, b_power = reducible
        first = (a_power - 2, b_power)
        second = (a_power - 2, b_power + 2)
        result[first] = result.get(first, 0) + coefficient
        result[second] = result.get(second, 0) - coefficient
        if result.get(first) == 0:
            result.pop(first, None)
        if result.get(second) == 0:
            result.pop(second, None)
    return result


def transpose(matrix):
    return [[matrix[column][row] for column in range(2)] for row in range(2)]


def matrix_multiply(left, right):
    product = []
    for row in range(2):
        product_row = []
        for column in range(2):
            entry = {}
            for middle in range(2):
                entry = add(entry, multiply(left[row][middle], right[middle][column]))
            product_row.append(entry)
        product.append(product_row)
    return product


def invariant_under_all_rotations(matrix):
    a = {(1, 0): 1}
    b = {(0, 1): 1}
    rotation = [[a, add({}, b, -1)], [b, a]]
    tensor = [[constant(matrix[row][column]) for column in range(2)] for row in range(2)]
    transformed = matrix_multiply(matrix_multiply(transpose(rotation), tensor), rotation)
    for row in range(2):
        for column in range(2):
            difference = add(transformed[row][column], constant(matrix[row][column]), -1)
            if reduce_circle(difference):
                return False
    return True


def nonzero_alternating(matrix):
    return (
        matrix != ((0, 0), (0, 0))
        and matrix[0][0] == 0
        and matrix[1][1] == 0
        and matrix[0][1] == -matrix[1][0]
    )


def outside_identity_span(matrix):
    return not (
        matrix[0][1] == 0
        and matrix[1][0] == 0
        and matrix[0][0] == matrix[1][1]
    )


def main():
    quarter_turn_transpose_minus_identity = ((-1, 1), (-1, -1))
    determinant = (
        quarter_turn_transpose_minus_identity[0][0]
        * quarter_turn_transpose_minus_identity[1][1]
        - quarter_turn_transpose_minus_identity[0][1]
        * quarter_turn_transpose_minus_identity[1][0]
    )
    assert determinant == 2

    witnesses = []
    tested = 0
    for entries in itertools.product((-1, 0, 1), repeat=4):
        tested += 1
        matrix = ((entries[0], entries[1]), (entries[2], entries[3]))
        if (
            invariant_under_all_rotations(matrix)
            and nonzero_alternating(matrix)
            and outside_identity_span(matrix)
        ):
            witnesses.append(matrix)

    assert tested == 81
    assert witnesses
    assert witnesses[0] == ((0, -1), (1, 0))

    result = {
        "record_id": RECORD_ID,
        "outcome": OUTCOME,
        "witness_description": WITNESS,
        "refutation_explanation": EXPLANATION,
        "search_space": SPACE,
    }
    print(json.dumps(result, separators=(",", ":")))


if __name__ == "__main__":
    main()
