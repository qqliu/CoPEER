"""If some summand M_i is not contained in K in a decomposition M=N⊕K, then M_i contains a nonzero element of N."""

import json
from itertools import product

VECTORS = (0, 1, 2, 3)
ZERO_SUBSPACE = 1
FULL_SPACE = 15


def is_subspace(mask):
    if (mask & ZERO_SUBSPACE) == 0:
        return False
    members = tuple(v for v in VECTORS if (mask & (1 << v)) != 0)
    return all((mask & (1 << (a ^ b))) != 0 for a in members for b in members)


def subspace_sum(left, right):
    result = 0
    for a in VECTORS:
        if (left & (1 << a)) == 0:
            continue
        for b in VECTORS:
            if (right & (1 << b)) != 0:
                result |= 1 << (a ^ b)
    return result


def is_direct_decomposition(left, right):
    return (left & right) == ZERO_SUBSPACE and subspace_sum(left, right) == FULL_SPACE


subspaces = tuple(mask for mask in range(16) if is_subspace(mask))
assert subspaces == (1, 3, 5, 9, 15)

complements = {
    space: tuple(candidate for candidate in subspaces if is_direct_decomposition(space, candidate))
    for space in subspaces
}

witnesses = []
checked = 0
for n_space, k_space, mi_space in product(subspaces, repeat=3):
    checked += 1
    if not is_direct_decomposition(n_space, k_space):
        continue
    if not complements[mi_space]:
        continue
    if (mi_space & k_space) == mi_space:
        continue
    if (mi_space & n_space) != ZERO_SUBSPACE:
        continue
    witnesses.append((n_space, k_space, mi_space))

assert checked == 125
assert witnesses
assert witnesses[0] == (3, 5, 9)
assert is_direct_decomposition(9, 5)

result = {
    "record_id": "reddit_learnmath_k0t5hg",
    "outcome": "WITNESS_FOUND",
    "witness_description": "In the two-dimensional vector space M=F_2^2, take N=span{(1,0)}, K=span{(0,1)}, and M_i=span{(1,1)}. Then M=N⊕K, and M_i is a direct summand of M (indeed M=M_i⊕K).",
    "refutation_explanation": "M_i is not contained in K because (1,1) belongs to M_i but not K. Yet M_i∩N={(0,0)}, so M_i contains no nonzero element of N; the antecedent holds and the conclusion fails.",
    "search_space": "The program enumerates all 16 subsets of F_2^2 to obtain its 5 subspaces, then exhaustively checks all 5^3=125 ordered triples (N,K,M_i), retaining those with M=N⊕K and with M_i a direct summand (checked against all 5 possible complementary subspaces).",
}
print(json.dumps(result, separators=(",", ":")))
