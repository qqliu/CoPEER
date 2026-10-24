#!/usr/bin/env python3
"""
Blind TEST-SEARCH for record Algorithms_11__sol5.

TARGET CLAIM (from the solution, lines 0015-0044):
    The reduction from Graph Coloring: given (G, c), build the river-crossing
    instance with the SAME conflict graph G, n = |V(G)| passengers, and ferry
    capacity k = c + 1 (Charon + c passengers).  The solution claims an iff:

        G is c-colorable   <=>   a valid crossing sequence exists.

    Part 1 (lines 0030-0037): ferry color class C1 across, Charon returns alone,
    repeat for C2..Cc.  Claimed invariant: "After each crossing, the remaining
    passengers are in independent sets".
    Part 2 (lines 0038-0042): a valid crossing sequence partitions the
    passengers into <= c independent sets, hence a c-coloring.

WHAT THIS FILE CONTAINS
    1. FAITHFUL implementation of the solution's algorithm:
         - the reduction map  f(G, c) -> (n, k = c+1, G)
         - the solution's explicit Part-1 crossing schedule (its "algorithm"),
           simulated move by move
         - the solution's Part-2 extraction (groups ferried -> color classes)
    2. BRUTE-FORCE ORACLE for the river-crossing decision problem:
         BFS over states (frozenset of passengers still on the left bank,
         side of Charon).  A move: Charon crosses with any subset S of the
         passengers currently on his bank, |S| <= k-1.  A state is legal iff
         the bank WITHOUT Charon induces an independent set of G.
         Accept iff (left bank empty, Charon on right) is reachable.
       plus a BRUTE-FORCE exact c-colorability checker (all c^n assignments).
       All arithmetic is exact integer / set logic; no floats anywhere.
    3. Exhaustive search over ALL labeled graphs on n <= 6 vertices and all
       c in 1..n, comparing  feasible(G, k=c+1)  against  c_colorable(G, c),
       plus the two adversarial constructions named in the triage sketches.
    4. Deterministic __main__ printing the verdict.  No randomness, no timing.
"""

from itertools import combinations, product
from collections import deque
import sys

# ----------------------------------------------------------------------------
# Graph representation: (n, frozenset of frozenset({u,v}) edges)
# ----------------------------------------------------------------------------

def make_graph(n, edge_list):
    return (n, frozenset(frozenset(e) for e in edge_list))


def edges_of(G):
    return [tuple(sorted(e)) for e in sorted(G[1], key=lambda e: tuple(sorted(e)))]


def graph_name(G, label=None):
    return "%s(n=%d, E=%s)" % (label + " " if label else "", G[0], edges_of(G))


def all_graphs(n):
    """All labeled simple graphs on vertex set {0..n-1} (exhaustive)."""
    pairs = list(combinations(range(n), 2))
    for mask in range(1 << len(pairs)):
        yield make_graph(n, [pairs[i] for i in range(len(pairs)) if (mask >> i) & 1])


def is_independent(G, vertices):
    """True iff `vertices` induces an edge-free subgraph of G."""
    vs = set(vertices)
    for e in G[1]:
        u, v = tuple(e)
        if u in vs and v in vs:
            return False
    return True


# ----------------------------------------------------------------------------
# (1) FAITHFUL IMPLEMENTATION OF THE SOLUTION
# ----------------------------------------------------------------------------

def solution_reduction(G, c):
    """The solution's construction, lines 0015-0022:
         passengers  = vertices of G          (n of them)
         conflict graph = G, unchanged
         ferry capacity k = c + 1  (Charon + up to c passengers)
       Returns the river-crossing instance (n, k, G).  Polynomial (identity)."""
    n = G[0]
    k = c + 1
    return (n, k, G)


def solution_part1_schedule(G, coloring, c):
    """The solution's Part-1 crossing strategy, lines 0031-0034, executed
    literally:
        1. Charon takes ALL passengers of C1 to the other side
        2. Charon returns alone
        3. repeat for C2, ..., Cc
        4. finally Charon crosses himself
    `coloring` maps vertex -> color in 0..c-1.
    Returns (moves, ok, violation) where `moves` is the list of
    (crossing_set, direction) actually attempted, `ok` says whether every
    intermediate configuration satisfied capacity + safety, and `violation`
    describes the first failure.  This is the solution's own algorithm,
    faithfully including its bugs -- nothing is repaired."""
    n, k, _ = solution_reduction(G, c)
    classes = [sorted(v for v in range(n) if coloring[v] == col) for col in range(c)]

    left = set(range(n))          # passengers still on the start bank
    right = set()
    charon = 'L'
    moves = []

    def check(where):
        """Safety: the bank WITHOUT Charon must induce an independent set."""
        unattended = right if charon == 'L' else left
        if not is_independent(G, unattended):
            bad = [tuple(sorted(e)) for e in G[1]
                   if set(e) <= set(unattended)]
            return ("unsafe unattended bank %s after %s: enemy pair(s) %s"
                    % (sorted(unattended), where, bad))
        return None

    for idx, Ci in enumerate(classes):
        # step: Charon takes all of Ci across (capacity: |Ci| + 1 <= k ?)
        if len(Ci) + 1 > k:
            return moves, False, ("capacity violated ferrying C%d: |C%d|=%d, k=%d"
                                  % (idx + 1, idx + 1, len(Ci), k))
        left -= set(Ci)
        right |= set(Ci)
        charon = 'R'
        moves.append((tuple(Ci), 'L->R'))
        v = check("ferrying C%d across" % (idx + 1))
        if v:
            return moves, False, v
        if idx == len(classes) - 1:
            break                      # last class: Charon stays (step 4)
        # step: Charon returns alone
        charon = 'L'
        moves.append(((), 'R->L'))
        v = check("Charon returning alone after C%d" % (idx + 1))
        if v:
            return moves, False, v

    if left or charon != 'R':
        return moves, False, "schedule ended with left=%s charon=%s" % (sorted(left), charon)
    return moves, True, None


def solution_part2_extraction(move_groups, c):
    """The solution's Part-2 claim, lines 0038-0042: the groups ferried across
    partition the passengers into <= c independent sets, giving a c-coloring.
    Faithful reading: color a passenger by the index of the L->R crossing that
    carried them.  Returns (coloring_or_None, num_classes_used)."""
    coloring = {}
    idx = 0
    for grp, direction in move_groups:
        if direction != 'L->R':
            continue
        for p in grp:
            coloring[p] = idx      # last L->R trip wins (passenger may re-cross)
        if grp:
            idx += 1
    return coloring, idx


# ----------------------------------------------------------------------------
# (2) BRUTE-FORCE ORACLES  (exact; sets and ints only)
# ----------------------------------------------------------------------------

def oracle_crossing_feasible(n, k, G, want_witness=False):
    """Exhaustive BFS over the full state space of the river-crossing problem.
    State = (frozenset of passengers on LEFT bank, Charon's side).
    Legal state: the bank without Charon induces an independent set of G.
    Move: Charon crosses carrying any subset S of the passengers on his bank
          with |S| <= k-1 (k counts Charon).
    Returns True iff the goal (nobody left, Charon right) is reachable.
    With want_witness=True also returns the shortest witnessing move list."""
    start = (frozenset(range(n)), 'L')
    goal = (frozenset(), 'R')

    def legal(state):
        left, side = state
        right = frozenset(range(n)) - left
        unattended = right if side == 'L' else left
        return is_independent(G, unattended)

    if not legal(start):
        return (False, None) if want_witness else False
    if start == goal:
        return (True, []) if want_witness else True

    prev = {start: None}
    q = deque([start])
    while q:
        state = q.popleft()
        left, side = state
        here = left if side == 'L' else (frozenset(range(n)) - left)
        cap = k - 1
        here_list = sorted(here)
        for r in range(0, min(cap, len(here_list)) + 1):
            for S in combinations(here_list, r):
                Sset = frozenset(S)
                if side == 'L':
                    nstate = (left - Sset, 'R')
                    direction = 'L->R'
                else:
                    nstate = (left | Sset, 'L')
                    direction = 'R->L'
                if nstate in prev or not legal(nstate):
                    continue
                prev[nstate] = (state, tuple(sorted(S)), direction)
                if nstate == goal:
                    if not want_witness:
                        return True
                    path = []
                    cur = nstate
                    while prev[cur] is not None:
                        par, grp, d = prev[cur]
                        path.append((grp, d))
                        cur = par
                    return True, list(reversed(path))
                q.append(nstate)
    return (False, None) if want_witness else False


def oracle_c_colorable(G, c, want_witness=False):
    """Exact brute force over all c^n colorings."""
    n = G[0]
    if c <= 0:
        ok = (n == 0)
        return (ok, {} if ok else None) if want_witness else ok
    for assign in product(range(c), repeat=n):
        good = True
        for e in G[1]:
            u, v = tuple(e)
            if assign[u] == assign[v]:
                good = False
                break
        if good:
            col = {v: assign[v] for v in range(n)}
            return (True, col) if want_witness else True
    return (False, None) if want_witness else False


def chromatic_number(G):
    for c in range(0, G[0] + 1):
        if oracle_c_colorable(G, c):
            return c
    return G[0]


# ----------------------------------------------------------------------------
# (3) SEARCH
# ----------------------------------------------------------------------------

def check_instance(G, c):
    """Compare the reduction's promise against the oracles.
    Returns None if the iff holds on this instance, else a dict describing
    which direction failed."""
    n, k, Gp = solution_reduction(G, c)
    colorable = oracle_c_colorable(G, c)
    feasible = oracle_crossing_feasible(n, k, Gp)
    if colorable == feasible:
        return None
    return {
        'graph': G, 'c': c, 'k': k, 'n': n,
        'c_colorable': colorable, 'crossing_feasible': feasible,
        'direction': ('c-colorable => valid crossing sequence'
                      if colorable and not feasible else
                      'valid crossing sequence => c-colorable'),
    }


def describe(cx, label):
    G, c, k, n = cx['graph'], cx['c'], cx['k'], cx['n']
    lines = []
    lines.append("  %s" % label)
    lines.append("    input : %s, c = %d   -->  reduction gives (n=%d, k=c+1=%d, G unchanged)"
                 % (graph_name(G), c, n, k))
    lines.append("    oracle: G is %d-colorable        = %s" % (c, cx['c_colorable']))
    lines.append("    oracle: valid crossing exists    = %s" % cx['crossing_feasible'])
    lines.append("    BROKEN DIRECTION: %s" % cx['direction'])
    if cx['crossing_feasible']:
        _, wit = oracle_crossing_feasible(n, k, G, want_witness=True)
        lines.append("    witnessing crossing sequence (%d moves):" % len(wit))
        for i, (grp, d) in enumerate(wit, 1):
            lines.append("      %2d. Charon %s carrying %s" % (i, d, list(grp) if grp else "nobody"))
        col, used = solution_part2_extraction(wit, c)
        lines.append("    solution's Part-2 extraction from this sequence uses %d L->R groups"
                     % used)
        proper = all(col[u] != col[v] for e in G[1] for u, v in [tuple(e)])
        lines.append("    ... extracted map is a proper coloring? %s ; uses <= c = %d colors? %s"
                     % (proper, c, used <= c))
    else:
        okc, coloring = oracle_c_colorable(G, c, want_witness=True)
        lines.append("    a genuine %d-coloring exists, e.g. %s" % (c, coloring))
        moves, ok, viol = solution_part1_schedule(G, coloring, c)
        lines.append("    running the solution's OWN Part-1 schedule on it:")
        for i, (grp, d) in enumerate(moves, 1):
            lines.append("      %2d. Charon %s carrying %s" % (i, d, list(grp) if grp else "nobody"))
        lines.append("      => schedule valid? %s ; first violation: %s" % (ok, viol))
    return "\n".join(lines)


def main():
    print("=" * 78)
    print("TEST-SEARCH  record_id = Algorithms_11__sol5")
    print("Target claim: reduction (G unchanged, k = c+1) makes")
    print("              'G is c-colorable'  <=>  'a valid crossing sequence exists'")
    print("Claim kind  : CORRECTNESS")
    print("=" * 78)

    # -- sanity: oracle reproduces the classic wolf/goat/cabbage answer -------
    P3 = make_graph(3, [(0, 1), (1, 2)])          # 0=wolf 1=goat 2=cabbage
    assert oracle_crossing_feasible(3, 2, P3) is True, "oracle sanity failed (P3,k=2)"
    K3 = make_graph(3, [(0, 1), (1, 2), (0, 2)])
    assert oracle_crossing_feasible(3, 2, K3) is False, "oracle sanity failed (K3,k=2)"
    assert oracle_c_colorable(P3, 2) and not oracle_c_colorable(P3, 1)
    assert chromatic_number(K3) == 3
    print("[sanity] oracles agree with the classic wolf-goat-cabbage instance: OK")
    print()

    # -- adversarial constructions named in the triage sketches --------------
    print("--- adversarial constructions from the triage sketches ---")
    adversarial = [
        ("p0 sketch: P3 (wolf-goat-cabbage), c = chi-1 = 1, k = 2", P3, 1),
        ("p1 sketch: 2K3 (two disjoint triangles), c = 3, k = 4",
         make_graph(6, [(0, 1), (1, 2), (0, 2), (3, 4), (4, 5), (3, 5)]), 3),
    ]
    adv_hits = []
    for label, G, c in adversarial:
        cx = check_instance(G, c)
        if cx is None:
            print("  %s -> iff HOLDS here" % label)
        else:
            adv_hits.append((label, cx))
            print(describe(cx, label))
            print()

    # -- exhaustive search over all labeled graphs on n <= 6 -----------------
    print("--- exhaustive search: ALL labeled graphs on n = 1..6, all c in 1..n ---")
    first_fail = {}          # direction -> (n, cx)
    counts = {}
    total_checked = 0
    for n in range(1, 7):
        nfail = 0
        for G in all_graphs(n):
            for c in range(1, n + 1):
                total_checked += 1
                cx = check_instance(G, c)
                if cx is not None:
                    nfail += 1
                    d = cx['direction']
                    counts[d] = counts.get(d, 0) + 1
                    if d not in first_fail:
                        first_fail[d] = (n, cx)
        print("  n = %d : %d instance(s) where the claimed iff FAILS" % (n, nfail))
    print("  total (graph, c) instances checked: %d" % total_checked)
    print()

    print("--- smallest counterexample found for each broken direction ---")
    for d in sorted(first_fail, key=lambda d: first_fail[d][0]):
        n, cx = first_fail[d]
        print(describe(cx, "first failure of '%s' (n=%d, %d total such failures)"
                       % (d, n, counts[d])))
        print()

    print("=" * 78)
    if first_fail or adv_hits:
        print("VERDICT: BUG_FOUND")
        print("The claimed equivalence is false in BOTH directions." if len(first_fail) == 2
              else "The claimed equivalence is false.")
        ks = sorted(first_fail, key=lambda d: first_fail[d][0])
        if ks:
            n0, cx0 = first_fail[ks[0]]
            print("Smallest overall failing input: %s with c = %d (k = %d); "
                  "%d-colorable=%s, crossing-feasible=%s"
                  % (graph_name(cx0['graph']), cx0['c'], cx0['k'], cx0['c'],
                     cx0['c_colorable'], cx0['crossing_feasible']))
    else:
        print("VERDICT: NO_BUG_FOUND")
    print("=" * 78)
    return 0


if __name__ == '__main__':
    sys.exit(main())
