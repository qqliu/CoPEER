#!/usr/bin/env python3
"""
INDEPENDENT VERIFIER oracle for record Algorithms_11__sol3.

Written from scratch; imports nothing from test.py.  Deliberately uses a
different internal representation from the reported test (named vertices +
frozensets + edge-list independence checks + explicit DFS stack, instead of
bitmasks + BFS) so that a coding mistake would not coincide.

What is being checked (the solution's OWN definitions, quoted line numbers):

  0015-0019  state (L, R, c);  initial (V, {}, left);  goal ({}, V, right)
  0020-0023  a state is valid iff the bank Charon is NOT on is independent in G
  0024-0026  a move ships any subset S of Charon's bank with |S| <= k-1,
             and flips Charon's side
  0030-0035  reduction:  n = 3m, three copies v(1),v(2),v(3) per v in VH,
             EG = {(u(i),v(i)) : (u,v) in EH} U {(v(i),v(j)) : v in VH, i != j},
             k = m+1
  0043-0044  Claim 1: H 3-colorable  <=>  constructed instance is crossable
  0054-0063  the solution's own forward schedule (ship C1, return, C2, return, C3)

Everything is exact integer / set arithmetic.  No floats, no randomness, no
timing, no heuristics: reachability is a complete DFS over the finite state
space, and 3-colorability is complete enumeration of all 3^m colorings.
"""

import itertools
import sys


# --------------------------------------------------------------------------
# The reduction, transcribed independently from the solution text.
# Vertices of G are strings "v<idx>(<copy>)".
# --------------------------------------------------------------------------

def reduce_3col_to_river(m, EH):
    """Return (n, k, VG, EG) exactly as solution lines 0029-0035 specify."""
    VG = frozenset("v%d(%d)" % (v, i) for v in range(m) for i in (1, 2, 3))
    EG = set()
    for (u, v) in EH:                                   # (u,v) in EH, i = j
        for i in (1, 2, 3):
            EG.add(frozenset(("v%d(%d)" % (u, i), "v%d(%d)" % (v, i))))
    for v in range(m):                                  # v(i), v(j) with i != j
        for i in (1, 2, 3):
            for j in (1, 2, 3):
                if i < j:
                    EG.add(frozenset(("v%d(%d)" % (v, i), "v%d(%d)" % (v, j))))
    n = 3 * m
    k = m + 1
    assert len(VG) == n
    return n, k, VG, frozenset(EG)


def is_independent(S, EG):
    """True iff no edge of G has both endpoints inside the set S."""
    for e in EG:
        a, b = tuple(e)
        if a in S and b in S:
            return False
    return True


def is_valid_state(L, R, c, EG):
    """Solution 0020-0023: unattended bank must be independent."""
    if c == 'L':
        return is_independent(R, EG)
    if c == 'R':
        return is_independent(L, EG)
    raise ValueError(c)


def moves(state, k, EG):
    """Solution 0024-0026.  Yields every valid successor state."""
    L, R, c = state
    here = L if c == 'L' else R
    here = sorted(here)
    out = []
    for size in range(0, k):                 # |S| <= k-1, S may be empty
        for S in itertools.combinations(here, size):
            S = frozenset(S)
            if c == 'L':
                nxt = (L - S, R | S, 'R')
            else:
                nxt = (L | S, R - S, 'L')
            if is_valid_state(nxt[0], nxt[1], nxt[2], EG):
                out.append(nxt)
    return out


def crossable(n, k, VG, EG):
    """Complete DFS reachability.  Returns (bool, witness_path_or_None)."""
    start = (VG, frozenset(), 'L')
    goal = (frozenset(), VG, 'R')
    if not is_valid_state(*start, EG=EG):
        return False, None
    if start == goal:
        return True, []
    seen = {start}
    stack = [(start, [])]
    while stack:
        st, path = stack.pop()
        for nxt in moves(st, k, EG):
            if nxt in seen:
                continue
            if nxt == goal:
                return True, path + [nxt]
            seen.add(nxt)
            stack.append((nxt, path + [nxt]))
    return False, None


def three_colorable(m, EH):
    """Complete enumeration of all 3^m colorings."""
    for chi in itertools.product((1, 2, 3), repeat=m):
        if all(chi[u] != chi[v] for (u, v) in EH):
            return True, chi
    return False, None


def all_labelled_graphs(m):
    pairs = list(itertools.combinations(range(m), 2))
    for bits in range(1 << len(pairs)):
        yield tuple(pairs[t] for t in range(len(pairs)) if (bits >> t) & 1)


# --------------------------------------------------------------------------
# Checks
# --------------------------------------------------------------------------

def check_reported_failing_input():
    print("### A. The reported failing input: H = K1 (m=1, EH = {})")
    m, EH = 1, ()
    n, k, VG, EG = reduce_3col_to_river(m, EH)
    print("    n = 3m = %d, k = m+1 = %d  =>  a trip carries at most k-1 = %d passengers"
          % (n, k, k - 1))
    print("    V(G) = %s" % sorted(VG))
    print("    E(G) = %s" % sorted(tuple(sorted(e)) for e in EG))
    col, chi = three_colorable(m, EH)
    print("    3-colorable(H) = %s   witness chi = %s" % (col, chi))
    feas, path = crossable(n, k, VG, EG)
    print("    crossable(constructed instance) = %s" % feas)
    start = (VG, frozenset(), 'L')
    succ = moves(start, k, EG)
    print("    legal moves out of the INITIAL state: %d" % len(succ))
    # Show why, by exhibiting the size lower bound directly.
    best = None
    for size in range(0, n + 1):
        found = False
        for S in itertools.combinations(sorted(VG), size):
            if is_independent(VG - frozenset(S), EG):
                found = True
                break
        if found:
            best = size
            break
    print("    minimum |S| making V(G)\\S independent = %d ; capacity allows |S| <= %d"
          % (best, k - 1))
    mismatch = (col != feas)
    print("    CLAIM 1 HOLDS ON THIS INPUT: %s" % (not mismatch))
    print()
    return mismatch


def check_sweep(mmax):
    print("### B. Exhaustive sweep over all labelled graphs H, m = 1..%d" % mmax)
    total = 0
    mismatches = []
    for m in range(1, mmax + 1):
        for EH in all_labelled_graphs(m):
            total += 1
            n, k, VG, EG = reduce_3col_to_river(m, EH)
            col, _ = three_colorable(m, EH)
            feas, _ = crossable(n, k, VG, EG)
            if col != feas:
                mismatches.append((m, EH, col, feas))
    print("    graphs examined : %d" % total)
    print("    claim violations: %d" % len(mismatches))
    for row in mismatches[:5]:
        print("      m=%d EH=%s 3col=%s crossable=%s" % row)
    if len(mismatches) > 5:
        print("      ... (%d more)" % (len(mismatches) - 5))
    # Is the instance EVER crossable?
    anyfeas = any(f for (_, _, _, f) in
                  [(m, EH, None, crossable(*reduce_3col_to_river(m, EH))[0])
                   for m in range(1, mmax + 1) for EH in all_labelled_graphs(m)])
    print("    constructed instance crossable for ANY H tested: %s" % anyfeas)
    print()
    return mismatches, total


def check_paper_forward_schedule():
    print("### C. Replay of the solution's own forward schedule (lines 0054-0063)")
    print("    Take H = K2 (m=2, EH={(0,1)}), a 3-colorable graph, chi = (1,2).")
    m, EH = 2, ((0, 1),)
    n, k, VG, EG = reduce_3col_to_river(m, EH)
    chi = (1, 2)
    assert all(chi[u] != chi[v] for (u, v) in EH)
    C = {i: frozenset("v%d(%d)" % (v, i) for v in range(m) if chi[v] == i)
         for i in (1, 2, 3)}
    print("    C1=%s C2=%s C3=%s   (|C1|+|C2|+|C3| = %d, but n = %d)"
          % (sorted(C[1]), sorted(C[2]), sorted(C[3]),
             len(C[1]) + len(C[2]) + len(C[3]), n))
    L, R, c = VG, frozenset(), 'L'
    ok_all = True
    for step, ship in ((1, C[1]), (2, frozenset()), (3, C[2]),
                       (4, frozenset()), (5, C[3])):
        if len(ship) > k - 1:
            print("    step %d: CAPACITY VIOLATED (%d > %d)" % (step, len(ship), k - 1))
            ok_all = False
            break
        if c == 'L':
            L, R, c = L - ship, R | ship, 'R'
        else:
            L, R, c = L | ship, R - ship, 'L'
        safe = is_valid_state(L, R, c, EG)
        print("    step %d: ship %d -> |L|=%d |R|=%d Charon=%s  SAFE=%s"
              % (step, len(ship), len(L), len(R), c, safe))
        if not safe:
            # name a violated edge on the unattended bank
            bank = R if c == 'L' else L
            bad = [tuple(sorted(e)) for e in EG
                   if all(x in bank for x in e)]
            print("        violating edge(s) on the unattended bank: %s" % bad[:4])
            ok_all = False
            break
    if ok_all:
        reached = (len(L) == 0 and R == VG and c == 'R')
        print("    goal reached after step 5: %s (|R|=%d of n=%d)"
              % (reached, len(R), n))
        ok_all = reached
    print("    schedule as written is a valid complete crossing: %s" % ok_all)
    print()
    return ok_all


def check_typo_hypothesis():
    print("### D. Is this a mere typo in k?  Try k' = 2m+1 instead of m+1.")
    for m in range(1, 4):
        for EH in all_labelled_graphs(m):
            n, _, VG, EG = reduce_3col_to_river(m, EH)
            col, _ = three_colorable(m, EH)
            feas, _ = crossable(n, 2 * m + 1, VG, EG)
            flag = "" if col == feas else "   <-- still mismatched"
            if m <= 2:
                print("    m=%d EH=%-12s 3col=%-5s crossable(k=2m+1)=%-5s%s"
                      % (m, str(EH), col, feas, flag))
    print("    (Even under the most favourable capacity repair, the solution's own")
    print("     schedule of lines 0054-0063 still ships only m of the 3m passengers,")
    print("     and its backward argument 'exactly one copy of each vertex is in S'")
    print("     is the exact opposite of what independence of V(G)\\S requires.)")
    print()


def main():
    print("=" * 76)
    print("INDEPENDENT ORACLE  --  record Algorithms_11__sol3")
    print("=" * 76)
    print()
    a = check_reported_failing_input()
    mism, total = check_sweep(4)
    sched_ok = check_paper_forward_schedule()
    check_typo_hypothesis()
    print("=" * 76)
    print("SUMMARY")
    print("  reported failing input (H=K1) refutes Claim 1 : %s" % a)
    print("  claim violations over %d graphs H (m<=4)      : %d" % (total, len(mism)))
    print("  solution's own schedule is a valid crossing    : %s" % sched_ok)
    print("  INDEPENDENT VERDICT: %s"
          % ("CONFIRMED (Claim 1 is false as stated)" if a and mism and not sched_ok
             else "NOT CONFIRMED"))
    print("=" * 76)
    return 0


if __name__ == "__main__":
    sys.exit(main())
