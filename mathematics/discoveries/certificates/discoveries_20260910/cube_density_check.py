#!/usr/bin/env python3
"""Exact standalone certificate for the cyclic 5-cube density counterexample.

Run with Python 3; no external packages or experiment files are needed.
We check every five-entry multiset in Z_16, including repetitions and zero,
and all 31 nonempty indexed subsets, including the full index set. Sorting
does not alter the collection of subset sums, so multisets cover every
ordered tuple. A successful finite obstruction lifts from Z_16 to Z_80.
"""

import json
from fractions import Fraction
from itertools import combinations_with_replacement
from math import comb


def require(condition, message):
    if not condition:
        raise ValueError(message)


def check():
    d, modulus, quotient = 5, 80, 16
    forbidden = frozenset({0, 4, 12})
    masks = tuple(range(1, 1 << d))
    require(len(masks) == 31 and masks[-1] == 31, "subset coverage")

    multisets_checked = 0
    subset_sums_checked = 0
    for generators in combinations_with_replacement(range(quotient), d):
        hits = []
        for mask in masks:
            residue = sum(
                generators[index] for index in range(d) if mask & (1 << index)
            ) % quotient
            subset_sums_checked += 1
            if residue in forbidden:
                hits.append(mask)
        require(bool(hits), f"finite obstruction fails for {generators}")
        multisets_checked += 1
    require(multisets_checked == comb(quotient + d - 1, d) == 15504,
            "multiset coverage")
    require(subset_sums_checked == multisets_checked * 31 == 480624,
            "indexed-subset coverage")

    require(modulus % d == 0, "source divisibility condition d | N")
    require(modulus % quotient == 0, "quotient divisibility condition Q | N")
    group = tuple(range(modulus))
    projection = tuple(x % quotient for x in group)
    require(set(projection) == set(range(quotient)), "projection surjectivity")
    fibers = [projection.count(residue) for residue in range(quotient)]
    require(fibers == [5] * 16, "equal projection fibers")
    homomorphism_pairs_checked = 0
    for x in group:
        for y in group:
            require(projection[(x + y) % modulus]
                    == (projection[x] + projection[y]) % quotient,
                    "projection is additive")
            homomorphism_pairs_checked += 1

    allowed = tuple(x for x in group if projection[x] not in forbidden)
    complement = tuple(x for x in group if projection[x] in forbidden)
    bound = Fraction(d - 1, d) * modulus
    require(len(allowed) == 65 and len(complement) == 15, "cardinalities")
    require(len(allowed) == (quotient - len(forbidden)) * (modulus // quotient),
            "cardinality from quotient fibers")
    require(bound == 64 and len(allowed) > bound, "strict bound violation")

    return {
        "certificate": "cyclic-cube-free-density-counterexample",
        "status": "PASS",
        "d": d,
        "N": modulus,
        "quotient_modulus": quotient,
        "forbidden_quotient_residues": sorted(forbidden),
        "all_quotient_multisets_checked": multisets_checked,
        "nonempty_indexed_subsets_per_multiset": len(masks),
        "indexed_subset_sums_checked": subset_sums_checked,
        "repetitions_and_zeros_included": True,
        "full_index_set_included": True,
        "homomorphism_pairs_checked": homomorphism_pairs_checked,
        "quotient_fiber_sizes": fibers,
        "complement_in_Z80": list(complement),
        "A_cardinality": len(allowed),
        "conjectured_upper_bound": str(bound),
        "strict_excess": str(len(allowed) - bound),
    }


if __name__ == "__main__":
    print(json.dumps(check(), indent=2, sort_keys=True))
