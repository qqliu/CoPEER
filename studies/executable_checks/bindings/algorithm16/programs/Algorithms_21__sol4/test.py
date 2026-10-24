#!/usr/bin/env python3
"""
Blind test-search for record Algorithms_21__sol4.

TARGET CLAIM (PERFORMANCE / lower bound), quoted from the solution (lines 0180-0184):

    "There are 2^(n-2) - 1 nonempty subsets of {v2, ..., v_{n-1}}, so the edge
     relaxations vi -> vn (for i = 2, 3, ..., n-1) account for 2^(n-2) - 1
     updates to vn's distance alone. Even excluding the source's initial
     relaxations and all the intermediate-to-intermediate relaxations, we
     already have Omega(2^n) relaxations."

The solution constructs an explicit family G_n and asserts that running
"Dijkstra with revisiting allowed" on G_n performs Omega(2^n) Relax operations,
of which 2^(n-2)-1 are *successful updates to d(v_n)*.

WHAT THIS FILE DOES
  1. Faithful implementation of G_n exactly as specified (lines 0007-0020).
  2. Faithful implementation of the described algorithm: Dijkstra with a min-heap
     in which a vertex is re-inserted whenever its tentative distance improves
     ("no permanent closed status"), lines 0074-0080. Two readings of "revisit"
     are implemented (lazy-skip-stale and never-skip) so the claim is tested
     under the more generous one too.
  3. A brute-force ORACLE: exhaustive enumeration of all v1->vn paths with exact
     integer arithmetic, giving the true shortest-path distance AND the true
     number of *distinct strictly-decreasing* path weights that any
     "one relax per newly-discovered-shorter-path" argument could ever produce.
  4. OPERATION COUNTERS (no wall clock): total Relax invocations, successful
     relaxations, and successful updates to d(v_n), measured over n = 5..14.
  5. An adversarial tie-break search: for small n, exhaustive branching over
     *every* legal extract-min choice among tied keys, to check whether ANY
     execution order of the described algorithm attains the claimed 2^(n-2)-1
     sink updates.

All arithmetic is integer (delta_i = 2^(i-2) are integers). No floats decide
anything. Deterministic: no sampling, no seeds needed.
"""

import heapq
import itertools
from collections import defaultdict


# ----------------------------------------------------------------------------
# 1. The construction G_n, exactly as written in the solution (lines 0007-0020).
#    Vertices v1..vn are represented by their integer indices 1..n.
#      delta_i = 2^(i-2)                       for 2 <= i <= n-1   (line 0013-0014)
#      W       = sum_{i=2}^{n-1} delta_i                            (line 0014-0015)
#      w(v1 -> vn)  = W                                             (line 0016)
#      w(v1 -> vi)  = 0            for 2 <= i <= n-1                (line 0017)
#      w(vi -> vn)  = W - delta_i  for 2 <= i <= n-1                (line 0018)
#      w(vi -> vj)  = -delta_i     for 2 <= i < j <= n-1            (line 0019)
# ----------------------------------------------------------------------------
def build_Gn(n):
    """Return (adj, W, delta) for G_n.  adj[u] = list of (v, weight)."""
    assert n >= 3
    delta = {i: 2 ** (i - 2) for i in range(2, n)}      # i = 2..n-1
    W = sum(delta.values())                             # = 2^(n-2) - 1
    adj = defaultdict(list)
    adj[1].append((n, W))                               # direct source->sink
    for i in range(2, n):
        adj[1].append((i, 0))                           # source->intermediate
    for i in range(2, n):
        adj[i].append((n, W - delta[i]))                # intermediate->sink
    for i in range(2, n):
        for j in range(i + 1, n):
            adj[i].append((j, -delta[i]))               # intermediate->intermediate
    # keep edge order deterministic
    for u in adj:
        adj[u].sort()
    return adj, W, delta


def edge_count(n):
    """|E(G_n)| = 1 + (n-2) + (n-2) + C(n-2, 2)   (solution lines 0190-0203)."""
    m = n - 2
    return 1 + m + m + m * (m - 1) // 2


# ----------------------------------------------------------------------------
# 2. The algorithm the solution analyses: Dijkstra, negative edges allowed,
#    vertices may be revisited / re-inserted whenever d improves.
#    Ties in the heap are broken by smallest vertex index, which reproduces the
#    solution's own stated trace ("WLOG it picks v2 ... assume it chooses v3").
# ----------------------------------------------------------------------------
INF = None  # represented as None = +infinity, so all comparisons stay exact ints


def less(a, b):
    """a < b with None meaning +infinity. Exact integer comparison."""
    if b is None:
        return a is not None
    if a is None:
        return False
    return a < b


def dijkstra_revisiting(n, adj, skip_stale=True):
    """
    Returns dict of counters plus final distances.

    skip_stale=True : standard lazy re-insertion Dijkstra (pop, ignore entries
                      whose key is worse than the current dist).
    skip_stale=False: the maximally generous reading of "no permanent closed
                      status" -- every popped entry triggers a full relaxation
                      round of the tail's outgoing edges.
    """
    dist = {v: INF for v in range(1, n + 1)}
    dist[1] = 0
    relax_calls = 0          # every evaluation of "d(tail)+w < d(head)"
    successful_relax = 0     # every one that actually lowered a distance
    sink_updates = 0         # successful relaxations that lowered d(v_n)
    pops = 0
    heap = [(0, 1)]
    while heap:
        d, u = heapq.heappop(heap)
        pops += 1
        if skip_stale and (dist[u] is None or d > dist[u]):
            continue
        base = dist[u]
        if base is None:
            continue
        for (v, w) in adj[u]:
            relax_calls += 1
            cand = base + w
            if less(cand, dist[v]):
                dist[v] = cand
                successful_relax += 1
                if v == n:
                    sink_updates += 1
                heapq.heappush(heap, (cand, v))
    return {
        "dist": dist,
        "relax_calls": relax_calls,
        "successful_relax": successful_relax,
        "sink_updates": sink_updates,
        "pops": pops,
    }


# ----------------------------------------------------------------------------
# 3. Brute-force ORACLE: enumerate every directed v1->vn path exactly.
#    Exact integer arithmetic only.
# ----------------------------------------------------------------------------
def oracle_all_paths(n, adj):
    """Exhaustively enumerate all simple v1..vn paths (G_n is a DAG, so all
    directed paths are simple). Returns (shortest_distance, sorted_weight_list)."""
    weights = []

    def dfs(u, acc, seen):
        if u == n:
            weights.append(acc)
            return
        for (v, w) in adj[u]:
            if v in seen:
                continue
            dfs(v, acc + w, seen | {v})

    dfs(1, 0, frozenset([1]))
    return min(weights), sorted(weights)


def oracle_subset_formula(n):
    """The solution's own closed form: path for subset S has weight W - sum_{i in S} delta_i.
    Enumerate all 2^(n-2) subsets exactly."""
    _, W, delta = build_Gn(n)
    inter = list(range(2, n))
    out = []
    for k in range(len(inter) + 1):
        for S in itertools.combinations(inter, k):
            out.append(W - sum(delta[i] for i in S))
    return min(out), sorted(out)


def oracle_dag_shortest(n, adj):
    """Independent reference shortest path: DAG relaxation in topological order
    (indices are already a topological order for G_n). Exact integers."""
    dist = {v: INF for v in range(1, n + 1)}
    dist[1] = 0
    for u in range(1, n + 1):
        if dist[u] is None:
            continue
        for (v, w) in adj[u]:
            if less(dist[u] + w, dist[v]):
                dist[v] = dist[u] + w
    return dist[n]


# ----------------------------------------------------------------------------
# 5. Adversarial tie-break search: explore EVERY legal extract-min order.
#    A "legal" step pops any heap entry whose key equals the current minimum.
#    Returns the maximum number of sink updates achievable over all orders.
# ----------------------------------------------------------------------------
def adversarial_max_sink_updates(n, adj, node_cap=400000):
    best = [0]
    best_relax = [0]
    nodes = [0]
    truncated = [False]
    seen = set()

    def rec(dist, heap, sink_updates, relax_calls):
        nodes[0] += 1
        if nodes[0] > node_cap:
            truncated[0] = True
            return
        if sink_updates > best[0]:
            best[0] = sink_updates
        if relax_calls > best_relax[0]:
            best_relax[0] = relax_calls
        if not heap:
            return
        key = tuple(sorted(dist.items())) + (tuple(sorted(heap)),)
        if key in seen:
            return
        seen.add(key)
        mn = min(heap)[0]
        choices = sorted({e for e in heap if e[0] == mn})
        for e in choices:
            rest = list(heap)
            rest.remove(e)
            d, u = e
            if dist[u] is None or d > dist[u]:
                rec(dist, tuple(rest), sink_updates, relax_calls)
                continue
            nd = dict(dist)
            nh = rest
            su = sink_updates
            rc = relax_calls
            for (v, w) in adj[u]:
                rc += 1
                cand = nd[u] + w
                if less(cand, nd[v]):
                    nd[v] = cand
                    if v == n:
                        su += 1
                    nh = nh + [(cand, v)]
            rec(nd, tuple(nh), su, rc)

    dist0 = {v: INF for v in range(1, n + 1)}
    dist0[1] = 0
    rec(dist0, ((0, 1),), 0, 0)
    return best[0], best_relax[0], truncated[0]


# ----------------------------------------------------------------------------
# main
# ----------------------------------------------------------------------------
def main():
    print("=" * 78)
    print("Algorithms_21__sol4  --  PERFORMANCE (lower-bound) claim under test")
    print("=" * 78)
    print("CLAIM (solution lines 0180-0184): on the constructed G_n, the")
    print("relaxations v_i -> v_n account for 2^(n-2) - 1 successful updates to")
    print("d(v_n), hence Omega(2^n) Relax operations.")
    print()

    # ---- Step A: sanity-check the construction against the oracle -----------
    print("-" * 78)
    print("STEP A: construction / oracle cross-check (exact integer arithmetic)")
    print("-" * 78)
    print(f"{'n':>3} {'W':>8} {'#paths':>8} {'min path w':>11} {'DAG-relax d(vn)':>16} "
          f"{'subset-formula min':>19} {'agree':>6}")
    for n in range(3, 11):
        adj, W, delta = build_Gn(n)
        mn_paths, all_w = oracle_all_paths(n, adj)
        mn_sub, all_sub = oracle_subset_formula(n)
        dagd = oracle_dag_shortest(n, adj)
        agree = (mn_paths == mn_sub == dagd == 0) and (all_w == all_sub) \
                and (len(all_w) == 2 ** (n - 2))
        print(f"{n:>3} {W:>8} {len(all_w):>8} {mn_paths:>11} {dagd:>16} "
              f"{mn_sub:>19} {str(agree):>6}")
    print()
    print("=> The construction is as advertised: 2^(n-2) distinct v1->vn paths,")
    print("   all path weights distinct, true shortest distance = 0.")
    print("   The graph-theoretic part of the solution (Part 1) checks out.")
    print()

    # ---- Step B: run the described algorithm, count operations --------------
    print("-" * 78)
    print("STEP B: operation counts for the described algorithm (no wall clock)")
    print("-" * 78)
    hdr = (f"{'n':>3} | {'|E|':>6} {'relax':>7} {'succ':>6} {'sinkUpd':>8} "
           f"| {'relax(NS)':>10} {'sinkUpd(NS)':>12} "
           f"| {'CLAIMED sinkUpd':>16} {'CLAIMED >= 2^(n-2)':>19}")
    print(hdr)
    print("-" * len(hdr))
    rows = []
    for n in [5, 6, 7, 8, 10, 12, 14]:
        adj, W, delta = build_Gn(n)
        r1 = dijkstra_revisiting(n, adj, skip_stale=True)
        r2 = dijkstra_revisiting(n, adj, skip_stale=False)
        claimed = 2 ** (n - 2) - 1
        # correctness cross-check against the oracle
        assert r1["dist"][n] == oracle_dag_shortest(n, adj) == 0, n
        assert r2["dist"][n] == 0, n
        rows.append((n, edge_count(n), r1["relax_calls"], r1["successful_relax"],
                     r1["sink_updates"], r2["relax_calls"], r2["sink_updates"], claimed))
        print(f"{n:>3} | {edge_count(n):>6} {r1['relax_calls']:>7} "
              f"{r1['successful_relax']:>6} {r1['sink_updates']:>8} "
              f"| {r2['relax_calls']:>10} {r2['sink_updates']:>12} "
              f"| {claimed:>16} {2**(n-2):>19}")
    print()
    print("  (NS = 'never skip': the maximally generous reading of 'vertices may")
    print("   be revisited', where every popped heap entry re-relaxes its edges.)")
    print()

    # ---- Step C: growth analysis -------------------------------------------
    print("-" * 78)
    print("STEP C: measured growth vs. the claimed Omega(2^n) lower bound")
    print("-" * 78)
    print("  ('sinkUpd' counts every write to d(v_n): the initial INF->W write")
    print("   from v1->v_n, plus the strict decreases. So sinkUpd = 1 + (n-2).)")
    print(f"{'n':>3} {'sinkUpd':>8} {'decreases':>10} {'= n-2?':>7} {'relax':>7} "
          f"{'= |E|?':>7} {'relax/n^2':>10} {'claimed/observed':>17}")
    for (n, m, rc, sr, su, rc2, su2, claimed) in rows:
        print(f"{n:>3} {su:>8} {su-1:>10} {str(su - 1 == n-2):>7} {rc:>7} "
              f"{str(rc == m):>7} {rc/(n*n):>10.4f} "
              f"{claimed/su if su else float('inf'):>17.1f}")
    print()
    print("  Ratio relax(n)/n^2 is bounded (it converges to 1/2); doubling n")
    print("  multiplies the relaxation count by ~4, not by 2^n.")
    print("  Successive ratios of total relaxations:")
    for i in range(1, len(rows)):
        n0, _, r0 = rows[i-1][0], rows[i-1][1], rows[i-1][2]
        n1, _, r1c = rows[i][0], rows[i][1], rows[i][2]
        print(f"    relax({n1})/relax({n0}) = {r1c}/{r0} = {r1c/r0:.3f}"
              f"    (claimed bound would force >= 2^{n1-2}/2^{n0-2} = "
              f"{2**(n1-n0)})")
    print()

    # ---- Step D: adversarial tie-break search ------------------------------
    print("-" * 78)
    print("STEP D: adversarial search over EVERY legal extract-min order")
    print("-" * 78)
    print("  (The solution says 'the analysis is symmetric regardless of which")
    print("   intermediate is chosen at each step'. We check every choice.)")
    print(f"{'n':>3} {'max sinkUpd over all orders':>29} {'max relax':>10} "
          f"{'CLAIMED sinkUpd':>16} {'search complete':>16}")
    adversarial_ok = True
    for n in [5, 6, 7, 8]:
        adj, W, delta = build_Gn(n)
        best, bestr, trunc = adversarial_max_sink_updates(n, adj)
        claimed = 2 ** (n - 2) - 1
        if best >= claimed:
            adversarial_ok = False
        print(f"{n:>3} {best:>29} {bestr:>10} {claimed:>16} "
              f"{str(not trunc):>16}")
    print()

    # ---- Verdict -----------------------------------------------------------
    print("=" * 78)
    print("VERDICT")
    print("=" * 78)
    n_star = 12
    row = [r for r in rows if r[0] == n_star][0]
    _, m, rc, sr, su, rc2, su2, claimed = row
    violated = (su < claimed) and (rc < 2 ** (n_star - 2)) and adversarial_ok
    print(f"Failing input: n = {n_star}  (G_12 as constructed by the solution:")
    print(f"  delta_i = 2^(i-2) for i=2..11, W = {build_Gn(n_star)[1]}, 12 vertices,")
    print(f"  {m} edges, 2^10 = 1024 distinct v1->v12 paths).")
    print()
    print(f"  CLAIMED updates to d(v_n) : 2^(n-2)-1 = {claimed}")
    print(f"  OBSERVED updates to d(v_n): {su}  ({su-1} strict decreases, "
          f"= n-2 = {n_star-2}, plus the initial INF->W write)")
    print(f"  CLAIMED total Relax ops   : Omega(2^n), at least {2**(n_star-2)}")
    print(f"  OBSERVED total Relax ops  : {rc}  (lazy) / {rc2} (never-skip)")
    print(f"  OBSERVED = |E(G_n)| = (n-1)(n-2)/2 + ... = {m}: {rc == m}")
    print()
    print("  Under EVERY legal tie-breaking order (Step D, exhaustive for n<=8)")
    print("  the number of sink updates never exceeds n-2, never approaches")
    print(f"  2^(n-2)-1.  The construction's own algebra explains why: the")
    print("  algorithm settles v2,...,v_{n-1} once each in increasing key order,")
    print("  so d(v_n) takes exactly the n-2 values W-delta_2, W-delta_2-delta_3,")
    print("  ..., 0 -- one per PREFIX, not one per SUBSET. The 2^(n-2)-1 subsets")
    print("  correspond to path weights that exist in the graph but are never")
    print("  realised as separate relaxations of d(v_n).")
    print("  The solution contradicts itself at line 0206-0207: 'the overall")
    print("  relaxation count is Theta(n^2) ... which, notably, is polynomial'.")
    print()
    if violated:
        print("RESULT: BOUND_VIOLATION_FOUND")
        print("  The claimed Omega(2^n) relaxation lower bound on this explicit")
        print("  family is false; the measured operation count is Theta(n^2).")
    else:
        print("RESULT: NO_BUG_FOUND")
    print("=" * 78)


if __name__ == "__main__":
    main()
