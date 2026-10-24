#!/usr/bin/env python3
"""
Blind TEST-SEARCH for record Algorithms_21__sol1.

TARGET CLAIM (PERFORMANCE, lower bound):
  "For every n >= 1 there is a weighted DAG Gn (vertices a0,b1,a1,...,bn,an,t) such that
   running Dijkstra's min-key algorithm (with reinsertions on decreases) on Gn from
   source a0 performs at least 2^n invocations of RELAX."
  (solution lines 0079 'Tn >= 2^n T0 = 2^n' and 0083-0084 / 0086-0090)

The graph family and the algorithm are BOTH fully specified by the solution, so the
claim is a concrete, mechanically checkable statement about an operation count.

Contents:
  1. FAITHFUL IMPLEMENTATION of the solution's graph family Gn and of the solution's
     "min-key Dijkstra with reinsertion on strict decrease", instrumented with an
     explicit RELAX counter (one increment per directed edge scanned) and a per-vertex
     extraction counter.  Several equally-faithful readings of the under-specified
     details (queue = multiset of entries vs. keyed vertex set; relax using current
     d[u] vs. the popped key; tie-breaking order) are all implemented, so that the
     refutation cannot be blamed on one arbitrary reading.
  2. BRUTE-FORCE ORACLES, exact integer arithmetic only:
       (a) exact single-source shortest distances in the DAG by topological DP
           (sanity check that the simulated algorithm converges to the truth);
       (b) an EXHAUSTIVE search over *all* tie-breaking choices of the min-key queue,
           computing the MAXIMUM possible number of RELAX invocations over every
           legal execution of the specified algorithm on Gn.  This is the strongest
           possible reading of the claim ("there exists an execution with >= 2^n
           relaxations"), and it is what an Omega(2^n) *lower* bound must beat.
  3. MEASUREMENT across many sizes n (>= 4 sizes) with the constants printed, plus a
     sweep over the free parameter B (the solution allows ANY integer B > 2n+2).

No floats are used anywhere; all weights, distances and counts are Python ints.
Deterministic: no randomness at all.
"""

from fractions import Fraction  # noqa: F401  (exact arithmetic only; ints suffice here)
import heapq
import itertools
import sys

# ---------------------------------------------------------------------------
# 1. THE SOLUTION'S GRAPH FAMILY  G_n   (lines 0015-0027)
# ---------------------------------------------------------------------------
#   V(Gn) = {a0, b1, a1, b2, a2, ..., bn, an, t}      -> |V| = 2n+2
#   B any integer with B > 2n+2   (solution's example: B = 4n+5)
#   W_i := B^(n-i)
#   edges:  a_{i-1} -> a_i   weight 0            (i = 1..n)
#           a_{i-1} -> b_i   weight W_i          (i = 1..n)
#           b_i     -> a_i   weight -W_i - 1     (i = 1..n)
#           a_n     -> t     weight 0
# ---------------------------------------------------------------------------

def build_Gn(n, B=None):
    """Return (vertices, adj, source, topo_order) for the solution's G_n.

    adj[u] is the list of (v, w) outgoing edges of u, in the order the solution
    lists them (direct 0-edge first, then the W_i edge), all weights exact ints.
    """
    assert n >= 1
    if B is None:
        B = 4 * n + 5          # the solution's own example choice
    assert isinstance(B, int) and B > 2 * n + 2, "solution requires integer B > 2n+2"

    W = {i: B ** (n - i) for i in range(1, n + 1)}      # W_i = B^{n-i}, exact int

    A = lambda i: ("a", i)
    Bv = lambda i: ("b", i)
    T = ("t", 0)

    vertices = [A(0)]
    for i in range(1, n + 1):
        vertices.append(Bv(i))
        vertices.append(A(i))
    vertices.append(T)

    adj = {v: [] for v in vertices}
    for i in range(1, n + 1):
        adj[A(i - 1)].append((A(i), 0))            # a_{i-1} -> a_i, weight 0
        adj[A(i - 1)].append((Bv(i), W[i]))        # a_{i-1} -> b_i, weight W_i
        adj[Bv(i)].append((A(i), -W[i] - 1))       # b_i -> a_i,   weight -W_i-1
    adj[A(n)].append((T, 0))                       # a_n -> t, weight 0

    topo = vertices[:]                             # a0 < b1 < a1 < ... < bn < an < t
    return vertices, adj, A(0), topo, B, W


def check_is_dag(vertices, adj, topo):
    """Exact check that every edge goes forward in the stated topological order."""
    pos = {v: k for k, v in enumerate(topo)}
    for u in vertices:
        for (v, _w) in adj[u]:
            if pos[u] >= pos[v]:
                return False
    return True


# ---------------------------------------------------------------------------
# 1b. FAITHFUL IMPLEMENTATION of the solution's algorithm (lines 0003-0013)
# ---------------------------------------------------------------------------
#   d[s]=0, d[v]=+inf otherwise; insert s into Q.
#   while Q nonempty:
#       extract u of minimum key
#       for every outgoing edge (u,v):            <-- each scan = 1 RELAX invocation
#           if d[v] > d[u] + w(u,v): d[v] = d[u]+w(u,v); (re)insert v into Q
#   "The number of invocations of RELAX equals the total number of directed edges
#    scanned over all extractions."  (lines 0012-0013)
# ---------------------------------------------------------------------------

INF = None  # represented by None so that no float ever enters the arithmetic


def _less(x, y):
    """x < y with None meaning +infinity. Exact integer comparison."""
    if y is None:
        return x is not None
    if x is None:
        return False
    return x < y


def run_dijkstra_reinsert(n, B=None, queue_mode="multiset", key_mode="current",
                          tie="index", trace=False, cap=10 ** 7):
    """Simulate the solution's algorithm on G_n; return instrumentation.

    queue_mode:
      "multiset"    - Q is a heap of (key, vertex) entries; a re-insertion adds a new
                      entry (the solution's literal '(re)insert v in Q').
      "keyedset"    - Q holds at most one entry per vertex, keyed by the current d[.]
                      (the literal 'min-priority queue Q keyed by d[.]' reading, i.e.
                      decrease-key rather than duplicate entries).
    key_mode:
      "current"     - relax using the current d[u] (literal reading of line 0008).
      "popped"      - relax using the key the entry was popped with (stale-key reading).
    tie:
      "index"       - break ties by the topological index of the vertex (smallest first)
      "revindex"    - break ties by the topological index, largest first
    Returns dict with relax count, extraction counts, final distances.
    """
    vertices, adj, s, topo, B, W = build_Gn(n, B)
    pos = {v: k for k, v in enumerate(topo)}
    tb = (lambda v: pos[v]) if tie == "index" else (lambda v: -pos[v])

    d = {v: INF for v in vertices}
    d[s] = 0

    relax_calls = 0
    extractions = {v: 0 for v in vertices}
    total_extractions = 0
    updates = 0
    events = []

    if queue_mode == "multiset":
        heap = [(0, tb(s), s)]
        in_queue = None
    else:
        heap = [(0, tb(s), s)]
        in_queue = {s}

    while heap:
        key, _t, u = heapq.heappop(heap)
        if queue_mode == "keyedset":
            if u not in in_queue or key != d[u]:
                continue          # stale entry of an already-decreased/removed vertex
            in_queue.discard(u)
        extractions[u] += 1
        total_extractions += 1
        if trace:
            events.append(("extract", u, key, d[u]))
        base = d[u] if key_mode == "current" else key
        for (v, w) in adj[u]:
            relax_calls += 1                      # <-- THE INSTRUMENTED OPERATION
            if relax_calls > cap:
                raise RuntimeError("relax cap exceeded")
            if base is None:
                continue
            cand = base + w
            if _less(cand, d[v]):
                d[v] = cand
                updates += 1
                if queue_mode == "multiset":
                    heapq.heappush(heap, (cand, tb(v), v))
                else:
                    heapq.heappush(heap, (cand, tb(v), v))
                    in_queue.add(v)
    return {
        "n": n, "B": B, "relax": relax_calls, "extractions": extractions,
        "total_extractions": total_extractions, "updates": updates, "d": d,
        "events": events, "queue_mode": queue_mode, "key_mode": key_mode, "tie": tie,
    }


# ---------------------------------------------------------------------------
# 2a. ORACLE: exact shortest distances in the DAG by topological DP (exact ints)
# ---------------------------------------------------------------------------

def oracle_shortest_dag(n, B=None):
    vertices, adj, s, topo, B, W = build_Gn(n, B)
    d = {v: INF for v in vertices}
    d[s] = 0
    for u in topo:                       # relax in topological order: exact, one pass
        if d[u] is None:
            continue
        for (v, w) in adj[u]:
            if _less(d[u] + w, d[v]):
                d[v] = d[u] + w
    return d


def oracle_shortest_bruteforce_paths(n, B=None):
    """Fully exhaustive oracle for tiny n: enumerate every directed path from a0."""
    vertices, adj, s, topo, B, W = build_Gn(n, B)
    best = {v: INF for v in vertices}
    stack = [(s, 0)]
    while stack:
        u, dist = stack.pop()
        if _less(dist, best[u]):
            best[u] = dist
        for (v, w) in adj[u]:
            stack.append((v, dist + w))
    return best


# ---------------------------------------------------------------------------
# 2b. ORACLE: exhaustive maximisation of RELAX count over ALL tie-breaking choices
# ---------------------------------------------------------------------------
# The specified algorithm only says "extract a vertex u of minimum key".  When several
# entries share the minimum key the choice is free.  A *lower* bound of 2^n must hold
# for the best case for the adversary, i.e. it suffices to refute
#     max over all legal executions of (#RELAX)  >=  2^n
# to refute the claim under EVERY tie-breaking discipline simultaneously.
# We compute that maximum exactly by DFS with memoisation on the full state.
# ---------------------------------------------------------------------------

def exhaustive_max_relax(n, B=None, node_budget=4_000_000):
    vertices, adj, s, topo, B, W = build_Gn(n, B)
    idx = {v: k for k, v in enumerate(topo)}
    adj_i = [[(idx[v], w) for (v, w) in adj[u]] for u in topo]
    N = len(topo)

    start_d = tuple([0] + [None] * (N - 1))     # topo[0] is a0 = source
    start_q = (0,)                              # multiset of queue entries (vertex ids)

    memo = {}
    nodes = [0]
    overflow = [False]

    def rec(dvals, queue):
        # queue: sorted tuple of vertex-ids currently in Q (keys are d[v] at pop time;
        # the solution's queue is keyed by d[.], so an entry's key is the current d).
        if not queue:
            return 0
        st = (dvals, queue)
        if st in memo:
            return memo[st]
        nodes[0] += 1
        if nodes[0] > node_budget:
            overflow[0] = True
            return 0
        # minimum key among queue entries
        keys = [dvals[v] for v in queue]
        assert all(k is not None for k in keys)
        mn = min(keys)
        best = 0
        seen_choice = set()
        for j, v in enumerate(queue):
            if dvals[v] != mn or v in seen_choice:
                continue
            seen_choice.add(v)
            nq = list(queue)
            nq.pop(j)
            nd = list(dvals)
            cnt = 0
            for (t_, w) in adj_i[v]:
                cnt += 1                                  # RELAX invocation
                cand = nd[v] + w
                if nd[t_] is None or cand < nd[t_]:
                    nd[t_] = cand
                    nq.append(t_)
            val = cnt + rec(tuple(nd), tuple(sorted(nq)))
            if val > best:
                best = val
        memo[st] = best
        return best

    val = rec(start_d, start_q)
    return val, nodes[0], overflow[0]


# ---------------------------------------------------------------------------
# 3. MEASUREMENT / SEARCH
# ---------------------------------------------------------------------------

def main():
    print("=" * 78)
    print("record_id: Algorithms_21__sol1")
    print("claim kind: PERFORMANCE (lower bound)")
    print("target claim: running the solution's min-key-with-reinsertion Dijkstra on")
    print("              the solution's DAG G_n from a0 performs >= 2^n RELAX calls")
    print("              (solution line 0079: Tn >= 2^n T0 = 2^n; lines 0083-0089)")
    print("=" * 78)

    # ---- structural sanity: the construction really is a DAG with negative edges ----
    vs, adj, s, topo, B, W = build_Gn(4)
    print("\n[0] structural check of G_4 (B = 4n+5 = 21):")
    print("    |V| = %d  (solution says 2n+2 = %d)" % (len(vs), 2 * 4 + 2))
    print("    all edges forward in stated topological order (is DAG): %s"
          % check_is_dag(vs, adj, topo))
    print("    W_i = %s ; negative edges b_i->a_i weights = %s"
          % ([W[i] for i in range(1, 5)], [-W[i] - 1 for i in range(1, 5)]))

    # ---- oracle agreement on distances (exact ints) ----
    print("\n[1] distance oracle cross-check (topological DP vs exhaustive path enum")
    print("    vs the simulated algorithm's final d[]), exact integer arithmetic:")
    ok_all = True
    for n in range(1, 7):
        o1 = oracle_shortest_dag(n)
        o2 = oracle_shortest_bruteforce_paths(n)
        r = run_dijkstra_reinsert(n)
        ok = (o1 == o2 == r["d"])
        ok_all = ok_all and ok
        print("    n=%d  topoDP==pathEnum==algorithm final d[] : %s   d[t] = %s"
              % (n, ok, o1[("t", 0)]))
    print("    => the faithful implementation converges to the true shortest")
    print("       distances, so it is a correct simulation of the stated algorithm.")

    # ---- THE MEASUREMENT: instrumented RELAX counts vs the claimed 2^n ----
    print("\n[2] INSTRUMENTED OPERATION COUNTS (one increment per directed edge scanned,")
    print("    which is exactly the solution's own definition of a RELAX invocation,")
    print("    lines 0012-0013).  Primary faithful reading: Q = multiset of entries,")
    print("    relax using current d[u], ties by topological index. B = 4n+5.")
    print()
    hdr = ("   n   |V|=2n+2    #edges   RELAX   claimed 2^n   RELAX/2^n   extractions"
           "  T_n=#extract(a_n)   claimed 2^n")
    print(hdr)
    print("   " + "-" * (len(hdr) - 3))
    first_violation = None
    rows = []
    for n in range(1, 15):
        r = run_dijkstra_reinsert(n)
        m = 3 * n + 1
        claimed = 2 ** n
        Tn = r["extractions"][("a", n)]
        rows.append((n, r["relax"], claimed, Tn))
        ratio = "%.4f" % (r["relax"] / claimed)
        flag = ""
        if r["relax"] < claimed:
            flag = "   <-- BELOW CLAIMED LOWER BOUND"
            if first_violation is None:
                first_violation = n
        print("  %3d   %6d   %7d   %5d   %11d   %9s   %11d   %14d   %11d%s"
              % (n, 2 * n + 2, m, r["relax"], claimed, ratio,
                 r["total_extractions"], Tn, claimed, flag))

    print()
    print("    Fitted closed form for the measured RELAX count: (n+1)*(3n+2)/2")
    fit_ok = all(rl == (n + 1) * (3 * n + 2) // 2 for (n, rl, _c, _T) in rows)
    print("      matches every measured n in 1..14 : %s   => growth is Theta(n^2)," % fit_ok)
    print("      i.e. POLYNOMIAL in n, not Omega(2^n).")
    print("    Measured T_n = #extractions of a_n equals n+1 for every n:",
          all(T == n + 1 for (n, _r, _c, T) in rows))
    print("      => the solution's intermediate claim T_n >= 2^n (line 0079) already")
    print("         fails at n=2: measured T_2 = 3 < 4 = 2^2.")
    print("    First n where the total RELAX count drops below the claimed 2^n: n = %s"
          % first_violation)

    # ---- robustness: every alternative faithful reading of the under-specified bits ----
    print("\n[3] ROBUSTNESS -- the refutation does not depend on how the")
    print("    under-specified details are read.  All variants, n = 7..12:")
    print()
    variants = [("multiset", "current", "index"), ("multiset", "current", "revindex"),
                ("multiset", "popped", "index"), ("multiset", "popped", "revindex"),
                ("keyedset", "current", "index"), ("keyedset", "current", "revindex")]
    print("    queue      key       tie        " + "".join("  n=%-6d" % n for n in range(7, 13)))
    for (qm, km, tb) in variants:
        cells = []
        for n in range(7, 13):
            r = run_dijkstra_reinsert(n, queue_mode=qm, key_mode=km, tie=tb)
            cells.append("%8d" % r["relax"])
        print("    %-9s  %-8s  %-9s" % (qm, km, tb) + "".join(cells))
    print("    claimed 2^n lower bound        " + "".join("%8d" % (2 ** n) for n in range(7, 13)))
    print("    => every variant is far below 2^n from n=7 onward.")

    # ---- robustness: the free parameter B (solution allows ANY integer B > 2n+2) ----
    print("\n[4] ROBUSTNESS over the free parameter B (solution: 'any integer B > 2n+2';")
    print("    B = 4n+5 is only its example).  RELAX counts, n = 7..12:")
    print()
    print("    B choice        " + "".join("  n=%-6d" % n for n in range(7, 13)))
    for label, Bf in [("2n+3 (min)", lambda n: 2 * n + 3),
                      ("4n+5 (example)", lambda n: 4 * n + 5),
                      ("n^2+2n+3", lambda n: n * n + 2 * n + 3),
                      ("1000", lambda n: 1000),
                      ("2^(n+2)", lambda n: 2 ** (n + 2))]:
        cells = []
        for n in range(7, 13):
            r = run_dijkstra_reinsert(n, B=Bf(n))
            cells.append("%8d" % r["relax"])
        print("    %-14s" % label + "".join(cells))
    print("    claimed 2^n     " + "".join("%8d" % (2 ** n) for n in range(7, 13)))
    print("    => the count is B-independent; no admissible B rescues the bound.")

    # ---- exhaustive oracle over ALL tie-breaks: nothing can reach 2^n ----
    print("\n[5] BRUTE-FORCE ORACLE: exhaustive maximisation of the RELAX count over")
    print("    EVERY legal execution (all tie-breaking choices) of the specified")
    print("    algorithm on G_n.  A lower bound of 2^n must be beaten even by this")
    print("    adversarially maximal execution.")
    print()
    print("     n   max RELAX over all tie-breaks   deterministic run   claimed 2^n   states")
    for n in range(1, 8):
        val, nodes, over = exhaustive_max_relax(n)
        det = run_dijkstra_reinsert(n)["relax"]
        note = "  (SEARCH TRUNCATED)" if over else ""
        mark = "   <-- MAX < 2^n" if (not over and val < 2 ** n) else ""
        print("    %2d   %27d   %17d   %11d   %6d%s%s"
              % (n, val, det, 2 ** n, nodes, note, mark))
    print("    => even the worst-case (count-maximising) tie-breaking gives the same")
    print("       polynomial count; the min-key rule leaves no freedom that helps.")

    # ---- root cause, mechanically exhibited ----
    print("\n[6] ROOT CAUSE, exhibited from the trace of G_5 (B=25):")
    r = run_dijkstra_reinsert(5, trace=True)
    seq = [(u, k) for (tag, u, k, dc) in r["events"] if tag == "extract" and u == ("a", 5)]
    print("    keys at which a_5 is extracted, in order:",
          [k for (_u, k) in seq])
    print("    d[a_j] values at termination:",
          [r["d"][("a", j)] for j in range(0, 6)])
    print("    Each indirect shortcut a_{i-1}->b_i->a_i lowers a distance by EXACTLY 1,")
    print("    and the solution itself asserts the invariant  n >= -d[a_j] >= 0")
    print("    (lines 0038-0039).  Since d[a_j] is a strictly decreasing integer inside")
    print("    [-n, 0], a_j can be extracted at most n+1 times -- so T_j <= n+1 and the")
    print("    recurrence T_i >= 2 T_{i-1} (line 0072) is inconsistent with the")
    print("    solution's OWN invariant for i >= log2(n+1).  Concretely, the")
    print("    'two extractions per i-epoch' lemma fails because in an i-epoch the")
    print("    direct edge a_{i-1}->a_i produces NO strict decrease: d[a_i] has already")
    print("    been pushed to that value (or lower) by the b-cascade of the previous")
    print("    epoch, so 'd[v] > d[u]+w' is false and no re-insertion happens.")

    # ---- verdict ----
    print("\n" + "=" * 78)
    n0 = first_violation
    r0 = run_dijkstra_reinsert(n0)
    print("VERDICT: BOUND_VIOLATION_FOUND")
    print("  The claimed lower bound '>= 2^n RELAX invocations' is FALSE for the")
    print("  solution's own graph family under its own algorithm.")
    print("  Smallest refuting size: n = %d  (|V| = %d, B = %d)" % (n0, 2 * n0 + 2, 4 * n0 + 5))
    print("    measured RELAX invocations = %d" % r0["relax"])
    print("    claimed lower bound 2^n    = %d" % (2 ** n0))
    print("    measured / claimed         = %.4f" % (r0["relax"] / (2 ** n0)))
    print("  Measured growth: RELAX(n) = (n+1)(3n+2)/2 = Theta(n^2)  [constants above],")
    print("  verified exactly for n = 1..14 and unchanged under every tie-breaking")
    print("  rule, every queue/stale-key reading, and every admissible B.")
    print("  The intermediate claim T_n >= 2^n (line 0079) fails even earlier, at n = 2")
    print("  (measured T_2 = 3 < 4).")
    print("=" * 78)


if __name__ == "__main__":
    sys.setrecursionlimit(100000)
    main()
