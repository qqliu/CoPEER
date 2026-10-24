"""Over a real vector space, the existence of one real eigenvalue implies that the operator has an upper-triangular matrix in an orthonormal basis."""

import json
from itertools import permutations, product

RECORD_ID = "reddit_learnmath_1co5gzk"
OUTCOME = "WITNESS_FOUND"
WITNESS_DESCRIPTION = "A on R^3 with standard matrix [[0,-1,0],[1,0,0],[0,0,1]]; the nonzero vector e3=(0,0,1) satisfies A e3=e3, so 1 is a real eigenvalue."
REFUTATION_EXPLANATION = "Its characteristic polynomial is (t-1)(t^2+1). If A had a real upper-triangular matrix in an orthonormal basis, similarity would preserve this polynomial, while the characteristic polynomial of a real upper-triangular 3x3 matrix would be a product of three real linear factors. Since t^2+1 has no real root, this is impossible."
SEARCH_SPACE = "All 19,683 real 3x3 matrices whose entries are in {-1,0,1}, in fixed order with the displayed witness first and the remaining matrices in lexicographic product order; for each matrix, every integer lambda in {-3,-2,-1,0,1,2,3} was tested as an exact characteristic-polynomial root, and the resulting quadratic factor was tested for negative discriminant."


def polynomial_product(left, right):
    result = [0] * (len(left) + len(right) - 1)
    for i, left_coefficient in enumerate(left):
        for j, right_coefficient in enumerate(right):
            result[i + j] += left_coefficient * right_coefficient
    return tuple(result)


def permutation_sign(permutation):
    inversions = 0
    for i in range(len(permutation)):
        for j in range(i + 1, len(permutation)):
            if permutation[i] > permutation[j]:
                inversions += 1
    return -1 if inversions % 2 else 1


def characteristic_polynomial(matrix):
    size = 3
    coefficients = [0] * (size + 1)
    for permutation in permutations(range(size)):
        term = (1,)
        for row, column in enumerate(permutation):
            entry = matrix[row * size + column]
            factor = (-entry, 1) if row == column else (-entry,)
            term = polynomial_product(term, factor)
        sign = permutation_sign(permutation)
        for degree, coefficient in enumerate(term):
            coefficients[degree] += sign * coefficient
    return tuple(coefficients)


def evaluate_polynomial(coefficients, value):
    result = 0
    for coefficient in reversed(coefficients):
        result = result * value + coefficient
    return result


def quadratic_after_cubic_root(coefficients, root):
    quadratic = coefficients[3]
    linear = coefficients[2] + root * quadratic
    constant = coefficients[1] + root * linear
    remainder = coefficients[0] + root * constant
    assert remainder == 0
    return constant, linear, quadratic


def matrix_vector_product(matrix, vector):
    return tuple(
        sum(matrix[row * 3 + column] * vector[column] for column in range(3))
        for row in range(3)
    )


preferred = (0, -1, 0, 1, 0, 0, 0, 0, 1)
found = None
matrix_count = 0

candidate_stream = (preferred,)
for matrix in candidate_stream:
    matrix_count += 1
    coefficients = characteristic_polynomial(matrix)
    for eigenvalue in range(-3, 4):
        if evaluate_polynomial(coefficients, eigenvalue) == 0:
            constant, linear, quadratic = quadratic_after_cubic_root(coefficients, eigenvalue)
            discriminant = linear * linear - 4 * quadratic * constant
            if discriminant < 0 and found is None:
                found = (matrix, eigenvalue, coefficients, discriminant)

for matrix in product((-1, 0, 1), repeat=9):
    if matrix == preferred:
        continue
    matrix_count += 1
    coefficients = characteristic_polynomial(matrix)
    for eigenvalue in range(-3, 4):
        if evaluate_polynomial(coefficients, eigenvalue) == 0:
            constant, linear, quadratic = quadratic_after_cubic_root(coefficients, eigenvalue)
            discriminant = linear * linear - 4 * quadratic * constant
            if discriminant < 0 and found is None:
                found = (matrix, eigenvalue, coefficients, discriminant)

assert matrix_count == 19683
assert found == (preferred, 1, (-1, 1, -1, 1), -4)
assert matrix_vector_product(preferred, (0, 0, 1)) == (0, 0, 1)

result = {
    "record_id": RECORD_ID,
    "outcome": OUTCOME,
    "witness_description": WITNESS_DESCRIPTION,
    "refutation_explanation": REFUTATION_EXPLANATION,
    "search_space": SEARCH_SPACE,
}
print(json.dumps(result, ensure_ascii=True, separators=(",", ":")))
