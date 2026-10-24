#!/usr/bin/env python3
"""
Blind TEST-SEARCH for record Algorithms_28__sol5  (QEDBench / Algorithms-28).

PROBLEM: prove 12Color (does G admit a proper vertex coloring with a palette of
12 colors?) is NP-hard.

SOLUTION UNDER TEST (sol5) claims a Karp reduction from 3Color to 12Color:

  line 0007 : "Let G' be the same graph as G, i.e., G' = (V, E)."       <-- identity map
  line 0008-0010 : the 12 colors are partitioned into 4 groups of 3,
                   C_i = {c_i1, c_i2, c_i3}.
  line 0011 : "We need to show that G is 3-colorable if and only if
               G' is 12-colorable."                                     <-- TARGET CLAIM
  line 0017-0022 : backward direction: given a 12-coloring f' of G',
                   define f(v) = k when f'(v) = c_ik, and assert f is a
                   proper 3-coloring of G.                              <-- TARGET CLAIM (b)

TARGET CLAIM (CORRECTNESS), verbatim from triage:
  "The identity reduction G' = G satisfies the biconditional: G is 3-colorable
   if and only if G' is 12-colorable."

FAITHFUL IMPLEMENTATION
  * reduce_G(G)            -> returns G unchanged (exactly line 0007).
  * recover_3coloring(f')  -> the map of lines 0019-0020: colors are indexed
                              0..11, color c lies in group i = c // 3 and has
                              within-group index k = c % 3, and the solution
                              sets f(v) = k.  (Bug included as written.)

ORACLE
  * k_colorable(G, k) : exhaustive search over all k^n assignments, exact
                        integer arithmetic only, no floats anywhere.
  * is_proper(G, f)   : exact edge check.

SEARCH (correctness claim, inputs of size <= 12)
  A. Exhaustive over ALL undirected simple graphs on n = 1..5 vertices
     (2^(n choose 2) edge subsets), testing the biconditional
        3col(G)  <=>  12col(reduce_G(G)).
  B. Adversarial family from the triage sketch: K4..K12 and the Groetzsch
     graph (11 vertices, chromatic number 4).
  C. Direct refutation of the solution's backward map on K4: exhibit a proper
     12-coloring f' of K4 whose recovered f is NOT a proper 3-coloring.

VERDICT is printed deterministically (no sampling, no randomness, no timing).
"""

from itertools import combinations, product


# ----------------------------------------------------------------------------
# Graph representation: (n, frozenset of frozenset({u, v}))  -- undirected simple
# ----------------------------------------------------------------------------

def make_graph(n, edge_list):
    E = set()
    for u, v in edge_list:
        assert 0 <= u < n and 0 <= v < n and u != v
        E.add(frozenset((u, v)))
    return (n, frozenset(E))


def complete_graph(n):
    return make_graph(n, list(combinations(range(n), 2)))


def groetzsch_graph():
    """Mycielskian of C5: 11 vertices, triangle-free, chromatic number 4."""
    # C5 on 0..4 ; shadow vertices 5..9 (shadow of i is i+5) ; apex 10.
    edges = []
    for i in range(5):
        edges.append((i, (i + 1) % 5))
    for i in range(5):
        for j in [(i + 1) % 5, (i - 1) % 5]:
            e = (i + 5, j)
            if e not in edges and (e[1], e[0]) not in edges:
                edges.append(e)
    for i in range(5):
        edges.append((10, i + 5))
    return make_graph(11, edges)


def all_graphs_on(n):
    """Every simple undirected graph on n labelled vertices."""
    pairs = list(combinations(range(n), 2))
    for mask in range(1 << len(pairs)):
        el = [pairs[i] for i in range(len(pairs)) if (mask >> i) & 1]
        yield make_graph(n, el)


# ----------------------------------------------------------------------------
# FAITHFUL IMPLEMENTATION OF THE SOLUTION'S REDUCTION (bugs included)
# ----------------------------------------------------------------------------

def reduce_G(G):
    """Line 0007: 'Let G' be the same graph as G, i.e., G' = (V, E).'

    The solution performs NO modification to the graph whatsoever
    (lines 0023-0026 restate this: 'it involves no modification to the graph
    itself').  So the reduction is the identity map."""
    return G


def forward_map(f3):
    """Line 0015: f'(v) = c_{1, f(v)}.  Colors are numbered 0..11 with
    c_{i k}  ->  3 * (i - 1) + (k - 1).  Group 1 is colors {0, 1, 2}."""
    return [3 * 0 + k for k in f3]


def recover_3coloring(f12):
    """Lines 0018-0020: 'if f'(v) in C_i for some i, then set f(v) to be the
    index of the color within C_i (i.e., if f'(v) = c_ik, then f(v) = k).'

    Color number c in 0..11 sits in group i = c // 3 with within-group index
    k = c % 3, so the solution's recovered color is k = c % 3."""
    return [c % 3 for c in f12]


# ----------------------------------------------------------------------------
# BRUTE-FORCE ORACLE (exact; integers only)
# ----------------------------------------------------------------------------

def is_proper(G, coloring):
    n, E = G
    assert len(coloring) == n
    for e in E:
        u, v = tuple(e)
        if coloring[u] == coloring[v]:
            return False
    return True


def k_colorable_naive(G, k):
    """Literally exhaustive over all k^n assignments. Exact, no floats.
    Only usable for tiny k^n; used as a cross-check on the pruned oracle."""
    n, E = G
    if n == 0:
        return True, []
    for assign in product(range(k), repeat=n):
        if is_proper(G, list(assign)):
            return True, list(assign)
    return False, None


def k_colorable(G, k):
    """Complete (exhaustive-with-pruning) backtracking search over the same
    k^n assignment space, in lexicographic order, so it returns the SAME
    answer and the SAME lexicographically-first witness as k_colorable_naive.
    Exact integer arithmetic only. Returns (bool, witness or None)."""
    n, E = G
    adj = [set() for _ in range(n)]
    for e in E:
        u, v = tuple(e)
        adj[u].add(v)
        adj[v].add(u)
    col = [-1] * n

    def rec(v):
        if v == n:
            return True
        for c in range(k):
            if all(col[u] != c for u in adj[v] if u < v):
                col[v] = c
                if rec(v + 1):
                    return True
                col[v] = -1
        return False

    if n == 0:
        return True, []
    if rec(0):
        w = list(col)
        assert is_proper(G, w)
        return True, w
    return False, None


def find_12coloring_breaking_recovery(G):
    """Find a proper 12-coloring f' of G whose recovered f = f' mod 3 is NOT a
    proper 3-coloring of G.  Exhaustive; returns (f', f) or None."""
    n, E = G
    for assign in product(range(12), repeat=n):
        a = list(assign)
        if is_proper(G, a):
            rec = recover_3coloring(a)
            if not is_proper(G, rec):
                return a, rec
    return None


def cname(c):
    return "c%d%d" % (c // 3 + 1, c % 3 + 1)


# ----------------------------------------------------------------------------
# SEARCH
# ----------------------------------------------------------------------------

def check_biconditional(G):
    """Return None if the claimed iff holds on G, else a dict describing the
    counterexample."""
    Gp = reduce_G(G)
    lhs, w3 = k_colorable(G, 3)
    rhs, w12 = k_colorable(Gp, 12)
    if lhs != rhs:
        return {"n": G[0],
                "edges": sorted(tuple(sorted(e)) for e in G[1]),
                "3colorable": lhs,
                "12colorable_of_reduced": rhs,
                "witness12": w12}
    return None


def main():
    print("=" * 78)
    print("TEST-SEARCH  record_id = Algorithms_28__sol5")
    print("claim_kind = CORRECTNESS")
    print("target claim: identity reduction G' = G satisfies")
    print("              'G is 3-colorable  <=>  G' is 12-colorable'  (line 0011)")
    print("=" * 78)

    first_cex = None

    # ---- 0. oracle cross-check: pruned search vs literal k^n enumeration ----
    print()
    print("[0] ORACLE CROSS-CHECK: pruned backtracking vs literal k^n enumeration")
    xchecks = 0
    xok = True
    for n in range(1, 5):
        for G in all_graphs_on(n):
            for k in (2, 3, 4):
                a = k_colorable(G, k)
                b = k_colorable_naive(G, k)
                xchecks += 1
                if a != b:
                    xok = False
    for n in range(1, 4):
        for G in all_graphs_on(n):
            a = k_colorable(G, 12)
            b = k_colorable_naive(G, 12)
            xchecks += 1
            if a != b:
                xok = False
    print("    %d (graph, k) pairs compared; identical answers AND witnesses: %s"
          % (xchecks, xok))

    # ---- A. exhaustive over all graphs on n = 1..5 --------------------------
    print()
    print("[A] EXHAUSTIVE over all simple undirected graphs on n = 1..5 vertices")
    for n in range(1, 6):
        total = 0
        bad = 0
        firstbad_n = None
        for G in all_graphs_on(n):
            total += 1
            cex = check_biconditional(G)
            if cex is not None:
                bad += 1
                if firstbad_n is None:
                    firstbad_n = cex
                if first_cex is None:
                    first_cex = cex
        print("    n=%d : %5d graphs tested, %5d violate the claimed iff" % (n, total, bad))
        if firstbad_n is not None:
            print("           first violating graph: V=%d  E=%s" %
                  (firstbad_n["n"], firstbad_n["edges"]))
            print("           3-colorable(G) = %s   12-colorable(G'=G) = %s"
                  % (firstbad_n["3colorable"], firstbad_n["12colorable_of_reduced"]))

    # ---- B. adversarial family from the triage sketch ----------------------
    print()
    print("[B] ADVERSARIAL family: K4..K12 and the Groetzsch graph (chi = 4)")
    fam = [("K%d" % n, complete_graph(n)) for n in range(4, 13)]
    fam.append(("Groetzsch(11v)", groetzsch_graph()))
    for name, G in fam:
        n, E = G
        lhs, _ = k_colorable(G, 3)
        rhs, w12 = k_colorable(reduce_G(G), 12)
        verdict = "IFF HOLDS" if lhs == rhs else "IFF VIOLATED"
        print("    %-15s V=%2d E=%3d | 3-colorable=%-5s | 12-colorable(G')=%-5s | %s"
              % (name, n, len(E), lhs, rhs, verdict))
        if lhs != rhs and first_cex is None:
            first_cex = {"n": n, "edges": sorted(tuple(sorted(e)) for e in E),
                         "3colorable": lhs, "12colorable_of_reduced": rhs,
                         "witness12": w12}

    # ---- C. the solution's own backward map, refuted directly ---------------
    print()
    print("[C] The solution's backward color-recovery map (lines 0018-0020),")
    print("    f(v) = k  when  f'(v) = c_ik, applied on K4:")
    K4 = complete_graph(4)
    hit = find_12coloring_breaking_recovery(K4)
    if hit is None:
        print("    no counterexample found (map survives on K4)")
    else:
        f12, f3 = hit
        print("    proper 12-coloring f' of K4 : %s" % [cname(c) for c in f12])
        print("      (is_proper under 12 colors  = %s)" % is_proper(K4, f12))
        print("    recovered f(v) = k           : %s" % [k + 1 for k in f3])
        print("      (is_proper as a 3-coloring = %s)  <-- adjacent vertices share a color"
              % is_proper(K4, f3))

    # ---- forward direction sanity (the part of the proof that IS true) ------
    print()
    print("[D] Sanity: the FORWARD direction (line 0012-0016) is sound.")
    fwd_ok = True
    for n in range(1, 6):
        for G in all_graphs_on(n):
            ok3, w3 = k_colorable(G, 3)
            if ok3:
                if not is_proper(reduce_G(G), forward_map(w3)):
                    fwd_ok = False
    print("    every 3-coloring maps to a proper 12-coloring of G' : %s" % fwd_ok)

    # ---- verdict ------------------------------------------------------------
    print()
    print("=" * 78)
    if first_cex is not None:
        print("VERDICT: BUG_FOUND")
        print("  Smallest counterexample to the biconditional on line 0011:")
        print("    G : V = %d, E = %s" % (first_cex["n"], first_cex["edges"]))
        print("    brute-force oracle: G is 3-colorable          = %s"
              % first_cex["3colorable"])
        print("    brute-force oracle: G' = G is 12-colorable    = %s"
              % first_cex["12colorable_of_reduced"])
        print("    witness 12-coloring of G' : %s"
              % [cname(c) for c in first_cex["witness12"]])
        print("  The '<=' direction of the claimed equivalence therefore fails:")
        print("  G' is 12-colorable but G is not 3-colorable, so the identity")
        print("  reduction does not map 3Color to 12Color and establishes nothing")
        print("  about NP-hardness of 12Color.")
    else:
        print("VERDICT: NO_BUG_FOUND")
    print("=" * 78)


if __name__ == "__main__":
    main()
