r"""For every A in K, either ⋃X is a subset of A or A is a subset of ⋃X."""

import json

zero = 0
one = 1
A = frozenset((zero,))
X = frozenset((frozenset((one,)),))
K = frozenset((one, A))

union_x = frozenset(element for member in X for element in member)

assert X == frozenset((frozenset((one,)),))
assert union_x == frozenset((one,))
assert A == frozenset((zero,))
assert K == frozenset((one, A))
assert union_x.issubset(K)
assert A in K
assert one in union_x and one not in A
assert zero in A and zero not in union_x
assert not union_x.issubset(A)
assert not A.issubset(union_x)
assert not (union_x.issubset(A) or A.issubset(union_x))

REPORT = {
    "record_id": "reddit_learnmath_87dz19",
    "verdict": "CONFIRMED",
    "notes": "The concrete witness is valid: with X={{1}}, A={0}, and K={1,{0}}, the union of X is {1}, the premise union(X)⊆K holds, and A∈K, but neither {1}⊆{0} nor {0}⊆{1}. The refuted statement is substantive, not plainly a typo."
}

print(json.dumps(REPORT, ensure_ascii=False, separators=(",", ":")))
