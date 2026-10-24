#!/usr/bin/env python3
"""Independent exact certificate for rf_numbers_semigroup_leaf_type_bound.

Run with Python 3. No external packages, floating-point arithmetic, searches over
other semigroups, or reads of any other solution are used.

Infinite-domain reductions used by this finite checker:

1. S is defined by an explicitly enumerated prefix and the complete tail n>=50.
   The minimum positive element is 25, so any two positive elements sum to an
   integer >=50. Addition by zero preserves membership. The complement in N is
   therefore precisely the finitely enumerated gaps below 50.

2. Any n>=50+25 decomposes as 25+(n-25), with both summands positive in S.
   Consequently every minimal generator is below 75. Below 75 we test all
   possible positive two-summand decompositions, independently of the draft's
   proposed decompositions. A strong induction on n now proves that the set of
   indecomposable elements generates S: every other positive n is a sum of two
   smaller positive elements, to each of which the induction hypothesis applies.
   Conversely an indecomposable element must occur in every generating set.

3. For a positive gap x, all positive s in S with s>=50-x give x+s>=50 in S.
   Thus it is necessary and sufficient to test the finite set of positive s in S
   below 50-x. We apply this test to EVERY positive gap, without assuming that the
   listed H and P are exhaustive. Separately, testing all minimal generators is
   sufficient: express any positive s as a sum of generators and use closure
   after adding the first generator. We also perform this independent check.

4. For x<=-26, adding 25 gives x+25<=-1, outside S. For -24<=x<=-1,
   adding 25 gives a gap from 1 to 24, all tested below. For x=-25, adding 26
   gives the gap 1. This covers ALL negative integers, not a bounded sample.
   Zero belongs to S; every integer >=50 belongs to S. Together with item 3,
   these observations enumerate all pseudo-Frobenius numbers in Z\\S.

The printed finite data and the reductions above form the exact certificate.
"""

import json


CONDUCTOR = 50
A = set([25, 26, 28, 30, 31]) | set(range(38, 49))
H = set([27, 29, 32, 33, 34, 35, 36, 37, 49])
P = set([13, 14, 15, 16, 17, 20, 22])


def in_semigroup(n):
    return n == 0 or n in A or n >= CONDUCTOR


def verify():
    # Derive the positive prefix and gaps directly from the membership predicate.
    assert all(type(n) is int and 0 < n < CONDUCTOR for n in A)
    assert in_semigroup(0)
    positive_prefix = [n for n in range(1, CONDUCTOR) if in_semigroup(n)]
    multiplicity = min(positive_prefix)
    assert multiplicity == 25
    assert 2 * multiplicity >= CONDUCTOR
    # The last inequality plus the defined tail proves closure for all S.
    assert all(in_semigroup(a + b) for a in positive_prefix for b in positive_prefix)
    gaps = [n for n in range(CONDUCTOR) if not in_semigroup(n)]
    assert gaps == list(range(1, 25)) + [27, 29, 32, 33, 34, 35, 36, 37, 49]
    genus = len(gaps)
    frobenius = max(gaps)
    assert genus == 33 and frobenius == 49
    assert frobenius + 1 == CONDUCTOR

    # Exhaust ALL possible minimal generators by the proof in the docstring.
    generator_cutoff = CONDUCTOR + multiplicity
    atomic = []
    decompositions = {}
    for n in range(1, generator_cutoff):
        if not in_semigroup(n):
            continue
        split = next(((a, n - a) for a in range(1, n)
                      if in_semigroup(a) and in_semigroup(n - a)), None)
        if split is None:
            atomic.append(n)
        else:
            a, b = split
            assert 0 < a < n and 0 < b < n
            assert a + b == n and in_semigroup(a) and in_semigroup(b)
            decompositions[n] = [a, b]
    assert atomic == sorted(A)
    assert list(decompositions) == list(range(CONDUCTOR, generator_cutoff))
    assert in_semigroup(multiplicity)
    assert generator_cutoff - multiplicity == CONDUCTOR
    assert CONDUCTOR > 0
    # For any n>=generator_cutoff, n-multiplicity>=CONDUCTOR is in S.
    assert all(a <= frobenius for a in atomic)
    assert max(atomic) == 48

    # Check the draft's finite additive identity as an additional proof audit.
    E = {0, 1, 3, 5, 6}
    D = {25 + e for e in E}
    assert D == {25, 26, 28, 30, 31}
    E_plus_E = {a + b for a in E for b in E}
    assert E_plus_E == set(range(13))
    assert {a + b for a in D for b in D} == set(range(50, 63))
    assert all(n - 25 in A for n in range(63, 74))
    assert 26 + 48 == 74 and 26 in A and 48 in A

    # Complete PF computation via the conductor, not merely proposed inclusions.
    pf_direct = []
    positive_gap_obstructions = {}
    pf_finite_checks = {}
    for x in gaps:
        tested_s = [s for s in range(1, CONDUCTOR - x) if in_semigroup(s)]
        failures = [s for s in tested_s if not in_semigroup(x + s)]
        if failures:
            s = failures[0]
            assert s > 0 and in_semigroup(s) and not in_semigroup(x + s)
            positive_gap_obstructions[x] = [s, x + s]
        else:
            pf_direct.append(x)
            pf_finite_checks[x] = [[s, x + s] for s in tested_s]
    pf_generators = [x for x in gaps if all(in_semigroup(x + a) for a in atomic)]
    assert pf_direct == pf_generators
    assert H <= set(gaps) and P <= set(gaps) and not H & P
    assert len(H) == 9 and len(P) == 7
    assert set(pf_direct) == H | P

    # Check every addend and obstruction explicitly used by the submitted proof.
    assert min(H) + multiplicity >= CONDUCTOR
    assert min(P) + min(A - D) >= CONDUCTOR
    assert all(all(38 <= x + d <= 48 for d in D) for x in range(13, 18))
    assert {20 + d for d in D} == {45, 46, 48, 50, 51}
    assert {22 + d for d in D} == {47, 48, 50, 52, 53}
    draft_obstructions = {1: 26, 3: 26, 6: 26,
                          2: 25, 4: 25, 7: 25, 8: 25, 9: 25, 10: 25,
                          11: 25, 12: 25, 5: 28,
                          18: 31, 19: 30, 21: 28, 23: 26, 24: 25}
    assert set(draft_obstructions) == set(gaps) - (H | P)
    assert all(s > 0 and in_semigroup(s) and not in_semigroup(x + s)
               for x, s in draft_obstructions.items())

    # Negative integers: the finite middle interval and the infinite tail proof.
    negative_obstructions = {}
    for x in range(-multiplicity + 1, 0):
        s = multiplicity
        assert 1 <= x + s < multiplicity
        assert not in_semigroup(x) and in_semigroup(s) and not in_semigroup(x + s)
        negative_obstructions[x] = [s, x + s]
    x = -multiplicity
    s = 26
    assert in_semigroup(s) and x + s == 1 and not in_semigroup(x + s)
    negative_obstructions[x] = [s, x + s]
    infinite_negative_boundary = -multiplicity - 1
    assert infinite_negative_boundary + multiplicity == -1
    assert all(n >= 0 for n in A) and CONDUCTOR > 0
    # Hence for EVERY x<=infinite_negative_boundary, x+25<=-1 is outside S.

    semigroup_type = len(pf_direct)
    assert semigroup_type == 16
    assert genus >= 2
    q, r = divmod(genus, 4)
    assert 0 <= r < 4 and genus == 4 * q + r
    bound = 2 * q - 1 if r in (0, 1) else (2 * q if r == 2 else 2 * q + 1)
    assert (q, r, bound) == (8, 1, 15)
    assert semigroup_type > bound

    return {
        "record_id": "rf_numbers_semigroup_leaf_type_bound",
        "witness": {"zero": 0, "positive_prefix": positive_prefix,
                    "all_integers_at_least": CONDUCTOR},
        "multiplicity": multiplicity,
        "frobenius": frobenius,
        "gaps": gaps,
        "genus": genus,
        "minimal_generators": atomic,
        "finite_decompositions": decompositions,
        "infinite_decomposition": "For every n>=75: n=25+(n-25), n-25>=50.",
        "E_plus_E": sorted(E_plus_E),
        "leaf": True,
        "pseudo_frobenius": pf_direct,
        "positive_PF_finite_checks": pf_finite_checks,
        "other_positive_gap_obstructions_x_to_s_and_sum": positive_gap_obstructions,
        "negative_obstructions_x_to_s_and_sum": negative_obstructions,
        "infinite_negative_obstruction": "For every x<=-26: s=25, x+s<=-1 outside S.",
        "type": semigroup_type,
        "q": q,
        "r": r,
        "conjectured_bound": bound,
        "strict_violation": "16 > 15",
        "verified_claim_indices": list(range(9)),
        "status": "PASS"
    }


if __name__ == "__main__":
    print(json.dumps(verify(), indent=2, sort_keys=True))
