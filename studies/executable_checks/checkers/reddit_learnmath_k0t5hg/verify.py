r"""If some summand M_i is not contained in K in a decomposition M=N⊕K, then M_i contains a nonzero element of N."""

import json

REPORT = {
    "record_id": "reddit_learnmath_k0t5hg",
    "verdict": "CONFIRMED",
    "notes": "Exact arithmetic over F_2 confirms the witness: M=N⊕K, M_i is a direct summand, M_i is not contained in K, and M_i∩N contains only zero. The refuted statement is substantive, not plainly a typo.",
}


def add(left, right):
    return ((left[0] + right[0]) % 2, (left[1] + right[1]) % 2)


def span_one(vector):
    return frozenset(((0, 0), vector))


def subspace_sum(left, right):
    return frozenset(add(a, b) for a in left for b in right)


zero = (0, 0)
M = frozenset(((0, 0), (1, 0), (0, 1), (1, 1)))
N = span_one((1, 0))
K = span_one((0, 1))
M_i = span_one((1, 1))

assert subspace_sum(N, K) == M
assert N.intersection(K) == frozenset((zero,))
assert subspace_sum(M_i, K) == M
assert M_i.intersection(K) == frozenset((zero,))
assert (1, 1) in M_i and (1, 1) not in K
assert not M_i.issubset(K)
assert M_i.intersection(N) == frozenset((zero,))
assert not any(element != zero and element in N for element in M_i)

print(json.dumps(REPORT, separators=(",", ":")))
