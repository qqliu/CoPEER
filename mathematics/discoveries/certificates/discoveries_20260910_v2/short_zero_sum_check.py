#!/usr/bin/env python3
"""Exact standalone replay of Zhao 6.2's source-internal C2^4 exception.

Group elements are four-bit vectors; XOR is addition. Repetitions are
permitted in sequences. For s_le3's upper bound, repetitions already yield
a zero-sum pair, so enumerating distinct nine-element supports is complete.
"""
from functools import reduce
from itertools import combinations, combinations_with_replacement
import json
from operator import xor


def has_zero_subsequence(sequence, maximum):
    return any(reduce(xor, subsequence, 0) == 0
               for length in range(1, min(maximum, len(sequence)) + 1)
               for subsequence in combinations(sequence, length))


def check():
    group = range(16)
    basis = (1, 2, 4, 8)
    assert not has_zero_subsequence(basis, 4)
    d_upper_count = 0
    for sequence in combinations_with_replacement(group, 5):
        assert has_zero_subsequence(sequence, 5)
        d_upper_count += 1
    affine_hyperplane = tuple(range(8, 16))
    assert not has_zero_subsequence(affine_hyperplane, 3)
    assert not has_zero_subsequence(affine_hyperplane[:7], 3)
    s_upper_count = 0
    for support in combinations(group, 9):
        assert has_zero_subsequence(support, 3)
        s_upper_count += 1
    for x in group:
        assert has_zero_subsequence((x, x), 2)
    rank, exponent, d, d_star, k, short_constant = 4, 2, 5, 1 + 4 * (2 - 1), 2, 9
    assert rank >= 2 and d == d_star and k > 0
    assert exponent <= d - k <= d and 2 * (d - k) >= d + 1
    assert short_constant > d + k
    return {"result": "PASS", "group": "C_2^4", "rank": rank, "exponent": exponent,
            "D": d, "D_star": d_star, "k": k, "D_minus_k": d-k,
            "conjectured_upper_bound": d+k, "actual_short_zero_sum_constant": short_constant,
            "zero_sum_free_length_4": list(basis), "short_zero_sum_free_length_8": list(affine_hyperplane),
            "length_5_multisets_checked": d_upper_count, "length_9_distinct_supports_checked": s_upper_count,
            "repetition_case": "Every repeated vector gives a zero-sum pair",
            "provenance": "SOURCE_INTERNAL_CONTRADICTION_NOT_MODEL_DISCOVERY"}


if __name__ == "__main__":
    print(json.dumps(check(), indent=2))
