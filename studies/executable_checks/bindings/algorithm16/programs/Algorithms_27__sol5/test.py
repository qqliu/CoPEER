#!/usr/bin/env python3
"""
Blind test-search for record Algorithms_27__sol5.

TARGET CLAIM (CORRECTNESS), as quoted by triage:
    The transformation "copy the 3m integers of a 3Partition instance S, append 9m
    elements equal to 0, set n = m" is a correct (answer-preserving) many-one
    reduction 3Partition <=_p 12Partition.  In particular (solution lines 0029-0034):
      "Since S' contains 3m non-zero elements and 9m zeros, each Ai must contain
       exactly 3 non-zero elements (because 3m non-zero elements distributed into m
       subsets requires 3 per subset) and 9 zeros."

WHAT IS IMPLEMENTED HERE
  * reduce_faithful(S)  -- the solution's transformation, verbatim: S' = S ++ [0]*9m, n = m.
  * decide_via_reduction(S) -- the answer the solution's reduction claims for S:
        3Partition(S)  ==  12Partition(reduce_faithful(S)).
    Since the reduction asserts an "iff", the reduction, used as a decision procedure,
    outputs 12Partition(S').  This is the "implementation output".
  * ORACLE oracle_3partition(S) -- exhaustive brute force over all partitions of the
    3m elements into m triples with equal sums (exact integer arithmetic only).
  * ORACLE oracle_kpartition(S', n, k=12) -- exhaustive search for a partition of S'
    into n blocks of exactly k elements each with equal sums.  Implemented as a
    complete backtracking search with sound symmetry breaking, and CROSS-VALIDATED on
    small cases against a literally exhaustive C(24,12) enumeration over index subsets.

A BUG is an input S (multiset of 3m positive integers) on which
    12Partition(reduce_faithful(S))  !=  3Partition(S).

All arithmetic is integer.  Deterministic: exhaustive sweep, no randomness.
"""

from itertools import combinations, combinations_with_replacement


# ----------------------------------------------------------------------------
# 1. FAITHFUL IMPLEMENTATION OF THE SOLUTION'S REDUCTION (bugs included)
# ----------------------------------------------------------------------------

def reduce_faithful(S):
    """Solution lines 0010-0017:
         'For each element s_i in S, create a corresponding element s'_i = s_i in S'.
          Additionally, introduce 9m new elements into S', each equal to 0.
          Thus |S'| = 3m + 9m = 12m.  Here, n = m.'
    Verbatim.  Note the padding value is 0 exactly as written (the solution says
    'each equal to 0'); the problem demands positive integers -- that defect is
    recorded but is NOT what the counterexample below relies on.
    """
    assert len(S) % 3 == 0
    m = len(S) // 3
    S_prime = list(S) + [0] * (9 * m)
    n = m
    assert len(S_prime) == 12 * m
    return S_prime, n


def decide_via_reduction(S):
    """The decision the solution's reduction yields for the 3Partition instance S."""
    S_prime, n = reduce_faithful(S)
    return oracle_kpartition(S_prime, n, 12)


# ----------------------------------------------------------------------------
# 2. BRUTE-FORCE ORACLES (exact integer arithmetic)
# ----------------------------------------------------------------------------

def oracle_3partition(S):
    """True iff the multiset S of 3m positive integers can be split into m triples
    of equal sum.  Exhaustive over all triple-partitions."""
    n3 = len(S)
    assert n3 % 3 == 0
    m = n3 // 3
    total = sum(S)
    if total % m != 0:
        return False
    T = total // m
    items = sorted(S, reverse=True)

    def rec(remaining):
        if not remaining:
            return True
        a = remaining[0]
        rest = remaining[1:]
        for i in range(len(rest)):
            for j in range(i + 1, len(rest)):
                if a + rest[i] + rest[j] == T:
                    nxt = rest[:i] + rest[i + 1:j] + rest[j + 1:]
                    if rec(nxt):
                        return True
        return False

    return rec(items)


def oracle_kpartition(elems, n, k):
    """True iff the multiset `elems` (of exactly n*k numbers) can be partitioned into
    n blocks of exactly k elements each, all blocks having the same sum.
    Complete backtracking search: every element is placed; blocks that are currently
    indistinguishable (same running sum AND same running count) are tried only once,
    which is sound symmetry breaking."""
    if len(elems) != n * k:
        return False
    total = sum(elems)
    if total % n != 0:
        return False
    T = total // n
    items = sorted(elems, reverse=True)
    if items and items[0] > T:
        return False

    sums = [0] * n
    cnts = [0] * n
    N = len(items)

    def rec(i):
        if i == N:
            return True
        v = items[i]
        seen = set()
        for b in range(n):
            if cnts[b] >= k:
                continue
            if sums[b] + v > T:
                continue
            key = (sums[b], cnts[b])
            if key in seen:
                continue
            seen.add(key)
            was_empty = (cnts[b] == 0)
            sums[b] += v
            cnts[b] += 1
            ok = rec(i + 1)
            sums[b] -= v
            cnts[b] -= 1
            if ok:
                return True
            if was_empty:
                # all still-empty blocks are interchangeable
                break
        return False

    return rec(0)


def oracle_kpartition_literal(elems, n, k):
    """Literally exhaustive reference for n == 2: enumerate every subset of exactly k
    index positions containing position 0, check both halves have equal sums.
    Used only to cross-validate oracle_kpartition."""
    assert n == 2 and len(elems) == 2 * k
    total = sum(elems)
    if total % 2 != 0:
        return False
    T = total // 2
    idx = list(range(1, 2 * k))
    for rest in combinations(idx, k - 1):
        block = (0,) + rest
        if sum(elems[t] for t in block) == T:
            return True
    return False


# ----------------------------------------------------------------------------
# 3. SEARCH
# ----------------------------------------------------------------------------

def cross_validate():
    """Check oracle_kpartition against the literally exhaustive enumerator on the
    24-element constructed instances of several m=2 cases."""
    cases = [
        (3, 3, 3, 1, 1, 1),
        (2, 2, 2, 3, 3, 6),
        (1, 1, 1, 1, 1, 1),
        (1, 2, 3, 4, 5, 3),
        (5, 5, 5, 5, 5, 5),
        (1, 1, 2, 2, 3, 3),
        (4, 1, 1, 1, 1, 4),
        (2, 3, 4, 5, 1, 1),
    ]
    lines = []
    all_ok = True
    for S in cases:
        Sp, n = reduce_faithful(list(S))
        a = oracle_kpartition(Sp, n, 12)
        b = oracle_kpartition_literal(Sp, n, 12)
        ok = (a == b)
        all_ok = all_ok and ok
        lines.append("    S=%-22s backtracking=%-5s literal_C(23,11)=%-5s %s"
                     % (str(S), a, b, "OK" if ok else "MISMATCH"))
    return all_ok, lines


def sweep(m=2, vmax=5):
    """Exhaustive over all multisets of 3m positive integers with values in 1..vmax."""
    bad = []
    checked = 0
    for S in combinations_with_replacement(range(1, vmax + 1), 3 * m):
        S = list(S)
        checked += 1
        truth = oracle_3partition(S)
        got = decide_via_reduction(S)
        if truth != got:
            bad.append((S, truth, got))
    return checked, bad


def main():
    print("=" * 78)
    print("Algorithms_27__sol5 -- blind test-search")
    print("CLAIM UNDER TEST (CORRECTNESS): 'copy the 3m integers, append 9m zeros,")
    print("  n = m' is an answer-preserving reduction 3Partition -> 12Partition;")
    print("  'each Ai must contain exactly 3 non-zero elements'.")
    print("=" * 78)

    print("\n[0] Oracle cross-validation (backtracking vs literal exhaustive C(23,11)):")
    ok, lines = cross_validate()
    for ln in lines:
        print(ln)
    print("    cross-validation: %s" % ("ALL AGREE" if ok else "FAILED"))
    if not ok:
        print("VERDICT: INCONCLUSIVE (oracle disagreement)")
        return

    print("\n[1] Adversarial constructions from the triage sketches (m=2, |S|=6 <= 12):")
    adversarial = [[3, 3, 3, 1, 1, 1], [2, 2, 2, 3, 3, 6]]
    first_hit = None
    for S in adversarial:
        Sp, n = reduce_faithful(S)
        truth = oracle_3partition(S)
        got = decide_via_reduction(S)
        lit = oracle_kpartition_literal(Sp, n, 12)
        print("    S=%-18s |S'|=%d n=%d  target T=%d" % (str(S), len(Sp), n, sum(S) // n))
        print("        oracle 3Partition(S)        = %s" % truth)
        print("        12Partition(S') [backtrack] = %s" % got)
        print("        12Partition(S') [literal]   = %s" % lit)
        print("        agree? %s" % ("yes" if truth == got else "NO  <-- REDUCTION IS WRONG"))
        if truth != got and first_hit is None:
            first_hit = (S, truth, got)

    print("\n[2] Exhaustive sweep: every multiset of 6 positive integers, values 1..5")
    checked, bad = sweep(m=2, vmax=5)
    print("    instances checked : %d" % checked)
    print("    mismatches found  : %d" % len(bad))
    for S, truth, got in bad[:10]:
        print("        S=%-22s oracle=%-5s reduction=%-5s" % (str(S), truth, got))
    if len(bad) > 10:
        print("        ... (%d more)" % (len(bad) - 10))

    if first_hit is None and bad:
        first_hit = bad[0]

    print("\n[3] Witness detail for the smallest mismatch:")
    if first_hit is not None:
        S, truth, got = first_hit
        Sp, n = reduce_faithful(S)
        T = sum(S) // n
        print("    S  = %s   (m=%d, 3Partition target T=%d)" % (S, len(S) // 3, T))
        print("    S' = S ++ [0]*%d, n=%d, |S'|=%d" % (9 * (len(S) // 3), n, len(Sp)))
        print("    oracle_3partition(S)        = %s" % truth)
        print("    12Partition(S') (exhaustive)= %s" % got)
        # exhibit the witnessing 12-partition
        witness = None
        for rest in combinations(range(1, 24), 11):
            block = (0,) + rest
            if sum(Sp[t] for t in block) == T:
                b1 = sorted((Sp[t] for t in block), reverse=True)
                other = [t for t in range(24) if t not in set(block)]
                b2 = sorted((Sp[t] for t in other), reverse=True)
                witness = (b1, b2)
                break
        if witness:
            b1, b2 = witness
            print("    witnessing 12Partition of S':")
            print("        A1 = %s  (12 elements, sum=%d, %d nonzero)"
                  % (b1, sum(b1), sum(1 for x in b1 if x)))
            print("        A2 = %s  (12 elements, sum=%d, %d nonzero)"
                  % (b2, sum(b2), sum(1 for x in b2 if x)))
            print("    -> the counts of NON-ZERO elements per block are %d and %d, not 3 and 3;"
                  % (sum(1 for x in b1 if x), sum(1 for x in b2 if x)))
            print("       the solution's line 0031-0032 forcing argument is false.")

    print("\n" + "=" * 78)
    if first_hit is not None or bad:
        print("VERDICT: BUG_FOUND -- the reduction is NOT answer-preserving.")
    else:
        print("VERDICT: NO_BUG_FOUND over the searched family.")
    print("Secondary defect (not needed for the counterexample): the 9m padding")
    print("elements are 0, but 12Partition's input must be POSITIVE integers.")
    print("=" * 78)


if __name__ == "__main__":
    main()
