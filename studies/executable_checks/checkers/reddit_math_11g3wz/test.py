"""From A(A-I_n)=0, the proof claims that either A=0 or A=I_n."""

import itertools
import json


def multiply(left, right):
    return tuple(
        tuple(sum(left[i][k] * right[k][j] for k in range(2)) for j in range(2))
        for i in range(2)
    )


identity = ((1, 0), (0, 1))
zero = ((0, 0), (0, 0))
violations = []

for entries in itertools.product((0, 1), repeat=4):
    matrix = (entries[:2], entries[2:])
    difference = tuple(
        tuple(matrix[i][j] - identity[i][j] for j in range(2))
        for i in range(2)
    )
    if multiply(matrix, difference) == zero and matrix != zero and matrix != identity:
        violations.append(matrix)

witness = ((0, 0), (0, 1))
assert violations
assert violations[0] == witness
assert multiply(
    witness,
    tuple(
        tuple(witness[i][j] - identity[i][j] for j in range(2))
        for i in range(2)
    ),
) == zero

result = {
    "record_id": "reddit_math_11g3wz",
    "outcome": "WITNESS_FOUND",
    "witness_description": "For n=2, A=((0,0),(0,1)) is a witness: A(A-I_2)=((0,0),(0,0)), while A is neither the zero matrix nor I_2.",
    "refutation_explanation": "The claimed dichotomy fails because matrix factors can multiply to the zero matrix without either factor being zero. The displayed A is a nonzero, nonidentity idempotent matrix.",
    "search_space": "All 16 2-by-2 integer matrices whose four entries independently range over {0,1}, swept in the fixed lexicographic order produced by itertools.product((0,1), repeat=4).",
}
print(json.dumps(result, separators=(",", ":")))
