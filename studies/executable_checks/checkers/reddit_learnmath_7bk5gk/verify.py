r'''If the linear composition F∘G is one-to-one, then both F and G are one-to-one.'''

import json
from fractions import Fraction

REPORT = {
    "record_id": "reddit_learnmath_7bk5gk",
    "verdict": "CONFIRMED",
    "notes": "Exact rational recomputation shows that F∘G is the identity on Q, while F maps the distinct vectors (0,0) and (1,0) to the same value. The refuted statement is substantive, not a typo."
}


def multiply_matrices(left, right):
    rows = len(left)
    inner = len(right)
    columns = len(right[0])
    assert all(len(row) == inner for row in left)
    assert all(len(row) == columns for row in right)
    result = []
    for i in range(rows):
        result_row = []
        for j in range(columns):
            value = Fraction(0)
            for k in range(inner):
                value += left[i][k] * right[k][j]
            result_row.append(value)
        result.append(tuple(result_row))
    return tuple(result)


def apply_matrix(matrix, vector):
    assert all(len(row) == len(vector) for row in matrix)
    output = []
    for row in matrix:
        value = Fraction(0)
        for coefficient, coordinate in zip(row, vector):
            value += coefficient * coordinate
        output.append(value)
    return tuple(output)


zero = Fraction(0)
one = Fraction(1)
g_matrix = ((zero,), (one,))
f_matrix = ((zero, one),)
composition = multiply_matrices(f_matrix, g_matrix)

# The recomputed composition matrix is [1], so its map on Q is x -> x
# and is injective.
assert composition == ((one,),)
assert composition[0][0] != zero

first_vector = (zero, zero)
second_vector = (one, zero)
assert first_vector != second_vector
assert apply_matrix(f_matrix, first_vector) == (zero,)
assert apply_matrix(f_matrix, second_vector) == (zero,)

# Directly check that the matrices encode the reported formulas.
assert apply_matrix(g_matrix, (Fraction(7),)) == (zero, Fraction(7))
assert apply_matrix(composition, (Fraction(-3),)) == (Fraction(-3),)

print(json.dumps(REPORT, separators=(",", ":")))
