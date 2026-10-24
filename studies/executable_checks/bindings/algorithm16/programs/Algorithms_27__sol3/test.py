#!/usr/bin/env python3
"""
Blind test-search for Algorithms_27__sol3.

TARGET CLAIM (quoted by triage passes 0 and 1):
    "where Cj depends only on the indices. Since each index appears in exactly one
     partition set, all Aj have the same sum."
i.e. the forward direction of the claimed reduction 3-Partition <=p 12Partition:
grouping all four copies of the three elements of each 3-Partition block T_j yields
12-element subsets A_j that all have the same sum -- and more generally that the
reduction is a correct many-one reduction (T is a yes-instance of 3-Partition
IFF S = reduce(T,B) is a yes-instance of 12Partition).

FAITHFUL IMPLEMENTATION (solution lines 0021-0038, 0123-0136):
    K = 1 + sum_i t_i = 1 + mB
    s^(j)_i = t_i + j * K * 4^(3m+1-i)   for i = 1..3m, j = 1..4
    S = { s^(j)_i }   (12m elements)
    forward map: A_j = all four copies of each of the three elements of T_j

ORACLE:
    - exact brute-force 3-Partition decision (exhaustive over triple partitions)
    - exact brute-force 12Partition decision for m = 2 (|S| = 24), done two ways:
      (a) meet-in-the-middle over (count,sum) states  -- used for the sweep
      (b) plain exhaustive itertools.combinations over all C(23,11) splits
          -- used as an independent cross-check on the headline instances
    All arithmetic is exact Python int. No floats decide anything.

Deterministic: no randomness anywhere.
"""

import itertools
from fractions import Fraction

# --------------------------------------------------------------------------
# 1. FAITHFUL IMPLEMENTATION OF THE SOLUTION'S CONSTRUCTION
# --------------------------------------------------------------------------

def reduction_K(T):
    """K = 1 + sum of all original elements (solution line 0037-0038)."""
    return 1 + sum(T)


def reduce_3P_to_12P(T):
    """
    Faithful transcription of construction (1), solution lines 0023-0035.

    T is 1-indexed in the paper: T = (t_1, ..., t_{3m}).  Here T is a Python list
    with T[i-1] = t_i.  Returns a list of (i, j, value) triples in the order the
    solution writes them: i = 1..3m outer, j = 1..4 inner.
    """
    assert len(T) % 3 == 0
    m = len(T) // 3
    K = reduction_K(T)
    out = []
    for i in range(1, 3 * m + 1):
        t_i = T[i - 1]
        w = 4 ** (3 * m + 1 - i)          # positional weight 4^{3m+1-i}
        for j in (1, 2, 3, 4):
            out.append((i, j, t_i + j * K * w))
    return out


def S_values(T):
    return [v for (_i, _j, v) in reduce_3P_to_12P(T)]


def forward_subsets(T, blocks):
    """
    Faithful transcription of the Forward Direction, solution lines 0123-0133:
    for each 3-Partition block T_j (given as a list of 1-based indices into T),
    A_j = { s^(l)_{i_k} : k in {1,2,3}, l in {1,2,3,4} }.
    Returns list of (block_indices, A_j as list of values).
    """
    elems = reduce_3P_to_12P(T)
    by_index = {}
    for (i, j, v) in elems:
        by_index.setdefault(i, []).append(v)
    res = []
    for blk in blocks:
        A = []
        for i in blk:
            A.extend(by_index[i])
        res.append((tuple(blk), A))
    return res


def claimed_subset_sum(T, blk):
    """Solution's own formula (7): sum(A_j) = 4B + 10K * C_j, C_j = sum of weights."""
    m = len(T) // 3
    K = reduction_K(T)
    B = sum(T) // m
    C = sum(4 ** (3 * m + 1 - i) for i in blk)
    return 4 * B + 10 * K * C, C


# --------------------------------------------------------------------------
# 2. BRUTE-FORCE ORACLES (exact integer arithmetic only)
# --------------------------------------------------------------------------

def oracle_3partition(T, B):
    """
    Exhaustive: can T (3m integers) be split into m triples each summing to B?
    Recursive exact search over index sets.
    """
    n = len(T)
    m = n // 3
    if sum(T) != m * B:
        return False, None
    idx = list(range(n))

    def rec(remaining, acc):
        if not remaining:
            return acc
        first = remaining[0]
        rest = remaining[1:]
        for a, b in itertools.combinations(range(len(rest)), 2):
            if T[first] + T[rest[a]] + T[rest[b]] == B:
                nxt = [x for k, x in enumerate(rest) if k not in (a, b)]
                r = rec(nxt, acc + [(first + 1, rest[a] + 1, rest[b] + 1)])
                if r is not None:
                    return r
        return None

    got = rec(idx, [])
    return (got is not None), got


def oracle_12partition_m2_mitm(vals):
    """
    Exact decision for m=2: can the 24 values be split into two 12-element
    subsets of equal sum?  Meet in the middle over (count, sum) states.
    Returns (bool, witness_index_set_or_None).
    """
    n = len(vals)
    assert n == 24
    tot = sum(vals)
    if tot % 2 != 0:
        return False, None
    half = tot // 2
    A, Bv = vals[:12], vals[12:]

    tableB = {}
    for mask in range(1 << 12):
        c = 0
        s = 0
        mm = mask
        k = 0
        while mm:
            if mm & 1:
                c += 1
                s += Bv[k]
            mm >>= 1
            k += 1
        tableB.setdefault((c, s), mask)

    for mask in range(1 << 12):
        c = 0
        s = 0
        mm = mask
        k = 0
        while mm:
            if mm & 1:
                c += 1
                s += A[k]
            mm >>= 1
            k += 1
        if s > half:
            continue
        key = (12 - c, half - s)
        if key in tableB:
            mb = tableB[key]
            sel = [i for i in range(12) if mask >> i & 1] + \
                  [12 + i for i in range(12) if mb >> i & 1]
            return True, sel
    return False, None


def oracle_12partition_m2_exhaustive(vals):
    """
    Independent, dumbest-possible oracle for m=2: enumerate every 12-subset that
    contains element 0 (i.e. all C(23,11) = 1352078 distinct splits) and test
    whether its sum equals half the total.  Exact ints only.
    """
    n = len(vals)
    assert n == 24
    tot = sum(vals)
    if tot % 2 != 0:
        return False, None
    half = tot // 2
    rest = list(range(1, n))
    v0 = vals[0]
    checked = 0
    for comb in itertools.combinations(rest, 11):
        checked += 1
        s = v0
        for i in comb:
            s += vals[i]
        if s == half:
            return True, (0,) + comb
    return False, None


# --------------------------------------------------------------------------
# 3. INSTANCE FAMILY (bounded, exhaustive) -- 3-Partition promise instances
# --------------------------------------------------------------------------

def promise_instances(m=2, Bmin=9, Bmax=20):
    """
    All multisets T of 3m positive integers with B/4 < t_i < B/2 (strict) and
    sum(T) = m*B, for B in [Bmin, Bmax].  |T| = 3m <= 12 (input size bound).
    Uses Fraction for the B/4 and B/2 bounds so no float ever decides anything.
    """
    out = []
    k = 3 * m
    for B in range(Bmin, Bmax + 1):
        lo = Fraction(B, 4)
        hi = Fraction(B, 2)
        cand = [t for t in range(1, B) if lo < t < hi]
        if not cand:
            continue
        for T in itertools.combinations_with_replacement(cand, k):
            if sum(T) == m * B:
                out.append((list(T), B))
    return out


# --------------------------------------------------------------------------
# 4. MAIN
# --------------------------------------------------------------------------

def show_forward_direction(T, B, label):
    m = len(T) // 3
    ok3, blocks = oracle_3partition(T, B)
    print("  T = %s, B = %d, m = %d, K = %d" % (T, B, m, reduction_K(T)))
    print("  3-Partition (oracle, exhaustive): %s" % ("YES" if ok3 else "NO"))
    if not ok3:
        return None
    print("  witness blocks (1-based indices into T): %s" % (blocks,))
    subs = forward_subsets(T, [list(b) for b in blocks])
    sums = []
    for (blk, A) in subs:
        s = sum(A)
        claimed, C = claimed_subset_sum(T, blk)
        assert s == claimed, "implementation disagrees with solution formula (7)"
        sums.append(s)
        print("    A_%s : |A|=%d  C_j=%d  sum(A_j)=%d = 4B + 10K*C_j" %
              (blk, len(A), C, s))
    print("  all A_j sums equal (solution's claim)? %s" %
          ("YES" if len(set(sums)) == 1 else "NO  <-- CLAIM REFUTED"))
    print("  pairwise difference: %s" %
          ([sums[a] - sums[b] for a, b in itertools.combinations(range(len(sums)), 2)],))
    return sums


def oracle_self_test():
    """Sanity: the m=2 oracles must be able to answer NO, and must agree."""
    cases = [
        [1] * 23 + [3],                       # total 26, half 13, but any 12-subset
                                              # sums to 12 or 14 -> NO
        [1] * 24,                             # -> YES
        [1] * 12 + [2] * 12,                  # -> YES (6 ones + 6 twos each side)
        [1] * 11 + [5] + [1] * 12,            # total 28, half 14; 12-subset sums
                                              # are 12 or 16 -> NO
    ]
    expected = [False, True, True, False]
    ok = True
    for vals, exp in zip(cases, expected):
        a, _ = oracle_12partition_m2_mitm(vals)
        b, _ = oracle_12partition_m2_exhaustive(vals)
        if a != b or a != exp:
            ok = False
        print("    vals=%s...  mitm=%s exhaustive=%s expected=%s  %s"
              % (vals[:4], a, b, exp, "OK" if (a == b == exp) else "FAIL"))
    # 3-Partition oracle sanity
    y, _ = oracle_3partition([1, 2, 3, 1, 2, 3], 6)
    n, _ = oracle_3partition([1, 1, 1, 1, 1, 7], 6)
    print("    3P oracle: [1,2,3,1,2,3],B=6 -> %s (want YES); "
          "[1,1,1,1,1,7],B=6 -> %s (want NO)" % (y, n))
    ok = ok and y and not n
    print("    oracle self-test: %s" % ("PASS" if ok else "FAIL"))
    assert ok, "oracle self-test failed"


def main():
    print("=" * 78)
    print("Algorithms_27__sol3  --  blind test-search")
    print("target claim: forward direction of the reduction; 'all Aj have the same sum'")
    print("=" * 78)
    print()
    print("[PART 0] Oracle self-test.")
    oracle_self_test()

    # ---------------- Part 1: the quoted claim, on triage instances ----------
    print()
    print("[PART 1] Direct refutation of the quoted forward-direction claim.")
    print()
    print(" instance A (triage p0): T = (5,5,5,5,5,5), B = 15")
    T_a, B_a = [5, 5, 5, 5, 5, 5], 15
    sums_a = show_forward_direction(T_a, B_a, "A")
    print()
    print(" instance B (triage p1): T = (5,5,6,5,5,6), B = 16")
    T_b, B_b = [5, 5, 6, 5, 5, 6], 16
    sums_b = show_forward_direction(T_b, B_b, "B")

    claim_refuted = (len(set(sums_a)) > 1) and (len(set(sums_b)) > 1)
    print()
    print(" => quoted claim 'all Aj have the same sum' is FALSE on both: %s" % claim_refuted)
    print("    reason: sum(A_j) = 4B + 10K*C_j with C_j = sum of distinct powers 4^(3m+1-i)")
    print("            over A_j's three indices; distinct index sets give distinct C_j.")

    # ---------------- Part 2: does the reduction even preserve the answer? ---
    print()
    print("[PART 2] Exhaustive sweep: is 'T yes-instance of 3-Partition'  <=>")
    print("         'S = reduce(T,B) yes-instance of 12Partition'  ?")
    print("         family: all promise instances with m=2 (|T|=6 <= 12), B in [9,20].")
    print()
    fam = promise_instances(m=2, Bmin=9, Bmax=20)
    print("  family size: %d instances" % len(fam))

    mism_no_to_yes = []   # 3P = NO  but 12P = YES  (reduction unsound)
    mism_yes_to_no = []   # 3P = YES but 12P = NO   (reduction incomplete)
    agree = 0
    for (T, B) in fam:
        ok3, _ = oracle_3partition(T, B)
        vals = S_values(T)
        ok12, _w = oracle_12partition_m2_mitm(vals)
        if ok3 == ok12:
            agree += 1
        elif ok12 and not ok3:
            mism_no_to_yes.append((T, B))
        else:
            mism_yes_to_no.append((T, B))
    print("  agreeing instances                      : %d" % agree)
    print("  3P=NO  but 12P=YES (reduction UNSOUND)  : %d" % len(mism_no_to_yes))
    print("  3P=YES but 12P=NO  (reduction INCOMPLETE): %d" % len(mism_yes_to_no))

    headline = None
    if mism_no_to_yes:
        headline = min(mism_no_to_yes, key=lambda tb: (tb[1], tb[0]))
        print()
        print("  smallest 3P=NO / 12P=YES counterexample: T = %s, B = %d" % headline)

    # ---------------- Part 3: independent exhaustive cross-check ------------
    print()
    print("[PART 3] Independent exhaustive cross-check (all C(23,11)=1352078 splits)")
    print("         on the headline counterexample and on instance B.")
    print()
    to_check = []
    if headline:
        to_check.append(("headline (3P = NO)", headline[0], headline[1]))
    to_check.append(("instance B (3P = YES)", T_b, B_b))
    for (label, T, B) in to_check:
        vals = S_values(T)
        ok3, blocks = oracle_3partition(T, B)
        mit, wm = oracle_12partition_m2_mitm(vals)
        ex, we = oracle_12partition_m2_exhaustive(vals)
        assert mit == ex, "the two oracles disagree -- oracle bug"
        print("  %s : T=%s B=%d K=%d" % (label, T, B, reduction_K(T)))
        print("    3-Partition(T,B)              = %s" % ("YES" if ok3 else "NO"))
        print("    12Partition(S) [meet-in-middle] = %s" % ("YES" if mit else "NO"))
        print("    12Partition(S) [exhaustive]     = %s" % ("YES" if ex else "NO"))
        if ex:
            sel = set(we)
            elems = reduce_3P_to_12P(T)
            A1 = [elems[i] for i in range(24) if i in sel]
            A2 = [elems[i] for i in range(24) if i not in sel]
            print("    witness A1 (i,j) = %s  sum=%d" %
                  ([(i, j) for (i, j, _v) in A1], sum(v for (_i, _j, v) in A1)))
            print("    witness A2 (i,j) = %s  sum=%d" %
                  ([(i, j) for (i, j, _v) in A2], sum(v for (_i, _j, v) in A2)))
            print("    (note: each index i contributes copies {1,4} to one side and")
            print("     {2,3} to the other; 1+4 = 2+3 = 5, so the huge K*4^e weights")
            print("     cancel exactly -- this split exists for EVERY m=2 instance,")
            print("     independently of whether T is a 3-Partition yes-instance.)")

    # ---------------- Verdict ------------------------------------------------
    print()
    print("=" * 78)
    if claim_refuted and mism_no_to_yes:
        print("VERDICT: BUG_FOUND")
        print()
        print("(1) The quoted claim is false. For T=(5,5,6,5,5,6), B=16 (a 3-Partition")
        print("    yes-instance) the forward-direction subsets have sums")
        print("      sum(A_1) = %d  and  sum(A_2) = %d   (difference %d)."
              % (sums_b[0], sums_b[1], sums_b[0] - sums_b[1]))
        print("    'Since each index appears in exactly one partition set, all Aj have")
        print("    the same sum' is a non sequitur: C_j is a sum of DISTINCT powers of 4")
        print("    determined by which indices land in block j, so C_j varies with j.")
        print()
        print("(2) The reduction is not even answer-preserving. For T=%s, B=%d the"
              % (headline[0], headline[1]))
        print("    oracle says 3-Partition is NO, but the constructed S IS a yes-instance")
        print("    of 12Partition (confirmed by exhaustive enumeration of all 1352078")
        print("    splits). So Lemma 3 and the Reverse Direction are false too: the")
        print("    {1,4} / {2,3} split of each index's four copies balances every weight.")
    else:
        print("VERDICT: NO_BUG_FOUND")
    print("=" * 78)


if __name__ == "__main__":
    main()
