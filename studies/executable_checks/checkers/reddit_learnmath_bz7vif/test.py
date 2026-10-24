"""From AT = T, the proof infers A = I without establishing that T is invertible or otherwise right-cancellable."""

import itertools
import json


def multiply(left, right):
    return (
        left[0] * right[0] + left[1] * right[2],
        left[0] * right[1] + left[1] * right[3],
        left[2] * right[0] + left[3] * right[2],
        left[2] * right[1] + left[3] * right[3],
    )


identity = (1, 0, 0, 1)
zero = (0, 0, 0, 0)
witnesses = []

for entries in itertools.product((0, 1), repeat=4):
    t_matrix = entries
    a_matrix = t_matrix
    if t_matrix != zero and multiply(a_matrix, t_matrix) == t_matrix and a_matrix != identity:
        witnesses.append((a_matrix, t_matrix))

expected = (0, 0, 0, 1)
if not witnesses or witnesses[0] != (expected, expected):
    raise RuntimeError("deterministic exhaustive search did not find the expected witness")

result = {
    "record_id": "reddit_learnmath_bz7vif",
    "outcome": "WITNESS_FOUND",
    "witness_description": "T = A = [[0, 0], [0, 1]] (so A = c_1*T with c_1 = 1 and all higher coefficients 0), and I = [[1, 0], [0, 1]].",
    "refutation_explanation": "Exact multiplication gives AT = T^2 = [[0, 0], [0, 1]] = T, while A != I because A's top-left entry is 0 and I's is 1. Thus AT = T does not permit right-cancellation of T in this bounded matrix instance.",
    "search_space": "All 16 2x2 matrices T with row-major entries in {0,1}, with A fixed to T (the c_1 = 1, all higher coefficients 0 case); every candidate was checked in lexicographic itertools.product order.",
}
print(json.dumps(result))
