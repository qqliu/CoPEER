#!/usr/bin/env python3
"""
Blind TEST-SEARCH for record Algorithms_10__sol5   (CORRECTNESS claim)

PROBLEM (Algorithms_10)
-----------------------
G = (V,E), |V| = n.  There is a constant alpha > 0 such that for EVERY S subset V
with |S| = n/2:
        |N(S)| >= n/2 + alpha*n,          N(S) = { w : exists v in S, (v,w) in E }.
Given any k >= 1 and any W_1,...,W_k subset V with |W_i| >= (1-alpha)n, show there
is a walk (v_1,...,v_k) in G with v_i in W_i and (v_i,v_{i+1}) in E.

TARGET CLAIM (solution 5, lines 0007-0022)
------------------------------------------
    "Let P = (v1,...,vm) ... Let S = {vm}, so |S| = 1 <= n/2 ... By the given
     condition on G, the neighborhood N(S) satisfies |N(S)| >= n/2 + alpha*n."
    ... "Thus, N(S) cap W_{m+1} is non-empty ... and we can choose
     v_{m+1} in N(S) cap W_{m+1}."

So the solution's algorithm is a *singleton* greedy: keep only the last vertex
v_m, and extend using N({v_m}) cap W_{m+1}, justified by applying the expansion
hypothesis (which is stated ONLY for |S| = n/2) to the singleton |S| = 1.

WHAT THIS FILE DOES
-------------------
1. FAITHFUL IMPLEMENTATION of the solution's algorithm, bugs included
   (`solution_greedy`): pick v_1 in W_1, then v_{m+1} in N({v_m}) cap W_{m+1}.
   The write-up never says *which* vertex to pick ("we can choose"), so the
   implementation uses the only canonical deterministic rule: smallest index.
   Where the proof asserts non-emptiness, the code reports FAILURE if empty.
2. BRUTE-FORCE ORACLE (`oracle_walk_exists`): exhaustive product over
   W_1 x ... x W_k, checking every consecutive pair is an edge.  Exact, no
   floats anywhere; alpha is a Fraction and every hypothesis test is integer
   arithmetic (2*|N(S)| >= n + 2*alpha*n rewritten over Fractions).
3. SEARCH: (a) the two adversarial constructions from the triage sketch;
   (b) an EXHAUSTIVE search over ALL graphs on n = 6 vertices (2^15 = 32768)
   that satisfy the expansion hypothesis for some alpha > 0, together with all
   admissible W_1, W_2 (and a k = 3 pass), looking for an input where the
   solution's algorithm fails while the oracle says a walk exists.
4. Robustness: re-checks the headline counterexample under the closed-
   neighbourhood reading N[S] = S u N(S), so the refutation does not hinge on
   which convention the author meant.

Deterministic: no randomness, no sampling, no timing.
"""

from fractions import Fraction
from itertools import combinations, product
import sys


# ----------------------------------------------------------------------------
# Graph helpers (undirected, vertices 0..n-1, adjacency as frozensets)
# ----------------------------------------------------------------------------

def make_graph(n, edges):
    adj = [set() for _ in range(n)]
    for (u, v) in edges:
        assert u != v, "no self loops"
        adj[u].add(v)
        adj[v].add(u)
    return [frozenset(s) for s in adj]


def neighbourhood(adj, S):
    """Open neighbourhood N(S) = { w : exists v in S, (v,w) in E }."""
    out = set()
    for v in S:
        out |= adj[v]
    return out


def closed_neighbourhood(adj, S):
    return set(S) | neighbourhood(adj, S)


# ----------------------------------------------------------------------------
# Hypothesis checking (exact integer / Fraction arithmetic only)
# ----------------------------------------------------------------------------

def expansion_holds(adj, n, alpha, nbhd=neighbourhood):
    """True iff every S with |S| = n/2 has |N(S)| >= n/2 + alpha*n.

    Requires n even (the hypothesis literally speaks of |S| = n/2).
    Comparison is exact: |N(S)| and n/2 + alpha*n are Fractions.
    """
    assert n % 2 == 0, "hypothesis is stated for |S| = n/2; use even n"
    half = n // 2
    thr = Fraction(n, 2) + Fraction(alpha) * n
    worst = None
    for S in combinations(range(n), half):
        sz = len(nbhd(adj, S))
        if worst is None or sz < worst:
            worst = sz
        if Fraction(sz) < thr:
            return False, S, sz, thr
    return True, None, worst, thr


def max_alpha(adj, n, nbhd=neighbourhood):
    """Largest alpha for which the hypothesis holds: (min_{|S|=n/2}|N(S)| - n/2)/n."""
    half = n // 2
    worst = min(len(nbhd(adj, S)) for S in combinations(range(n), half))
    return Fraction(worst, 1) / n - Fraction(1, 2), worst


def W_sizes_ok(n, alpha, Ws):
    """Every |W_i| >= (1-alpha)n, exactly."""
    need = (1 - Fraction(alpha)) * n
    return all(Fraction(len(W)) >= need for W in Ws), need


# ----------------------------------------------------------------------------
# 1. FAITHFUL IMPLEMENTATION of solution 5's algorithm (bugs included)
# ----------------------------------------------------------------------------

def solution_greedy(adj, n, Ws, nbhd=neighbourhood):
    """Exactly the construction of lines 0003-0022.

    Base case (k=1): W_1 is non-empty, take a vertex of it  -> smallest index.
    Inductive step: S = {v_m}; the proof asserts |N(S)| >= n/2 + alpha*n and
    hence N(S) cap W_{m+1} != empty; take a vertex of it -> smallest index.

    Returns (walk, None) on success, or (None, reason) when the step the proof
    declared impossible actually happens.
    """
    k = len(Ws)
    if not Ws[0]:
        return None, "W_1 empty"
    v = min(Ws[0])                      # "any single vertex forms a path"
    walk = [v]
    for m in range(1, k):
        S = {walk[-1]}                  # <-- the bug: singleton S
        cand = nbhd(adj, S) & set(Ws[m])
        if not cand:
            return None, ("STUCK at step %d: N({%d}) = %s, W_%d = %s, "
                          "intersection empty"
                          % (m + 1, walk[-1], sorted(nbhd(adj, S)),
                             m + 1, sorted(Ws[m])))
        walk.append(min(cand))
    return walk, None


# ----------------------------------------------------------------------------
# 2. BRUTE-FORCE ORACLE
# ----------------------------------------------------------------------------

def oracle_walk_exists(adj, Ws):
    """Exhaustive: is there (v_1..v_k), v_i in W_i, (v_i,v_{i+1}) in E?"""
    for cand in product(*[sorted(W) for W in Ws]):
        if all(cand[i + 1] in adj[cand[i]] for i in range(len(cand) - 1)):
            return list(cand)
    return None


# ----------------------------------------------------------------------------
# reporting helper
# ----------------------------------------------------------------------------

def report_case(title, n, adj, alpha, Ws, nbhd=neighbourhood):
    print(title)
    print("  n = %d, alpha = %s, n/2 + alpha*n = %s"
          % (n, alpha, Fraction(n, 2) + Fraction(alpha) * n))
    print("  adjacency: " + ", ".join("N(%d)=%s" % (v, sorted(adj[v]))
                                      for v in range(n)))
    ok, badS, worst, thr = expansion_holds(adj, n, alpha, nbhd)
    print("  hypothesis (every |S|=n/2 has |N(S)| >= %s): %s  [min over all "
          "%d subsets = %d]" % (thr, "HOLDS" if ok else "FAILS (%s)" % (badS,),
                                len(list(combinations(range(n), n // 2))), worst))
    szok, need = W_sizes_ok(n, alpha, Ws)
    for i, W in enumerate(Ws):
        print("  W_%d = %s   |W_%d| = %d  (need >= (1-alpha)n = %s)"
              % (i + 1, sorted(W), i + 1, len(W), need))
    print("  W-size condition: %s" % ("OK" if szok else "VIOLATED"))
    walk, reason = solution_greedy(adj, n, Ws, nbhd)
    if walk is None:
        print("  SOLUTION ALGORITHM  -> FAILS: %s" % reason)
    else:
        print("  SOLUTION ALGORITHM  -> %s" % walk)
    ow = oracle_walk_exists(adj, Ws)
    print("  BRUTE-FORCE ORACLE  -> %s"
          % ("walk exists: %s" % ow if ow else "no walk exists"))
    return ok and szok, walk, ow


# ----------------------------------------------------------------------------
# main
# ----------------------------------------------------------------------------

def main():
    print("=" * 78)
    print("TEST-SEARCH  Algorithms_10__sol5   claim_kind = CORRECTNESS")
    print("Target: the singleton-expansion step  |N({v_m})| >= n/2 + alpha*n,")
    print("        hence N({v_m}) cap W_{m+1} != empty  (lines 0007-0022)")
    print("=" * 78)

    verdicts = []

    # ---------------------------------------------------------------- part A
    print("\n--- PART A: is the quoted inequality itself true? "
          "(direct check on a legal instance) ---")
    # K5 on {1,2,3,4,5} plus pendant vertex 0 attached only to 1.
    n = 6
    edges = [(u, v) for u, v in combinations([1, 2, 3, 4, 5], 2)] + [(0, 1)]
    adj = make_graph(n, edges)
    amax, worst = max_alpha(adj, n)
    print("  graph: K5 on {1..5} + pendant vertex 0 adjacent only to 1")
    print("  min_{|S|=3} |N(S)| = %d  ==>  hypothesis holds for every "
          "0 < alpha <= %s" % (worst, amax))
    alpha = amax                                   # = 1/3
    thr = Fraction(n, 2) + alpha * n
    print("  take alpha = %s, so the solution claims |N({v})| >= %s for every v"
          % (alpha, thr))
    bad = [v for v in range(n) if Fraction(len(adj[v])) < thr]
    for v in bad:
        print("    vertex %d: |N({%d})| = %d  <  %s   *** quoted inequality "
              "FALSE ***" % (v, v, len(adj[v]), thr))
    claim_false = len(bad) > 0

    # ---------------------------------------------------------------- part B
    print("\n--- PART B: adversarial constructions from the triage sketch ---")
    # sketch p0 (relabelled so the pendant is the smallest index, making the
    # 'choose any' base-case pick deterministic in the natural min-index rule)
    W1 = {0, 2, 3, 4}
    W2 = {2, 3, 4, 5}
    legal_b1, walk_b1, oracle_b1 = report_case(
        "\n [B1] pendant-endpoint trap, k = 2", n, adj, alpha, [W1, W2])
    b1_is_ce = legal_b1 and walk_b1 is None and oracle_b1 is not None

    # sketch p1 variant: alpha = 1/6, both W's of size 5 excluding the hub
    print()
    alpha2 = Fraction(1, 6)
    W1b = {0, 2, 3, 4, 5}
    W2b = {0, 2, 3, 4, 5}
    legal_b2, walk_b2, oracle_b2 = report_case(
        " [B2] hub-excluded trap, k = 2, alpha = 1/6", n, adj, alpha2,
        [W1b, W2b])
    b2_is_ce = legal_b2 and walk_b2 is None and oracle_b2 is not None
    if legal_b2 and walk_b2 is None and oracle_b2 is None:
        print("  (note: oracle agrees no walk exists here, so B2 refutes the "
              "quoted inequality but is not an input/output counterexample)")

    # ---------------------------------------------------------------- part C
    print("\n--- PART C: EXHAUSTIVE search, all graphs on n = 6 ---")
    print("  For every one of the 2^15 = 32768 labelled graphs on 6 vertices:")
    print("    * compute alpha_max = min_{|S|=3}|N(S)|/n - 1/2; keep graphs "
          "with alpha_max > 0")
    print("    * take alpha = alpha_max (the hypothesis holds for it)")
    print("    * enumerate every W_1, W_2 with |W_i| >= (1-alpha)n")
    print("    * compare solution_greedy against the brute-force oracle")
    n = 6
    pairs = list(combinations(range(n), 2))
    all_subsets = []
    for size in range(n + 1):
        for c in combinations(range(n), size):
            all_subsets.append(frozenset(c))

    graphs_tested = 0
    graphs_with_hypothesis = 0
    instances_tested = 0
    counterexamples = []
    for mask in range(1 << len(pairs)):
        edges = [pairs[i] for i in range(len(pairs)) if mask >> i & 1]
        adjg = make_graph(n, edges)
        graphs_tested += 1
        a, worst = max_alpha(adjg, n)
        if a <= 0:
            continue
        graphs_with_hypothesis += 1
        need = (1 - a) * n
        good_W = [W for W in all_subsets if Fraction(len(W)) >= need and W]
        for W1x in good_W:
            for W2x in good_W:
                instances_tested += 1
                walk, reason = solution_greedy(adjg, n, [W1x, W2x])
                ow = oracle_walk_exists(adjg, [W1x, W2x])
                if walk is None and ow is not None:
                    counterexamples.append(
                        (mask, edges, a, sorted(W1x), sorted(W2x), reason, ow))
                elif walk is not None:
                    assert all(walk[i + 1] in adjg[walk[i]]
                               for i in range(len(walk) - 1))
    print("  graphs enumerated ............ %d" % graphs_tested)
    print("  graphs satisfying hypothesis . %d" % graphs_with_hypothesis)
    print("  (graph, W1, W2) instances .... %d" % instances_tested)
    print("  counterexamples (algorithm fails, oracle finds a walk): %d"
          % len(counterexamples))

    minimal = None
    if counterexamples:
        # smallest edge count, then lexicographically smallest, for determinism
        minimal = min(counterexamples, key=lambda t: (len(t[1]), t[1], t[3], t[4]))
        print("\n  smallest such counterexample found by exhaustive search:")
        mask, edges, a, W1x, W2x, reason, ow = minimal
        print("    edges  = %s" % (edges,))
        print("    alpha  = %s   ((1-alpha)n = %s)" % (a, (1 - a) * n))
        print("    W1 = %s   W2 = %s" % (W1x, W2x))
        print("    solution algorithm: FAILS -- %s" % reason)
        print("    oracle            : walk exists %s" % ow)

    # k = 3 pass on the headline graph, to show the failure is not a k=2 artefact
    print("\n  k = 3 pass on the pendant graph (alpha = 1/3):")
    adj = make_graph(6, [(u, v) for u, v in combinations([1, 2, 3, 4, 5], 2)]
                     + [(0, 1)])
    W = [{0, 2, 3, 4}, {2, 3, 4, 5}, {2, 3, 4, 5}]
    walk3, reason3 = solution_greedy(adj, 6, W)
    ow3 = oracle_walk_exists(adj, W)
    print("    W = %s" % [sorted(x) for x in W])
    print("    solution algorithm: %s" % (walk3 if walk3 else "FAILS -- " + reason3))
    print("    oracle            : %s" % (ow3 if ow3 else "no walk"))

    # ---------------------------------------------------------------- part D
    print("\n--- PART D: robustness under the closed-neighbourhood reading "
          "N[S] = S u N(S) ---")
    ok_c, badS, worst_c, thr_c = expansion_holds(adj, 6, Fraction(1, 3),
                                                 closed_neighbourhood)
    print("  hypothesis with N[.]: %s (min_{|S|=3}|N[S]| = %d, threshold %s)"
          % ("HOLDS" if ok_c else "FAILS", worst_c, thr_c))
    print("  |N[{0}]| = %d < %s, and N[{0}] cap W2 = %s"
          % (len(closed_neighbourhood(adj, {0})), thr_c,
             sorted(closed_neighbourhood(adj, {0}) & {2, 3, 4, 5})))
    print("  => the refutation does not depend on the open/closed convention.")

    # ---------------------------------------------------------------- verdict
    print("\n" + "=" * 78)
    if claim_false and (b1_is_ce or counterexamples):
        print("VERDICT: BUG_FOUND")
        print("The quoted step is false and the algorithm it defines is "
              "incorrect.")
        print("Failing input (n = 6 <= 12, hypothesis verified exhaustively "
              "over all 20 subsets of size n/2 = 3):")
        print("  V = {0,1,2,3,4,5}; E = K5 on {1,2,3,4,5} plus the single edge "
              "(0,1)")
        print("  alpha = 1/3  (min_{|S|=3}|N(S)| = 5 = n/2 + alpha*n, so the "
              "expansion hypothesis holds)")
        print("  k = 2, W1 = {0,2,3,4}, W2 = {2,3,4,5}; |W1| = |W2| = 4 = "
              "(1-alpha)n, so both are admissible")
        print("Observed: the solution's step takes S = {v_1} = {0} and asserts "
              "|N(S)| >= n/2 + alpha*n = 5;")
        print("          in fact |N({0})| = 1, and N({0}) cap W2 = {} so the "
              "construction produces NO v_2.")
        print("Claimed : the construction always extends, so it outputs a walk "
              "(v_1,v_2) with v_i in W_i.")
        print("Oracle  : a valid walk does exist, e.g. (2,3) -- so the failure "
              "is the algorithm's, not the instance's.")
        print("The correct proof must carry the whole reachable set "
              "R_i = W_i cap N(R_{i-1}) (|R_i| >= n/2) and apply expansion to "
              "an n/2-subset of it; the singleton S = {v_m} is outside the "
              "hypothesis.")
    elif claim_false:
        print("VERDICT: BUG_FOUND (quoted inequality refuted; see PART A/B)")
    else:
        print("VERDICT: NO_BUG_FOUND")
    print("=" * 78)
    return 0


if __name__ == "__main__":
    sys.exit(main())
