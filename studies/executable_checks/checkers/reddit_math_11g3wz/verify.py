r'''From A(A-I_n)=0, the proof claims that either A=0 or A=I_n.'''

import json

REPORT = {
    "record_id": "reddit_math_11g3wz",
    "verdict": "CONFIRMED",
    "notes": "Exact integer matrix multiplication verifies the reported 2-by-2 witness. The refuted statement is substantive, not plainly a typo: it incorrectly applies the zero-product property to matrices.",
}

A = ((0, 0), (0, 1))
I = ((1, 0), (0, 1))
Z = ((0, 0), (0, 0))


def matrix_product(x, y):
    size = len(x)
    rows = []
    for row_index in range(size):
        row = []
        for column_index in range(size):
            total = 0
            for inner_index in range(size):
                total += x[row_index][inner_index] * y[inner_index][column_index]
            row.append(total)
        rows.append(tuple(row))
    return tuple(rows)


A_minus_I = tuple(
    tuple(A[row][column] - I[row][column] for column in range(2))
    for row in range(2)
)
computed_product = matrix_product(A, A_minus_I)

assert len(A) == 2
assert all(len(row) == 2 for row in A)
assert A != Z
assert A != I
assert A_minus_I == ((-1, 0), (0, 0))
assert computed_product == Z
assert matrix_product(A, A) == A
assert REPORT["verdict"] == "CONFIRMED"

print(json.dumps(REPORT, separators=(",", ":")))
