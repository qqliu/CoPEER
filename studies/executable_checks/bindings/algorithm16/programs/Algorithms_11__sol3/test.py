#!/usr/bin/env python3
"""
Blind TEST-SEARCH for record Algorithms_11__sol3.

TARGET CLAIM (solution lines 0043-0044):
    "Claim 1. H is 3-colorable if and only if there exists a valid crossing
     sequence for the constructed instance."

The construction (lines 0029-0035) is:
    n  = 3m               (three copies v(1),v(2),v(3) of each vertex v of H)
    EG = {(u(i),v(j)) : (u,v) in EH, i = j}  U  {(v(i),v(j)) : v in VH, i != j}
    k  = m + 1

The river-crossing semantics are the solution's own (lines 0015-0026):
    state (L,R,c); valid iff the bank WITHOUT Charon induces an independent set;
    a move ships S subset of Charon's bank with |S| <= k-1 and flips c.
    initial (V,{},left), goal ({},V,right).

This file contains
  (1) a verbatim implementation of the solution's reduction + its stated
      transition system (the "implementation"),
  (2) a brute-force oracle: exhaustive BFS over the 2^n * 2 state space for
      river-crossing feasibility, and exhaustive 3^m search for 3-colorability,
  (3) an exhaustive search over ALL graphs H on m = 1..4 vertices (n = 3m <= 12)
      for an input where the claimed iff fails,
  (4) an extra check of the solution's own forward-direction schedule
      (lines 0054-0063).

All arithmetic is exact integer / set arithmetic. No floats, no randomness,
no wall-clock timing.
"""

from itertools import combinations, product
from collections import deque


# ----------------------------------------------------------------------------
# (1) FAITHFUL IMPLEMENTATION OF THE SOLUTION'S REDUCTION AND STATE MACHINE
# ----------------------------------------------------------------------------

def build_instance(m, EH):
    """Solution lines 0029-0035, verbatim.

    Vertices of G are pairs (v, i) with v in {0..m-1}, i in {1,2,3}.
    Returns (n, k, vertices, edges) with edges a set of frozensets.
    """
    verts = [(v, i) for v in range(m) for i in (1, 2, 3)]
    idx = {x: t for t, x in enumerate(verts)}
    EG = set()
    # {(u(i), v(j)) : (u,v) in EH, i = j}
    for (u, v) in EH:
        for i in (1, 2, 3):
            EG.add(frozenset((idx[(u, i)], idx[(v, i)])))
    # {(v(i), v(j)) : v in VH, i != j}
    for v in range(m):
        for i, j in combinations((1, 2, 3), 2):
            EG.add(frozenset((idx[(v, i)], idx[(v, j)])))
    n = 3 * m                      # line 0030
    k = m + 1                      # line 0035
    return n, k, verts, idx, EG


def independent(mask, n, adj):
    """Is the vertex set encoded by bitmask `mask` independent in G?"""
    mm = mask
    while mm:
        low = mm & -mm
        v = low.bit_length() - 1
        if adj[v] & mask:
            return False
        mm ^= low
    return True


def adjacency(n, EG):
    adj = [0] * n
    for e in EG:
        a, b = tuple(e)
        adj[a] |= 1 << b
        adj[b] |= 1 << a
    return adj


def state_valid(Lmask, Rmask, c, n, adj):
    """Solution lines 0020-0023: the bank Charon is NOT on must be independent."""
    if c == 'left':
        return independent(Rmask, n, adj)
    else:
        return independent(Lmask, n, adj)


def successors(Lmask, Rmask, c, n, k, adj):
    """Solution lines 0024-0026: ship any S subset of Charon's bank, |S| <= k-1."""
    src = Lmask if c == 'left' else Rmask
    elems = [i for i in range(n) if src >> i & 1]
    out = []
    for size in range(0, k):            # |S| <= k-1
        for S in combinations(elems, size):
            smask = 0
            for i in S:
                smask |= 1 << i
            if c == 'left':
                nL, nR, nc = Lmask & ~smask, Rmask | smask, 'right'
            else:
                nL, nR, nc = Lmask | smask, Rmask & ~smask, 'left'
            if state_valid(nL, nR, nc, n, adj):
                out.append((nL, nR, nc))
    return out


# ----------------------------------------------------------------------------
# (2) BRUTE-FORCE ORACLES
# ----------------------------------------------------------------------------

def crossing_feasible(n, k, EG):
    """Exhaustive BFS over all (L, R, c) states.  Exact, no heuristics."""
    adj = adjacency(n, EG)
    full = (1 << n) - 1
    start = (full, 0, 'left')                 # line 0018
    goal = (0, full, 'right')                 # line 0019
    if not state_valid(*start, n, adj):
        return False, None
    if start == goal:
        return True, []
    seen = {start}
    q = deque([(start, [])])
    while q:
        (L, R, c), path = q.popleft()
        for nxt in successors(L, R, c, n, k, adj):
            if nxt in seen:
                continue
            npath = path + [nxt]
            if nxt == goal:
                return True, npath
            seen.add(nxt)
            q.append((nxt, npath))
    return False, None


def three_colorable(m, EH):
    """Exhaustive 3^m search."""
    for chi in product((1, 2, 3), repeat=m):
        if all(chi[u] != chi[v] for (u, v) in EH):
            return True, chi
    return False, None


# ----------------------------------------------------------------------------
# (3) SEARCH
# ----------------------------------------------------------------------------

def all_graphs(m):
    """All labelled undirected simple graphs on m vertices."""
    pairs = list(combinations(range(m), 2))
    for bits in range(1 << len(pairs)):
        yield [pairs[t] for t in range(len(pairs)) if bits >> t & 1]


def check_paper_schedule(m, EH, chi, verts, idx, EG, n, k):
    """Replay the solution's own forward schedule, lines 0054-0063.

    Step 1: ship C1.  Step 2: return alone.  Step 3: ship C2.  Step 4: return
    alone.  Step 5: ship C3.  Report the first stated invariant that fails and
    whether the goal is reached.
    """
    adj = adjacency(n, EG)
    C = {i: 0 for i in (1, 2, 3)}
    for v in range(m):
        C[chi[v]] |= 1 << idx[(v, chi[v])]
    L, R, c = (1 << n) - 1, 0, 'left'
    log = []
    for step, ship in ((1, C[1]), (2, 0), (3, C[2]), (4, 0), (5, C[3])):
        cnt = bin(ship).count('1')
        if cnt > k - 1:
            log.append("step %d: capacity violated (%d > k-1=%d)" % (step, cnt, k - 1))
            return log, False
        if c == 'left':
            L, R, c = L & ~ship, R | ship, 'right'
        else:
            L, R, c = L | ship, R & ~ship, 'left'
        ok = state_valid(L, R, c, n, adj)
        log.append("step %d: ship %d passenger(s); |L|=%d |R|=%d Charon=%s; safe=%s"
                   % (step, cnt, bin(L).count('1'), bin(R).count('1'), c, ok))
        if not ok:
            return log, False
    reached = (L == 0 and R == (1 << n) - 1 and c == 'right')
    log.append("after step 5: goal reached = %s (|R|=%d of n=%d)"
               % (reached, bin(R).count('1'), n))
    return log, reached


def main():
    print("=" * 78)
    print("record_id: Algorithms_11__sol3")
    print("claim_kind: CORRECTNESS")
    print("target claim (lines 0043-0044): H is 3-colorable  <=>  the constructed")
    print("  river-crossing instance (n=3m, k=m+1) admits a valid crossing sequence.")
    print("=" * 78)
    print()

    counterexamples = []
    total = 0
    print("Exhaustive search over ALL labelled graphs H with m = 1..4 (n = 3m <= 12):")
    print()
    header = "%-3s %-28s %-8s %-10s %-8s" % ("m", "EH", "3-col?", "crossable?", "agree?")
    print(header)
    print("-" * len(header))
    for m in range(1, 5):
        for EH in all_graphs(m):
            total += 1
            n, k, verts, idx, EG = build_instance(m, EH)
            col, chi = three_colorable(m, EH)
            feas, _ = crossing_feasible(n, k, EG)
            agree = (col == feas)
            if not agree:
                counterexamples.append((m, EH, col, feas, chi, verts, idx, EG, n, k))
            # print only the smallest few rows in full, then summarize
            if m <= 2:
                print("%-3d %-28s %-8s %-10s %-8s"
                      % (m, str(EH), col, feas, "YES" if agree else "*** NO ***"))
    print("...")
    print("(m=3 and m=4 rows suppressed; totals below.)")
    print()
    print("graphs H examined: %d" % total)
    print("mismatches (claim violated): %d" % len(counterexamples))
    print()

    if not counterexamples:
        print("VERDICT: NO_BUG_FOUND")
        return

    # Report the smallest counterexample in full detail.
    m, EH, col, feas, chi, verts, idx, EG, n, k = counterexamples[0]
    print("=" * 78)
    print("SMALLEST COUNTEREXAMPLE")
    print("=" * 78)
    print("H: m = %d vertices, EH = %s   (H = K%d)" % (m, EH, m))
    print("oracle: H is 3-colorable = %s  (witness colouring chi = %s)" % (col, chi))
    print()
    print("constructed instance (solution lines 0029-0035):")
    print("  n = 3m = %d,  k = m+1 = %d,  so a boat trip carries at most k-1 = %d passengers"
          % (n, k, k - 1))
    print("  V(G) = %s" % ([("v%d(%d)" % (v, i)) for (v, i) in verts],))
    names = {t: "v%d(%d)" % verts[t] for t in range(n)}
    print("  E(G) = %s" % (sorted(tuple(sorted(names[x] for x in e)) for e in EG),))
    print()
    print("oracle: exhaustive BFS over all %d states says crossable = %s"
          % (2 * (1 << n), feas))
    print()
    print("why (mechanically checked below): every vertex v of H contributes the")
    print("triangle v(1)-v(2)-v(3) to G, so the unattended left bank may keep at")
    print("most ONE copy of each vertex; a legal first trip therefore needs")
    print("|S| >= 2m, but capacity allows only |S| <= k-1 = m.")
    adj = adjacency(n, EG)
    full = (1 << n) - 1
    legal_first = successors(full, 0, 'left', n, k, adj)
    print("  number of legal first moves from the initial state: %d" % len(legal_first))
    print("  required copies to remove per vertex = 2, times m = %d  ->  |S| >= %d > %d = k-1"
          % (m, 2 * m, k - 1))
    print()
    print("the solution's own forward schedule (lines 0054-0063), replayed:")
    log, reached = check_paper_schedule(m, EH, chi, verts, idx, EG, n, k)
    for line in log:
        print("   " + line)
    print()
    print("OBSERVED vs CLAIMED:")
    print("  claimed: 3-colorable H  =>  a valid crossing sequence exists")
    print("  observed: H = K%d is 3-colorable, but exhaustive BFS proves the goal" % m)
    print("            state is UNREACHABLE -- indeed no first move is even legal.")
    print()
    print("all counterexamples found (m, EH, 3-colorable, crossable):")
    for (mm, e, c_, f_, *_rest) in counterexamples[:12]:
        print("   m=%d EH=%s  3col=%s  crossable=%s" % (mm, e, c_, f_))
    print("   ... %d total; note EVERY 3-colorable H (i.e. every H with m<=4," % len(counterexamples))
    print("       since all such graphs here are 3-colorable except K4) fails.")
    print()
    print("VERDICT: BUG_FOUND")


if __name__ == "__main__":
    main()
