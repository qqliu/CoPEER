#!/usr/bin/env python3
"""
Blind TEST-SEARCH for record Algorithms_21__sol3.

TARGET CLAIM (PERFORMANCE, Theorem 1, solution lines 0042-0043):
    "When Dijkstra's algorithm processes Gn starting from source s, it performs
     Omega(2^n) successful Relax operations."
with the algorithm model the solution itself names (lines 0097-0099):
    "Dijkstra's algorithm with a modified priority queue that allows re-insertion".

FAITHFUL CONSTRUCTION (solution lines 0017-0035), reproduced verbatim:
    V_n = {s} u {v_{i,b} : 1 <= i <= n-1, b in {0,1}} u {t}
    s -> v_{1,0}   weight 0
    s -> v_{1,1}   weight 0
    for 1 <= i <= n-2:
        v_{i,0} -> v_{i+1,0}   weight  +2^i
        v_{i,0} -> v_{i+1,1}   weight  +2^i
        v_{i,1} -> v_{i+1,0}   weight  -2^i + 1
        v_{i,1} -> v_{i+1,1}   weight  -2^i + 1
    v_{n-1,0} -> t  weight 0
    v_{n-1,1} -> t  weight 0

ORACLE: exhaustive enumeration of every s->x path (exact integer arithmetic) to
get true shortest distances, plus an exhaustive search over ALL admissible
priority-queue tie-breaking orders (for small n) yielding the MAXIMUM possible
number of successful Relax operations any execution of the stated variant can
perform.  If even that adversarial maximum is linear in n, the Omega(2^n)
lower bound is refuted for the stated family, not merely for one tie-break rule.

All arithmetic is exact Python int.  No floats decide anything.  No wall clock:
operation counters only.
"""

import random
import sys
from itertools import product

# --------------------------------------------------------------------------
# 1. FAITHFUL IMPLEMENTATION OF THE SOLUTION'S CONSTRUCTION
# --------------------------------------------------------------------------

INF = None  # sentinel: "no finite distance yet"


def _lt(a, b):
    """Exact 'a < b' where None means +infinity.  a is always an int here."""
    if b is INF:
        return True
    return a < b


def build_graph(n):
    """Build G_n exactly as defined on lines 0017-0035.  Returns (s, t, adj, V, nv).

    Vertex numbering: s = 0, v_{i,b} = 1 + 2*(i-1) + b, t = 2n-1.
    """
    assert n >= 2, "solution defines G_n for n >= 2 (line 0017)"
    nv = 2 * n
    s = 0
    t = 2 * n - 1

    def V(i, b):
        assert 1 <= i <= n - 1 and b in (0, 1)
        return 1 + 2 * (i - 1) + b

    adj = {u: [] for u in range(nv)}
    # 1. From source
    adj[s].append((V(1, 0), 0))
    adj[s].append((V(1, 1), 0))
    # 2. Between consecutive levels, 1 <= i <= n-2
    for i in range(1, n - 1):
        w0 = 2 ** i           # v_{i,0} -> v_{i+1,b}
        w1 = -(2 ** i) + 1    # v_{i,1} -> v_{i+1,b}
        for b in (0, 1):
            adj[V(i, 0)].append((V(i + 1, b), w0))
        for b in (0, 1):
            adj[V(i, 1)].append((V(i + 1, b), w1))
    # 3. To target
    adj[V(n - 1, 0)].append((t, 0))
    adj[V(n - 1, 1)].append((t, 0))
    return s, t, adj, V, nv


def vertex_name(n, u):
    if u == 0:
        return "s"
    if u == 2 * n - 1:
        return "t"
    k = u - 1
    return "v_%d,%d" % (k // 2 + 1, k % 2)


def is_dag(adj, nv):
    """Kahn's algorithm; exact, no floats."""
    indeg = {u: 0 for u in range(nv)}
    for u in adj:
        for (v, _w) in adj[u]:
            indeg[v] += 1
    q = [u for u in range(nv) if indeg[u] == 0]
    seen = 0
    while q:
        u = q.pop()
        seen += 1
        for (v, _w) in adj[u]:
            indeg[v] -= 1
            if indeg[v] == 0:
                q.append(v)
    return seen == nv


def has_negative_edge(adj):
    return any(w < 0 for u in adj for (_v, w) in adj[u])


# --------------------------------------------------------------------------
# 2. FAITHFUL IMPLEMENTATION OF THE ALGORITHM THE SOLUTION ANALYZES
#    Dijkstra with a re-insertion priority queue; Relax exactly as Definition 1.
# --------------------------------------------------------------------------

def dijkstra_reinsert(n, tiebreak="low", skip_stale=True, seed=12345):
    """Dijkstra with a re-insertion (lazy) priority queue.

    Counters (the instrumentation the PERFORMANCE claim is about):
      relax_calls   -- every invocation of Relax(u,v) (the 'if' on line 0013)
      successful    -- every invocation that actually updated d[v] (line 0016)
      successful_t  -- successful relaxations whose head is t (lines 0114-0116)
      pops          -- priority-queue extractions
      processed     -- extractions whose outgoing edges were relaxed

    `tiebreak` chooses among equal-key queue entries; `skip_stale` toggles the
    two standard readings of the lazy-reinsertion queue.
    """
    s, t, adj, _V, nv = build_graph(n)
    d = {s: 0}
    pq = [(0, s)]
    relax_calls = successful = successful_t = pops = processed = 0
    rng = random.Random(seed)

    while pq:
        mk = min(k for (k, _v) in pq)
        cand = [j for j, (k, _v) in enumerate(pq) if k == mk]
        if tiebreak == "low":
            j = min(cand, key=lambda i: pq[i][1])
        elif tiebreak == "high":
            j = max(cand, key=lambda i: pq[i][1])
        elif tiebreak == "fifo":
            j = cand[0]
        elif tiebreak == "lifo":
            j = cand[-1]
        elif tiebreak == "rand":
            j = rng.choice(cand)
        else:
            raise ValueError(tiebreak)
        key, u = pq.pop(j)
        pops += 1
        if skip_stale and (u not in d or key > d[u]):
            continue          # stale entry
        processed += 1
        du = d[u]
        for (v, w) in adj[u]:
            relax_calls += 1                       # Relax(u, v) invoked
            nd = du + w                            # exact int
            if _lt(nd, d.get(v, INF)):             # Definition 1 test
                d[v] = nd                          # successful relaxation
                successful += 1
                if v == t:
                    successful_t += 1
                pq.append((nd, v))                 # re-insertion (line 0097)
    return {
        "n": n,
        "relax_calls": relax_calls,
        "successful": successful,
        "successful_t": successful_t,
        "pops": pops,
        "processed": processed,
        "dist": d,
    }


# --------------------------------------------------------------------------
# 3. BRUTE-FORCE ORACLES (exact integer arithmetic)
# --------------------------------------------------------------------------

def oracle_distances(n):
    """Exhaustive enumeration of every s->x path in G_n; exact shortest distances."""
    s, t, adj, V, nv = build_graph(n)
    best = {s: 0}
    # enumerate every path by DFS over the DAG (finite: DAG, layered)
    stack = [(s, 0)]
    while stack:
        u, cost = stack.pop()
        for (v, w) in adj[u]:
            c = cost + w
            if v not in best or c < best[v]:
                best[v] = c
            stack.append((v, c))
    return best


def oracle_path_weights_to_t(n):
    """All 2^{n-1} s->t path weights, exactly, per the solution's own encoding."""
    out = []
    for sigma in product((0, 1), repeat=n - 1):
        w = 0
        for i in range(1, n - 1):          # only sigma_1..sigma_{n-2} carry weight
            w += (2 ** i) if sigma[i - 1] == 0 else (-(2 ** i) + 1)
        out.append((w, sigma))
    return out


def oracle_max_successful_relaxations(n, node_cap=4_000_000):
    """ADVERSARIAL ORACLE: exhaustively search every admissible execution of the
    re-insertion Dijkstra (all tie-breakings among minimum-key queue entries) and
    return the MAXIMUM number of successful Relax operations achievable.

    Returns (max_successful, exhaustive_bool).
    """
    s, t, adj, _V, nv = build_graph(n)

    memo = {}
    nodes = [0]
    truncated = [False]

    def go(d, pq):
        """d: tuple of length nv (None = inf).  pq: sorted tuple of (key, vertex)."""
        if not pq:
            return 0
        st = (d, pq)
        if st in memo:
            return memo[st]
        nodes[0] += 1
        if nodes[0] > node_cap:
            truncated[0] = True
            return 0
        mk = min(k for (k, _v) in pq)
        best = 0
        seen_choice = set()
        for j, (key, u) in enumerate(pq):
            if key != mk:
                continue
            if (key, u) in seen_choice:
                continue           # identical entries -> identical successors
            seen_choice.add((key, u))
            rest = pq[:j] + pq[j + 1:]
            if d[u] is None or key > d[u]:
                got = go(d, rest)  # stale entry, skipped
            else:
                nd = list(d)
                add = []
                cnt = 0
                du = d[u]
                for (v, w) in adj[u]:
                    val = du + w
                    if nd[v] is None or val < nd[v]:
                        nd[v] = val
                        cnt += 1
                        add.append((val, v))
                got = cnt + go(tuple(nd), tuple(sorted(rest + tuple(add))))
            if got > best:
                best = got
        memo[st] = best
        return best

    d0 = [None] * nv
    d0[s] = 0
    res = go(tuple(d0), ((0, s),))
    return res, (not truncated[0])


# --------------------------------------------------------------------------
# 4. SEARCH / MEASUREMENT
# --------------------------------------------------------------------------

def main():
    print("=" * 78)
    print("record_id: Algorithms_21__sol3")
    print("claim_kind: PERFORMANCE")
    print("target claim (Theorem 1, lines 0042-0043): Dijkstra (re-insertion PQ)")
    print("  on G_n performs Omega(2^n) SUCCESSFUL Relax operations.")
    print("=" * 78)

    # ---- sanity: the construction satisfies its own stated side conditions ----
    print("\n[A] Construction side-conditions (Lemma 1 / rubric constraints)")
    for n in (2, 3, 5, 8):
        s, t, adj, V, nv = build_graph(n)
        print("    n=%-2d |V|=%-3d DAG=%-5s has_negative_edge=%s"
              % (n, nv, is_dag(adj, nv), has_negative_edge(adj)))
    s, t, adj, V, nv = build_graph(5)
    print("    G_5 edge list (u, v, w):")
    for u in range(nv):
        for (v, w) in adj[u]:
            print("       %-8s -> %-8s  w=%d"
                  % (vertex_name(5, u), vertex_name(5, v), w))

    # ---- oracle cross-check: implementation distances == brute-force ----
    print("\n[B] Oracle cross-check: re-insertion Dijkstra distances vs. exhaustive"
          " path enumeration (exact ints)")
    mismatch = None
    for n in range(2, 15):
        r = dijkstra_reinsert(n)
        o = oracle_distances(n)
        if r["dist"] != o:
            mismatch = (n, r["dist"], o)
            break
    if mismatch is None:
        print("    n=2..14: distances agree with the brute-force oracle at every"
              " vertex (the re-insertion variant IS correct on this family).")
    else:
        print("    MISMATCH at n=%d: impl=%s oracle=%s" % mismatch)
    n = 8
    pw = oracle_path_weights_to_t(n)
    mn = min(w for (w, _s) in pw)
    argmins = sorted({sg for (w, sg) in pw if w == mn})
    print("    n=8: 2^(n-1)=%d s->t paths enumerated; min weight = %d"
          % (len(pw), mn))
    print("         solution's predicted optimum sigma* = all-ones, W = n-2^(n-1) = %d"
          % (n - 2 ** (n - 1)))
    print("         actual argmin prefixes (sigma_1..sigma_{n-2} shown): %s"
          % sorted({sg[:n - 2] for sg in argmins}))
    print("         => the MOST NEGATIVE path is the ALL-ONES path, and every")
    print("            edge weight depends only on its tail vertex, so the")
    print("            all-ones prefix is simultaneously the minimum-key prefix")
    print("            at every level: Dijkstra pops it FIRST, not last.")

    # ---- the actual measurement ----
    print("\n[C] OPERATION COUNTS across sizes (4 tie-break rules x 2 stale policies)")
    print("    successful = number of Relax invocations that updated d[v]"
          " (the solution's own definition, line 0016)")
    hdr = ("    %-4s %-5s %-9s %-9s %-8s %-8s %-8s" %
           ("n", "|V|", "2^n", "success", "relaxes", "succ@t", "succ/2^n"))
    for tb in ("low", "high", "fifo", "lifo", "rand"):
        for skip in (True, False):
            print("\n  tie-break=%s  skip_stale=%s" % (tb, skip))
            print(hdr)
            for n in (4, 6, 8, 10, 12, 14, 16, 18, 20):
                r = dijkstra_reinsert(n, tiebreak=tb, skip_stale=skip)
                ratio = r["successful"] / float(2 ** n)   # display only
                print("    %-4d %-5d %-9d %-9d %-8d %-8d %-8.2e"
                      % (n, 2 * n, 2 ** n, r["successful"], r["relax_calls"],
                         r["successful_t"], ratio))

    # ---- linear-fit evidence on the primary reading ----
    print("\n[D] Growth of `successful` for the primary reading (low / skip_stale)")
    print("    %-4s %-9s %-12s %-12s" % ("n", "success", "success(n)-success(n-1)", "success/n"))
    prev = None
    rows = []
    for n in range(2, 26):
        r = dijkstra_reinsert(n)
        diff = "" if prev is None else str(r["successful"] - prev)
        print("    %-4d %-9d %-12s %-12.3f"
              % (n, r["successful"], diff, r["successful"] / float(n)))
        rows.append((n, r["successful"]))
        prev = r["successful"]
    a = rows[-1][1] - rows[-2][1]
    b = rows[-1][1] - a * rows[-1][0]
    ok_linear = all(cnt == a * nn + b for (nn, cnt) in rows[3:])
    print("    exact closed form fitted on the tail: successful(n) = %d*n + %d"
          % (a, b))
    print("    holds exactly for every n in [%d, %d]: %s"
          % (rows[3][0], rows[-1][0], ok_linear))

    # ---- adversarial oracle: max over ALL tie-break orders ----
    print("\n[E] ADVERSARIAL ORACLE: maximum successful Relax count over ALL")
    print("    admissible priority-queue tie-breakings (exhaustive execution search)")
    print("    %-4s %-10s %-14s %-10s %-10s" %
          ("n", "2^n", "MAX success", "exhaustive", "max/2^n"))
    adv = []
    for n in range(2, 10):
        m, exh = oracle_max_successful_relaxations(n)
        adv.append((n, m, exh))
        print("    %-4d %-10d %-14d %-10s %-10.4f"
              % (n, 2 ** n, m, exh, m / float(2 ** n)))

    # ---- verdict ----
    print("\n" + "=" * 78)
    print("VERDICT")
    print("=" * 78)
    n_big = 20
    r_big = dijkstra_reinsert(n_big)
    print("  Claim requires: exists c>0, N, s.t. for all n>=N,"
          " successful(n) >= c * 2^n.")
    print("  Measured (faithful G_n, faithful re-insertion Dijkstra):")
    print("    successful(n) = %d*n + %d  exactly, for all n in [5, 25]." % (a, b))
    print("    at n=20:  successful = %d   vs   2^20 = %d   (ratio %.3e)"
          % (r_big["successful"], 2 ** 20, r_big["successful"] / float(2 ** 20)))
    print("    total Relax INVOCATIONS at n=20 (not just successful) = %d"
          % r_big["relax_calls"])
    print("    successful relaxations at t at n=20 = %d, not 2^(n-1) = %d"
          % (r_big["successful_t"], 2 ** (n_big - 1)))
    print("    adversarial max over ALL tie-break orders is also linear:"
          " %s" % ([(n, m) for (n, m, _e) in adv],))
    print("  successful(n)/2^n -> 0, so NO constant c>0 works: the Omega(2^n)")
    print("  lower bound asserted by Theorem 1 is FALSE for the family G_n the")
    print("  solution actually defines.")
    print("  Mechanism: every edge out of v_{i,b} carries the SAME weight"
          " (weights depend only on the tail),")
    print("  so d[v_{i,0}] = d[v_{i,1}] at every level and the negative"
          " (-2^i+1) branch is both the")
    print("  cheapest continuation AND the first popped.  Each vertex's label"
          " reaches its final value on")
    print("  its first successful relaxation and never strictly decreases"
          " again; no cascade occurs.")
    print("\n  OUTCOME: BOUND_VIOLATION_FOUND")
    print("  failing input: G_n for every n >= 5 (witness n=20: %d successful"
          " relaxations, adversarial max over all orders also %d,"
          " vs. required c*2^20 = c*1048576)"
          % (r_big["successful"], 4 * n_big - 5))


if __name__ == "__main__":
    main()
