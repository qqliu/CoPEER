#!/usr/bin/env python3
"""
Blind test-search for record Algorithms_21__sol5.

TARGET CLAIM (PERFORMANCE, a LOWER bound):
    "Let R(n) be the number of relaxations required for Gn. We prove by induction
     that R(n) >= 2^n - 1."  ... "Therefore, processing Gn requires at least
     2^n - 1 relaxations, proving that Dijkstra's algorithm performs Omega(2^n)
     relaxation steps ... even for DAGs with negative edge weights."

The solution's EXPLICIT family (lines 0005-0008):
    V_n = {v_0, ..., v_{n-1}}
    E_n = {(v_i, v_j) : 0 <= i < j <= n-1}
    w(v_i, v_j) = -2^i   for all i < j
    source = v_0 (line 0013: d[v0] = 0, d[vi] = inf otherwise)

Everything below is exact integer arithmetic. No floats decide anything.
No wall clock is used anywhere: the "measurement" is an explicit counter
incremented at every invocation of Relax.

Structure:
  (A) Faithful implementation of the solution's algorithm: Dijkstra on G_n with
      an explicit Relax counter. Two variants are run:
        - lazy re-insertion ("re-enqueue on strict decrease"), i.e. the variant
          the solution's own trace (lines 0013-0017) describes and the only
          variant under which an exponential Relax count is even conceivable;
        - textbook extract-once Dijkstra.
      Both tie-breaking rules (lowest index first / highest index first) are run.
  (B) BRUTE-FORCE ORACLE #1: exhaustive enumeration of every simple path
      v_0 -> v_j in G_n (exact ints) giving the true shortest distances, used to
      confirm the graph/weights are implemented as specified.
  (C) BRUTE-FORCE ORACLE #2 (the decisive one): exhaustive search over EVERY
      legal execution of generalized Dijkstra-with-re-insertion on G_n, i.e.
      every possible adversarial resolution of priority-queue ties, returning
      the MAXIMUM number of Relax invocations any legal execution can perform.
      This is a true upper bound on R(n) over all Dijkstra implementations, so
      comparing it to 2^n - 1 settles the claim rather than merely testing one
      implementation.

  Relax counting convention: we count an invocation of Relax for EVERY outgoing
  edge examined when a vertex is processed (not just successful decreases).
  This is the LARGER, more generous reading, favouring the solution's claim.
"""

from itertools import combinations
import heapq
import sys

INF = None  # represented as None so that only exact ints are ever compared


# ----------------------------------------------------------------------------
# The solution's explicit graph family G_n
# ----------------------------------------------------------------------------
def build_Gn(n):
    """Vertices 0..n-1; edge (i,j) for i<j with integer weight -2**i."""
    adj = [[] for _ in range(n)]
    for i in range(n):
        for j in range(i + 1, n):
            adj[i].append((j, -(2 ** i)))
    return adj


def is_dag_with_negative_weights(n, adj):
    """Sanity: all edges go strictly forward (=> acyclic) and weights < 0."""
    if n < 2:
        return True, (n == 1)
    forward = all(j > i for i in range(n) for (j, _) in adj[i])
    negative = all(w < 0 for i in range(n) for (_, w) in adj[i])
    return forward, negative


# ----------------------------------------------------------------------------
# (A) FAITHFUL IMPLEMENTATION -- Dijkstra with an explicit Relax counter
# ----------------------------------------------------------------------------
def dijkstra_relax_count(n, adj, reinsert=True, tie="low"):
    """
    Dijkstra from v_0.

    reinsert=True : lazy priority queue; a vertex is (re-)enqueued every time its
                    tentative distance strictly decreases, and it is processed
                    whenever it is popped with a key equal to its current label.
                    This is the re-processing variant required for any
                    exponential Relax count to be possible.
    reinsert=False: textbook extract-once Dijkstra.

    tie="low" : ties broken by smallest vertex index.
    tie="high": ties broken by largest vertex index (adversarial).

    Returns (relax_calls, dist) with dist exact ints (None = unreached).
    """
    dist = [None] * n
    dist[0] = 0
    relax_calls = 0
    done = [False] * n

    def key(v):
        # exact-int priority; second component implements the tie-break rule
        return (dist[v], v if tie == "low" else -v)

    pq = [(0, 0 if tie == "low" else -0, 0)]  # (d, tiebreak, vertex)
    while pq:
        d, _tb, u = heapq.heappop(pq)
        if reinsert:
            if dist[u] is None or d != dist[u]:
                continue  # stale entry
        else:
            if done[u]:
                continue
        done[u] = True
        for (v, w) in adj[u]:
            relax_calls += 1                      # <-- Relax invocation
            nd = d + w                            # exact int arithmetic
            if dist[v] is None or nd < dist[v]:
                dist[v] = nd
                if reinsert or not done[v]:
                    heapq.heappush(pq, (nd, v if tie == "low" else -v, v))
    return relax_calls, dist


# ----------------------------------------------------------------------------
# (B) ORACLE #1 -- exhaustive shortest paths by enumerating all v0->vj paths
# ----------------------------------------------------------------------------
def oracle_shortest_dists(n, adj):
    """Enumerate every path v0 -> vj (all subsets of intermediate vertices, in
    increasing order, since the graph is a complete forward DAG). Exact ints."""
    W = {}
    for i in range(n):
        for (j, w) in adj[i]:
            W[(i, j)] = w
    best = [None] * n
    best[0] = 0
    for target in range(1, n):
        mids = list(range(1, target))
        for r in range(len(mids) + 1):
            for sub in combinations(mids, r):
                path = (0,) + sub + (target,)
                tot = 0
                ok = True
                for a, b in zip(path, path[1:]):
                    if (a, b) not in W:
                        ok = False
                        break
                    tot += W[(a, b)]
                if ok and (best[target] is None or tot < best[target]):
                    best[target] = tot
    return best


# ----------------------------------------------------------------------------
# (C) ORACLE #2 -- exhaustive over ALL legal Dijkstra executions (all tie orders)
# ----------------------------------------------------------------------------
def oracle_max_relax_over_all_tiebreaks(n, adj, node_budget=4_000_000):
    """
    Generalized Dijkstra with re-insertion, as a nondeterministic process:

      state = (dist tuple, frozenset of ACTIVE vertices)
      step  : the algorithm MUST extract an active vertex of minimum tentative
              distance; when several are tied, ANY of them may be chosen
              (that choice is exactly what a priority-queue implementation's
              tie-breaking/heap order decides). Processing u relaxes all
              outdeg(u) outgoing edges (that many Relax invocations) and
              re-activates every strictly improved head.

    Returns the MAXIMUM total Relax invocations over all legal executions, i.e.
    an exact upper bound on R(n) for ANY Dijkstra implementation on G_n.
    Returns None if the state-space budget is exhausted.
    """
    outdeg = [len(adj[u]) for u in range(n)]
    memo = {}
    counter = [0]

    def rec(dist, active):
        if not active:
            return 0
        st = (dist, active)
        if st in memo:
            return memo[st]
        counter[0] += 1
        if counter[0] > node_budget:
            raise RuntimeError("budget")
        m = min(dist[v] for v in active)          # exact int minimum
        best = 0
        for u in sorted(active):
            if dist[u] != m:
                continue
            d = list(dist)
            newly = set()
            for (v, w) in adj[u]:
                nd = dist[u] + w
                if d[v] is None or nd < d[v]:
                    d[v] = nd
                    newly.add(v)
            nxt = (active - {u}) | newly
            val = outdeg[u] + rec(tuple(d), frozenset(nxt))
            if val > best:
                best = val
        memo[st] = best
        return best

    dist0 = tuple([0] + [None] * (n - 1))
    try:
        return rec(dist0, frozenset([0]))
    except RuntimeError:
        return None


# ----------------------------------------------------------------------------
def main():
    print("=" * 78)
    print("record_id: Algorithms_21__sol5")
    print("claim_kind: PERFORMANCE (claimed LOWER bound R(n) >= 2^n - 1 = Omega(2^n))")
    print("family: G_n = complete forward DAG on v_0..v_{n-1}, w(v_i,v_j) = -2^i")
    print("Relax counting: one Relax per outgoing edge examined when a vertex is")
    print("processed (the most generous reading for the solution).")
    print("=" * 78)

    # --- structural sanity of the solution's construction -------------------
    n = 8
    adj = build_Gn(n)
    fwd, neg = is_dag_with_negative_weights(n, adj)
    print(f"\n[structure] n={n}: all edges forward (=> DAG): {fwd}; "
          f"all weights negative: {neg}")

    # --- ORACLE #1: distances agree with exhaustive path enumeration --------
    print("\n[oracle #1: exhaustive path enumeration vs. implementation]")
    dist_ok = True
    for n in range(1, 13):
        adj = build_Gn(n)
        ref = oracle_shortest_dists(n, adj) if n <= 12 else None
        _, dj = dijkstra_relax_count(n, adj, reinsert=True, tie="low")
        agree = (ref == dj)
        dist_ok &= agree
        if n in (1, 2, 4, 8, 12):
            print(f"  n={n:2d} true shortest dists (oracle) = {ref}")
            print(f"       Dijkstra-with-reinsertion dists = {dj}   agree={agree}")
    print(f"  distances agree with brute-force oracle for all n=1..12: {dist_ok}")
    print("  (note: true dist to v_j is -(2^j - 1), so the graph really does have"
          " exponentially large distances -- the weights are as specified.)")

    # --- (A) measured Relax counts across sizes -----------------------------
    print("\n[measured Relax invocation counts vs. the claimed lower bound 2^n - 1]")
    hdr = (f"{'n':>3} {'claim 2^n-1':>12} {'reinsert/low':>13} {'reinsert/high':>14}"
           f" {'extract-once':>13} {'n(n-1)/2':>9} {'MAX over ALL':>13}")
    print(hdr)
    print("-" * len(hdr))
    rows = []
    for n in range(2, 19):
        adj = build_Gn(n)
        claim = 2 ** n - 1
        c_lo, _ = dijkstra_relax_count(n, adj, reinsert=True, tie="low")
        c_hi, _ = dijkstra_relax_count(n, adj, reinsert=True, tie="high")
        c_once, _ = dijkstra_relax_count(n, adj, reinsert=False, tie="low")
        mx = oracle_max_relax_over_all_tiebreaks(n, adj, node_budget=60_000_000)
        rows.append((n, claim, c_lo, c_hi, c_once, n * (n - 1) // 2, mx))
        mxs = "budget" if mx is None else str(mx)
        print(f"{n:>3} {claim:>12} {c_lo:>13} {c_hi:>14} {c_once:>13}"
              f" {n*(n-1)//2:>9} {mxs:>13}")

    # --- verdict ------------------------------------------------------------
    print("\n[analysis]")
    print("  * The execution the solution itself traces (lines 0013-0017: v_0")
    print("    first, then a vertex at -1, then -1-2^k, ...) relaxes each edge")
    print("    exactly once: R(n) = |E_n| = n(n-1)/2 (column 'reinsert/low').")
    print("  * Allowing the adversary to resolve every priority-queue tie in the")
    print("    worst possible way does buy a little re-processing, but the")
    print("    exhaustive maximum over ALL legal Dijkstra executions is an exact")
    print("    CUBIC polynomial in n (closed form verified below), not 2^n.")
    print("  * Reason: w(v_i,v_j) = -2^i depends only on the TAIL index i, so the")
    print("    improvement a vertex can offer its successors is fixed once that")
    print("    vertex's own label is fixed; labels descend along the single chain")
    print("    v_0->v_1->...->v_j to the true optimum -(2^j - 1). There is no")
    print("    binary-counter cascade, so no exponential number of strict")
    print("    decreases. The solution's induction is also invalid on its own")
    print("    terms: it sums R(n-j) over the suffix subgraphs {v_j,...,v_{n-1}},")
    print("    j=1..n-1, which overlap and share edges, so the relaxations are")
    print("    massively double-counted.")

    # exact closed form for the adversarial maximum, from finite differences
    def cubic(n):
        k = n - 2
        return 1 + 2 * k + 2 * (k * (k - 1) // 2) + (k * (k - 1) * (k - 2) // 6)

    exhaustive_ok = all(r[6] is not None for r in rows)
    cubic_fit = all(r[6] == cubic(r[0]) for r in rows if r[6] is not None)
    all_below = all(r[6] is not None and r[6] < r[1] for r in rows)
    single_impl_below = all(max(r[2], r[3], r[4]) < r[1] for r in rows)
    hi_is_max = all(r[3] == r[6] for r in rows if r[6] is not None)

    print(f"\n  exhaustive tie-break search completed for every n=2..18: {exhaustive_ok}")
    print(f"  highest-index-first tie-breaking attains that maximum: {hi_is_max}")
    print(f"  MAX over all legal executions == 1+2k+2*C(k,2)+C(k,3), k=n-2 "
          f"(a CUBIC): {cubic_fit}")
    print(f"  MAX over all legal executions < 2^n - 1 for every tested n>=2: {all_below}")
    print(f"  every concrete implementation's count < 2^n - 1 for every n>=2: "
          f"{single_impl_below}")

    # growth constants, made visible
    print("\n[growth, constants visible]")
    print("  worst-case-over-all-executions R_max(n) vs claimed lower bound 2^n-1:")
    for (n, claim, c_lo, _hi, _once, edges, mx) in rows:
        val = mx if mx is not None else c_lo
        print(f"    n={n:2d}:  R_max={val:>5}  claim={claim:<7} ratio={val/claim:.8f}"
              f"   traced-execution R(n)={c_lo}")
    closed = all((n ** 3 - 3 * n ** 2 + 8 * n - 6) % 6 == 0
                 and (n ** 3 - 3 * n ** 2 + 8 * n - 6) // 6 == r[6]
                 for r in rows for n in [r[0]] if r[6] is not None)
    assert closed, "closed form mismatch"
    print("\n  R_max(n) = (n^3 - 3n^2 + 8n - 6)/6  -- third finite difference is")
    print("  constantly 1 across n=2..18, so R_max(n) = Theta(n^3) = o(2^n).")
    print("  The claimed lower bound therefore fails at EVERY n >= 2, and the gap")
    print("  widens geometrically: n=8: 63 < 255; n=12: 231 < 4095;")
    print("  n=18: 833 < 262143 (a factor of 315 short).")

    smallest = min((r[0] for r in rows if max(r[2], r[3], r[4]) < r[1]), default=None)
    print(f"\n  smallest n at which the claimed bound already fails: n={smallest}")

    violated = single_impl_below and all_below and exhaustive_ok and dist_ok
    print("\n" + "=" * 78)
    if violated:
        print("VERDICT: BOUND_VIOLATION_FOUND")
        print("  The claimed lower bound R(n) >= 2^n - 1 (Omega(2^n)) is refuted on")
        print("  the solution's OWN explicitly defined family G_n. Instrumented")
        print("  Relax counts under the solution's own traced execution are exactly")
        print("  n(n-1)/2; and this is not an artifact of one implementation --")
        print("  exhaustive search over EVERY legal priority-queue tie-breaking of")
        print("  Dijkstra-with-re-insertion (n=2..18) gives a maximum that is an")
        print("  exact cubic polynomial. e.g. n=12: 66 (traced) / 231 (adversarial")
        print("  maximum) vs the claimed >= 4095.")
    else:
        print("VERDICT: NO_BUG_FOUND")
    print("=" * 78)


if __name__ == "__main__":
    sys.setrecursionlimit(100000)
    main()
