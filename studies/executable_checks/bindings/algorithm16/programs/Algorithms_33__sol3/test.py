#!/usr/bin/env python3
"""
Blind TEST-SEARCH for record Algorithms_33__sol3.

TARGET CLAIM (quoted from the solution, line 0060-0061):
    "Therefore, each non-empty Cij is a minimal cut, and we have expressed C as a
     disjoint union of minimal cuts."

The solution's construction (Steps 1-3):
  * Given G=(V,E) and a bipartition V = S |_| T (both non-empty), let
    S1..Sp be the vertex sets of the connected components of G[S] and
    T1..Tq those of G[T].
  * Cij := { e in delta(S) : e joins a vertex of Si to a vertex of Tj }.
  * CLAIM: every non-empty Cij is a minimal cut (a bond) of G.

This file contains
  (1) a FAITHFUL implementation of the construction exactly as written,
  (2) a BRUTE-FORCE ORACLE that decides, for an arbitrary edge set F, whether F
      is a cut-set of G and whether it is a minimal cut, using the solution's
      own Definitions 1 and 2 (exhaustive over all 2^n vertex bipartitions and
      all subsets of F; pure integer/set arithmetic, no floats anywhere),
  (3) an exhaustive search over ALL labelled graphs on n <= 5 vertices crossed
      with ALL bipartitions, plus the adversarial C_{2k} constructions from the
      triage sketch, plus an exhaustive sweep of all connected graphs on 6
      vertices' cycle-rich subfamily, looking for a non-empty Cij that the
      oracle says is NOT a minimal cut.

Deterministic: no randomness at all, hence no seeds needed.
"""

from itertools import combinations, chain

# ----------------------------------------------------------------------------
# Graph helpers.  A graph is (n, edges) with vertices 0..n-1 and `edges` a
# sorted tuple of frozenset({u,v}) -- simple undirected, no loops.
# ----------------------------------------------------------------------------


def make_edges(pairs):
    return tuple(sorted((frozenset(p) for p in pairs), key=lambda f: sorted(f)))


def neighbors(n, edges, allowed=None):
    """Adjacency restricted to vertices in `allowed` (None = all)."""
    adj = {v: set() for v in range(n) if allowed is None or v in allowed}
    for e in edges:
        u, v = sorted(e)
        if allowed is None or (u in allowed and v in allowed):
            adj[u].add(v)
            adj[v].add(u)
    return adj


def components(n, edges, allowed=None):
    """Vertex sets of connected components of the induced subgraph."""
    verts = set(range(n)) if allowed is None else set(allowed)
    adj = neighbors(n, edges, verts)
    seen = set()
    comps = []
    for s in sorted(verts):
        if s in seen:
            continue
        stack = [s]
        seen.add(s)
        comp = set()
        while stack:  # BFS/DFS
            x = stack.pop()
            comp.add(x)
            for y in adj[x]:
                if y not in seen:
                    seen.add(y)
                    stack.append(y)
        comps.append(frozenset(comp))
    return comps


def delta(n, edges, X):
    """Definition 1: the cut-set of the bipartition V = X |_| (V\\X)."""
    X = set(X)
    return frozenset(e for e in edges if len(e & X) == 1)


def n_components(n, edges, removed=frozenset()):
    kept = tuple(e for e in edges if e not in removed)
    return len(components(n, kept))


# ----------------------------------------------------------------------------
# (1) FAITHFUL IMPLEMENTATION of the solution's construction.
# ----------------------------------------------------------------------------


def solution_construction(n, edges, S):
    """Return the list of non-empty C_ij together with the (Si, Tj) that
    produced them, exactly as Steps 1-2 of the solution prescribe."""
    S = frozenset(S)
    T = frozenset(range(n)) - S
    assert S and T, "Definition 1 requires S, T non-empty"

    S_comps = components(n, edges, S)   # S1..Sp   (components of G[S])
    T_comps = components(n, edges, T)   # T1..Tq   (components of G[T])

    C = delta(n, edges, S)              # C = delta(S)

    out = []
    for Si in S_comps:
        for Tj in T_comps:
            Cij = frozenset(
                e for e in C
                if len(e & Si) == 1 and len(e & Tj) == 1
            )
            if Cij:                      # "each non-empty Cij"
                out.append((Si, Tj, Cij))
    # Step 2's disjointness/union claim, checked as a sanity invariant.
    union = frozenset().union(*[c for (_, _, c) in out]) if out else frozenset()
    total = sum(len(c) for (_, _, c) in out)
    assert union == C and total == len(C), "Step 2 partition invariant broken"
    return S_comps, T_comps, C, out


# ----------------------------------------------------------------------------
# (2) BRUTE-FORCE ORACLE (exhaustive, exact set arithmetic).
# ----------------------------------------------------------------------------


def all_cutsets(n, edges):
    """Every set of edges that is delta(X) for SOME bipartition V = X |_| (V\\X)
    with X, V\\X non-empty.  This is exactly Definition 1."""
    res = set()
    for mask in range(1, (1 << n) - 1):
        X = {v for v in range(n) if (mask >> v) & 1}
        res.add(delta(n, edges, X))
    return res


def is_cutset(F, cutsets):
    return frozenset(F) in cutsets


def proper_nonempty_subsets(F):
    F = list(F)
    for k in range(1, len(F)):
        for sub in combinations(F, k):
            yield frozenset(sub)


def oracle_is_minimal_cut(n, edges, F, cutsets):
    """Definition 2 of the solution, taken literally:
       F is a minimal cut iff F is a (non-empty) cut-set and no proper
       non-empty subset of F is a cut-set for any partition of V.
    Returns (verdict, reason)."""
    F = frozenset(F)
    if not F:
        return False, "empty set is not a non-empty cut"
    if not is_cutset(F, cutsets):
        return False, "F is not a cut-set: F != delta(X) for every bipartition X"
    for sub in proper_nonempty_subsets(F):
        if is_cutset(sub, cutsets):
            return False, "proper subset %s is itself a cut-set" % (fmt_edges(sub),)
    return True, "minimal cut (bond)"


def oracle_removal_increases_components(n, edges, F):
    """The second, 'equivalently' phrasing in Definition 2: removal of F
    increases the number of connected components."""
    return n_components(n, edges, frozenset(F)) > n_components(n, edges)


# ----------------------------------------------------------------------------
# Formatting.
# ----------------------------------------------------------------------------


def fmt_edge(e):
    u, v = sorted(e)
    return "%d-%d" % (u, v)


def fmt_edges(E):
    return "{" + ", ".join(sorted(fmt_edge(e) for e in E)) + "}"


def fmt_set(X):
    return "{" + ",".join(str(v) for v in sorted(X)) + "}"


# ----------------------------------------------------------------------------
# (3) SEARCH.
# ----------------------------------------------------------------------------


def check_instance(n, edges, S):
    """Run construction + oracle.  Return list of counterexample dicts."""
    S_comps, T_comps, C, cijs = solution_construction(n, edges, S)
    cutsets = all_cutsets(n, edges)
    bad = []
    for (Si, Tj, Cij) in cijs:
        ok, reason = oracle_is_minimal_cut(n, edges, Cij, cutsets)
        if not ok:
            bad.append(dict(
                n=n, edges=edges, S=frozenset(S), Si=Si, Tj=Tj, Cij=Cij,
                reason=reason,
                is_cutset=is_cutset(Cij, cutsets),
                removal_splits=oracle_removal_increases_components(n, edges, Cij),
                S_comps=S_comps, T_comps=T_comps, C=C,
            ))
    return bad


def report(cx, title):
    n, edges, S = cx["n"], cx["edges"], cx["S"]
    T = frozenset(range(n)) - S
    print("  " + title)
    print("    V            = %s" % fmt_set(range(n)))
    print("    E            = %s" % fmt_edges(edges))
    print("    S            = %s   T = %s" % (fmt_set(S), fmt_set(T)))
    print("    comps G[S]   = %s" % " ".join(fmt_set(c) for c in cx["S_comps"]))
    print("    comps G[T]   = %s" % " ".join(fmt_set(c) for c in cx["T_comps"]))
    print("    C = delta(S) = %s" % fmt_edges(cx["C"]))
    print("    offending Cij: Si=%s Tj=%s  ->  Cij = %s"
          % (fmt_set(cx["Si"]), fmt_set(cx["Tj"]), fmt_edges(cx["Cij"])))
    print("    SOLUTION says : Cij is a minimal cut (bond) of G")
    print("    ORACLE says   : minimal cut = False  (%s)" % cx["reason"])
    print("    ORACLE detail : Cij is a cut-set at all?            %s" % cx["is_cutset"])
    print("    ORACLE detail : removing Cij increases #components? %s"
          % cx["removal_splits"])
    print("    ORACLE detail : #components(G) = %d, #components(G - Cij) = %d"
          % (n_components(n, edges), n_components(n, edges, cx["Cij"])))


def cycle(k):
    return k, make_edges([(i, (i + 1) % k) for i in range(k)])


def all_graphs(n):
    pairs = list(combinations(range(n), 2))
    m = len(pairs)
    for mask in range(1 << m):
        yield make_edges([pairs[i] for i in range(m) if (mask >> i) & 1])


def main():
    print("=" * 78)
    print("record_id : Algorithms_33__sol3")
    print("claim     : every non-empty Cij (edges between component Si of G[S]")
    print("            and component Tj of G[T]) is a MINIMAL CUT (bond) of G")
    print("=" * 78)

    # ---- A. adversarial witnesses from the triage sketch -------------------
    print("\n[A] Adversarial constructions from the triage sketch (even cycles,")
    print("    alternating bipartition):")
    first = None
    for k in (4, 6, 8):
        n, edges = cycle(k)
        S = frozenset(v for v in range(k) if v % 2 == 0)
        bad = check_instance(n, edges, S)
        status = "REFUTED (%d bad Cij of %d)" % (
            len(bad), len(solution_construction(n, edges, S)[3]))
        print("\n  C_%d, S = evens, T = odds  ->  %s" % (k, status))
        if bad:
            if first is None:
                first = bad[0]
            report(bad[0], "witness:")

    # K_{2,2} phrasing of the same graph, spelled out as in pass 0's sketch.
    print("\n  K_{2,2} phrasing (s1=0,s2=1,t1=2,t2=3; S={0,1}, T={2,3}):")
    n = 4
    edges = make_edges([(0, 2), (0, 3), (1, 2), (1, 3)])
    bad = check_instance(n, edges, {0, 1})
    print("    -> %d of %d non-empty Cij fail to be minimal cuts"
          % (len(bad), len(solution_construction(n, edges, {0, 1})[3])))
    if bad and first is None:
        first = bad[0]

    # ---- B. exhaustive sweep, all labelled graphs on n <= 5, all cuts ------
    print("\n[B] Exhaustive sweep: ALL labelled simple graphs on n vertices x")
    print("    ALL bipartitions V = S |_| T (S,T non-empty).")
    print("    %-4s %-9s %-9s %-9s %-9s" % ("n", "instances", "Cij_total",
                                            "Cij_bad", "bad_frac"))
    smallest = None
    for n in (2, 3, 4, 5):
        inst = tot = badc = 0
        for edges in all_graphs(n):
            for mask in range(1, (1 << n) - 1):
                S = frozenset(v for v in range(n) if (mask >> v) & 1)
                inst += 1
                S_comps, T_comps, C, cijs = solution_construction(n, edges, S)
                tot += len(cijs)
                b = check_instance(n, edges, S)
                badc += len(b)
                if b and smallest is None:
                    smallest = b[0]
        frac = "%d/%d" % (badc, tot) if tot else "0/0"
        print("    %-4d %-9d %-9d %-9d %-9s" % (n, inst, tot, badc, frac))

    # ---- C. exhaustive sweep restricted to CONNECTED graphs on n = 6 -------
    print("\n[C] Exhaustive sweep over all CONNECTED labelled graphs on n = 6")
    print("    with exactly 6 or 7 edges (cycle-rich), all bipartitions:")
    n = 6
    pairs = list(combinations(range(n), 2))
    inst = tot = badc = 0
    for m in (6, 7):
        for combo in combinations(range(len(pairs)), m):
            edges = make_edges([pairs[i] for i in combo])
            if n_components(n, edges) != 1:
                continue
            for mask in range(1, (1 << n) - 1):
                S = frozenset(v for v in range(n) if (mask >> v) & 1)
                inst += 1
                cijs = solution_construction(n, edges, S)[3]
                tot += len(cijs)
                badc += len(check_instance(n, edges, S))
    print("    instances=%d  Cij_total=%d  Cij_bad=%d" % (inst, tot, badc))

    # ---- verdict ----------------------------------------------------------
    cx = first if first is not None else smallest
    print("\n" + "=" * 78)
    if cx is None:
        print("VERDICT: NO_BUG_FOUND -- no non-empty Cij failed the oracle.")
    else:
        print("VERDICT: BUG_FOUND -- the quoted claim is FALSE.")
        print("Minimal failing input:")
        report(cx, "")
        print("\nWhy the proof breaks: Step 3 argues that Cij is a cut-set by")
        print("looking only at edges between Si and Tj, but Si and Tj can stay")
        print("connected THROUGH THE REST OF THE GRAPH (here around the cycle),")
        print("so deleting Cij need not disconnect anything.  Cij is not even a")
        print("cut-set, let alone a minimal one.  Line 0035's assertion")
        print("'Cij = delta(Si)' is likewise false whenever Si has cut edges to")
        print("more than one Tj.")
    print("=" * 78)


if __name__ == "__main__":
    main()
